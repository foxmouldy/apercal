import lib
import logging
import pylab as pl
import os
import sys

####################################################################################################

class source:
    '''
    Contains the paths and filenames for source. 
    pathtodata = Directory in which the raw data (MS or UVFITS) reside.
    path = Directory in which the data (UV) reside, and in which the images and processing will
        happen.
    ms = Name of the measurement set
    uvf = Name of the uvfits file. If this is not provided, then a name will be derived from the ms.
    uv = Name of the MIRIAD uv file. If this is not provided, then a name will be derived from the
        ms.
    '''
    def __init__(self, pathtodata='',  path='', ms=None, uvf=None, vis=None, output=None):
        self.pathtodata = pathtodata
        self.ms = ms
        if uvf is None and ms is not None:
            self.uvf = str(self.ms).upper().replace('.MS', 'UVF')
        else:
            self.uvf = uvf
        if vis is None and ms is not None:
            self.vis = str(self.ms).upper().replace('.MS', 'UV')
        else:
            self.vis = vis
        if path is '':
            self.path = pathtodata
        else:    
            self.path = path
        if output is None:
            self.output = 'output'
        else:    
            self.output = output    
    
    def update(self):
        if self.path is '' and self.pathtodata is not '':
            self.path = self.pathtodata
        if self.path is not '' and self.pathtodata is '':
            self.pathtodata = self.path

####################################################################################################

class wselfcal:
    '''
    selfcal: WSRT SelfCal
    Object that does conventional SelfCal using a process that's been well tested for WSRT data.
    '''
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.logger = logging.getLogger('selfcal')
        # Initial Attributes: Constant - Things that you want to change

        self.source = source()
        self.path = self.source.path
        self.output = self.source.output
        self.vis = self.source.vis

        self.num_major = 5 
        self.num_minor = 3
        self.linear = True # Can be linear or log. If log, then the entries are exponents.
        self.cmin = 3
        self.cmax = 2
        self.d = 10.
        self.nsigma = 7 
        self.immax = 0.0
        # Setting an advanced setting.

        # Initial Attributes: Constant - Things that you DON'T want to change
        self.image = 'image'
        self.model = 'model'
        self.mask = 'mask'
        self.residual = 'residual'
        self.map = 'map'
        self.beam = 'beam'
        self.rmgains = True # Remove gains from vis file.

        ## MIRIAD Task Interfaces - Things that you SHOULD NOT change.
        self.invert = invert
        self.invert.map = self.map
        self.invert.beam = self.beam
        #self.invert.vis = self.vis 

        ## Advanced Attributes - More things that you SHOULD NOT change
        self.clean = clean
        self.clean.out = self.model
        self.clean.beam =  self.beam
        self.clean.map =  self.map
        self.clean.region = 'mask('+self.mask+')'

        self.obsrms = obsrms

        self.selfcal = selfcal
        self.selfcal.model = self.model

        self.maths = maths
        self.maths.out = self.mask

        self.restor = restor
        self.restor.out = self.image
        self.restor.model = self.model
        self.restor.map = self.map
        self.restor.beam = self.beam
        self.restor.mode = 'clean'

        self.imstat = imstat
        self.imstat.in_ = self.map

    def __getitem__(self, key):
        return getattr(self, key)

    def help(self):
        logger.info("Print some help!")

    def setup(self):
        '''
        setup moves to the output directory specified, makes a symbolic link to the visibility file
        that you're working on.
        '''
        # Initial Attributes: Constant - Things that you DON'T want to change
        # First, check that the path exists, and complain if it doesn't.
        # If a source has been provided but the path has not been set.


        if not os.path.exists(self.path):
            self.logger.critical("Path not found. Please fix and start again.")
            sys.exit(0)
        
        # Now make the output path
        try:
            os.chdir(self.path+'/'+self.output)
        except:
            self.logger.warn("Cannot find "+self.path+'/'+self.output+", making it ")
            os.mkdir(self.path+'/'+self.output)
            os.chdir(self.path+'/'+self.output)
            
        self.logger.warn('You have now moved into '+self.path+'/'+self.output)
        self.logger.warn('All outputs will be relative to this path.')

        self.logger.info("Making symbolic/soft link to your visibility file")
        lib.basher("ln -s "+self.path+'/'+self.vis)
        self.selfcal.vis = self.vis
        self.invert.vis = self.vis
        # Advanced Attributes
        # This is an extra level of protection against not having enough cutoffs.
        if self.linear:
            self.mask_cutoffs = pl.linspace(float(self.cmin), float(self.cmax), self.num_minor)
        else:
            self.mask_cutoffs = pl.logspace(float(pl.log10(self.cmin)), float(pl.log10(self.cmax)), self.num_minor)
        self.clean_cutoffs = self.mask_cutoffs*self.d
        self.path0 = os.getcwd()
        self.trms = self.nsigma*float(self.obsrms.go()[-1].split()[3])/1000. # OBSRMS will return values in mJy/beam

    def go(self):
        '''
        Runs the selfcal loop niters times
        '''
        logger = self.logger
        logger.info('Starting SelfCal')
        self.setup()
        if len(self.mask_cutoffs)<self.num_minor or len(self.clean_cutoffs)<self.num_minor:
            logger.critical("Insufficient mask and clean cutoffs provided!")
            logger.critical("Number of cutoffs = num_minor")
            logger.critical("Please adjust and try again.")
            sys.exit(0)
        if self.rmgains:
            lib.basher('rm -r '+self.vis+'/gains')
            logger.info("Removing previous gains.")
        logger.info("Doing selfcal with "+str(self.num_major)+" major cycles.")

        self.deep_image()
        for i in range(0,int(self.num_major)):
            logger.info("Major Cycle = "+str(i+1))
            self.selfcal.go()
            self.deep_image()
            self.mask_cutoffs = self.mask_cutoffs*(i+2)
            self.clean_cutoffs = self.mask_cutoffs*self.d
        logger.info('SelfCal Completed.')    
        
    def deep_image(self):
        '''
        Module to do deep imaging. The names of the output are derived from self. 
        If the user wants to do a one-off invert or clean, then they do it with their own names
        and at their own risk.
        '''
        logger = logging.getLogger('deep_image')
        logger.info("Mask threshold: IMAX"+str(self.mask_cutoffs[0]))
        self.invert.go(rmfiles=True)
        self.imstat.in_ = self.invert.map
        immax = float(self.imstat.go()[-1].split()[3])
        self.maths.mask = self.invert.map+".gt.{:2.2}".format(max(immax/self.mask_cutoffs[0], self.trms))
        self.maths.go(rmfiles=True)
        for j in range(0,int(self.num_minor)):
            logger.info('Starting /minor-cycle = '+str(1+j))
            if j>0:
                self.imstat.in_ = self.image
                self.immax = float(self.imstat.go()[-1].split()[3])
                self.maths.mask = self.image+".gt.{:2.2}".format(max(immax/self.mask_cutoffs[j], self.trms))
                self.maths.go(rmfiles=True)
            self.clean.cutoff = "{:2.2}".format(max(immax/self.clean_cutoffs[j], self.trms))
            self.clean.go(rmfiles=True)
            self.restor.mode = 'clean'
            self.restor.out = self.image 
            self.restor.go(rmfiles=True)
            self.restor.mode = 'residual'
            self.restor.out = self.residual
            self.restor.go(rmfiles=True)
            logger.info('Completed /minor-cycle = '+str(1+j))

####################################################################################################

class crosscal:
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('crosscal')
        self.__dict__.update(kwargs)

        # Place MIRIAD interfaces here
        self.wsrtfits = wsrtfits 
        self.attsys = attsys
        self.uvflag = uvflag
        self.pgflag = pgflag
        self.mfcal = mfcal
        self.puthd = puthd
        self.uvcal = uvcal
        # source can be a source object, or a list of source objects
        self.source = source

    def __getitem__(self, key):
        return getattr(self, key)

    def setup(self):
        '''
        '''
        # Now make the output path
        if type(self.source) is list:
            logger.info('Setting path to first source')
            sourc = self.source[0]
            self.path = sourc.path
            self.output = sourc.output
            self.vis = sourc.vis
        else:
            self.path = self.source.path
            self.output = self.source.output
            self.vis = self.source.vis

        try:
            os.chdir(self.path)
        except:
            self.logger.warn("Cannot find "+self.path+", making it ")
            os.mkdir(self.path)
            os.chdir(self.path)
            
        self.logger.warn('You have now moved into '+self.path)
        self.logger.warn('All outputs will be relative to this path.')

    def help(self):
        logger.info("Print some help!")
    
    def uvflagger(self):
        '''
        If you want to flag multiple selections for multiple files.
        vis is either a list of source objects, or a single source object.
        '''
        path0 = os.getcwd()
        if type(self.sourc) is list: 
            for sourc in self.source:
                try:
                    os.chdir(sourc.path)
                except:
                    logger.critical(sourc.path+" does not exist! Please check your sources to continue.")
                    sys.exit(0)
                self.uvflag.vis = sourc.vis
                if type(self.uvflag.select) is list: 
                    for select in self.uvflag.select:
                        self.uvflag.select = select
                        self.uvflag.go()
                else:
                    self.go()
        else:
                sourc = self.source
                try:
                    os.chdir(sourc.path)
                except:
                    logger.critical(sourc.path+" does not exist! Please check your sources to continue.")
                    sys.exit(0)
                self.uvflag.vis = sourc.vis
                if type(self.uvflag.select) is list: 
                    for select in self.uvflag.select:
                        self.uvflag.select = select
                        self.uvflag.go()
                else:
                    self.go()
        os.chdir(path0)       

    def pgflagger(self):
        '''
        wrapper around the pgflag task, if you want to flag multiple visibilities.
        '''
        path0 = os.getcwd()
        if type(self.source) is list:
            for sourc in self.source:
                try:
                    os.chdir(sourc.path)
                except:
                    logger.critical(sourc.path+" does not exist! Please check your sources to continue.")
                    sys.exit(0)
            self.pgflag.vis = sourc.vis
            self.pgflag.go()
        else:
            sourc = self.source
            try:
                os.chdir(sourc.path)
            except:
                logger.critical(sourc.path+" does not exist! Please check your sources to continue.")
                sys.exit(0)
            self.pgflag.vis = sourc.vis
            self.pgflag.go()

    def ms2uvfits(self):
        '''
        wrapper around ms2uvfits
        '''
        path0 = os.getcwd()
        if self.source.ms is None:
            self.logger.critical("MS not provided. Please check source.")
            sys.exit(0)
        try:
            os.chdir(self.source.pathtodata)
        except:
            # Error message 
            logger.critical("Path does not exist!")
            logger.critical("Error with MS provided.")
            sys.exit(0)
        lib.ms2uvfits(ms=self.source.ms, uvf=self.source.uvf)
        os.chdir(path0)    
        
    def importloop(self, sourc):
        '''
        '''
        if sourc.ms is not None:
            if os.path.exists(sourc.pathtodata+'/'+sourc.uvf):
                self.logger.error(sourc.uvf+" found, not overwriting.")
            else:    
                ms2uvfits(sourc.ms)
        else:
            self.logger.warn('No MS provided. I\'m assuming that it\'s already been generated.')
        # Change path to where the output should be.
        try: 
            os.chdir(sourc.path)
        except:
            self.logger.error(sourc.path+' does not exist, making it...')
            lib.basher("mkdir "+sourc.path)
            os.chdir(sourc.path)
        if os.path.exists(sourc.path+'/'+sourc.vis):
            self.logger.error(sourc.vis+' found, not overwriting.')
        else:
            self.wsrtfits.in_ = sourc.uvf
            self.wsrtfits.out = os.path.relpath(sourc.pathtodata, sourc.path)+'/'+sourc.vis
            self.wsrtfits.go()
        self.do_tsys(sourc.vis)
        self.fixhead(sourc.vis)

    def importdata(self): 
        '''
        A wrapper to perform multiple import operations.
        For a list of source objects, the module will import MS or UVFITS data from
        source.pathtoworking to source.path, performing attsys and fixing the header of each of the
        visiblity files. 
        '''
        path0 = os.getcwd()
        if type(self.source) is list:
            for sourc in self.source:
                # First, go to the MS file and convert it.
                self.importloop(sourc)
        else:
            sourc = self.source
            self.importloop(sourc) 
        os.chdir(path0)

    def fixhead(self, vis):
        '''
        Inserts important header information to a visibility data set. 
        '''
        puthd.in_ = vis+'/restfreq'
        puthd.value ='1.420405752'
        puthd.go()

        puthd.in_ = vis+'/interval'
        puthd.type = 'double'
        puthd.value= '1.0'
        puthd.go()

    def do_tsys(self, vis):
        '''
        Does Tsys correction in input vis using the MIRIAD task ATTSYS. 
        '''
        attsys.vis = vis
        if os.path.exists('attsys_temp'):
            lib.basher('rm -r attsys_temp')
        self.attsys.out = 'attsys_temp'
        self.attsys.go()
        lib.basher('mv attsys_temp '+vis)

####################################################################################################
# MIRIAD interfaces for CROSSCAL 

wsrtfits = lib.miriad('wsrtfits')
wsrtfits.in_ = 'somefile.UVF'
wsrtfits.op = 'uvin'
wsrtfits.velocity = 'optbary'
wsrtfits.out = 'somefile.uv'

uvflag = lib.miriad('uvflag')
uvflag.vis = 'cal1.uv'
uvflag.select = 'auto;shadow(25)'
uvflag.flagval = 'flag'

pgflag = lib.miriad('pgflag')
pgflag.stokes = 'qq'
pgflag.options = 'nodisp'
pgflag.command = '<'
pgflag.flagpar = '7,1,1,3,5,3,20'

mfcal = lib.miriad('mfcal')
mfcal.interval = 10000
mfcal.vis = 'cal1.uv'
mfcal.edge = '10,30'
mfcal.refant = 2

gpcopy = lib.miriad('gpcopy')
gpcopy.vis = 'cal1.uv'
gpcopy.out = 'src.uv'

uvcat = lib.miriad('uvcat')
uvcat.vis = 'src1.uv,src2.uv'
uvcat.out = 'src.uv'

uvlin = lib.miriad('uvlin')
uvlin.vis = 'src.uv'
uvlin.chans = '10,200,250,400,650,900'
uvlin.order = 5
uvlin.mode = 'chan0'
uvlin.out = 'src.uv_chan0'

uvcal = lib.miriad('uvcal')
uvcal.options = 'hanning'
uvcal.select=None
uvcal.out = 'hanning.uv'

puthd = lib.miriad('puthd')

attsys = lib.miriad('attsys')

####################################################################################################
# General initialization of MIRIAD interfaces. This will get passed to the class as attributes
# MIRIAD tasks used in this are:
# invert, selfcal, clean, obsrms, maths, restor, imstat 
 
# INVERT Default Parameters
invert = lib.miriad('invert')
invert.vis = 'vis'
invert.robust = '-2'
invert.slop = '0.5'
invert.imsize ='1500'
invert.cell = 4
invert.options='mfs,double'
invert.select = 'NONE'

# OBRMS for Calculating Theoretical Noise
obsrms = lib.miriad('obsrms')
obsrms.tsys = 50
obsrms.jyperk = 150
obsrms.antdiam = 25
obsrms.freq = 1.4
obsrms.theta = 15
obsrms.nants = 11
obsrms.bw = 20
obsrms.inttime = 12.*60.
obsrms.coreta = 0.88

# SELFCAL
selfcal = lib.miriad('selfcal')
selfcal.select = '-uvrange(0,0.5)'
selfcal.options = 'mfs,phase'
selfcal.refant = '2'
selfcal.interval = 2
selfcal.clip = 1e-6
selfcal.model = 'model'

# CLEAN
clean = lib.miriad('clean')
clean.map = 'map'
clean.beam = 'beam'
clean.out = 'model'
clean.cutoff = 5e-4
clean.niters=100000

# MATHS
maths = lib.miriad('maths')
maths.exp = 'map'
maths.mask = 'map.gt.1e-3'
maths.out = 'mask'

# RESTOR
restor = lib.miriad('restor')

# IMSTAT
imstat = lib.miriad('imstat')
