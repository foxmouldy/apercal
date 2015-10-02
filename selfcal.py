import lib
import logging
import pylab as pl
import os
import sys

class wcal:
    '''
    wcal: WSRT SelfCal
    Object that does conventional SelfCal using a process that's been well tested for WSRT data.
    '''
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.logger = logging.getLogger('wcal')
        # Initial Attributes: Constant - Things that you want to change
        self.path = "./"
        self.num_major = 5 
        self.num_minor = 3
        self.vis = 'vis'
        self.output = 'output'
        self.c0 = 3
        self.dc = 3
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
        self.invert.vis = self.vis 

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

        # Now, where is the visibility file relative to present working directory? 
        #self.vis = os.path.relpath(self.vis, os.getcwd())
        self.logger.info("Making symbolic/soft link to your visibility file")
        lib.basher("ln -s "+self.path+'/'+self.vis)
        self.selfcal.vis = self.vis
        self.invert.vis = self.vis
        # Advanced Attributes
        # This is an extra level of protection against not having enough cutoffs.
        self.mask_cutoffs = pl.linspace(float(self.c0), float(self.c0)+2.*float(self.dc), self.num_minor)
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
        So if the user wants to do a one-off invert or clean, then they do it with their own names
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
            logger.info('/minor-cycle = '+str(j))
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
 
# General initialization of MIRIAD interfaces. This will get passed to the class as attributes
# MIRIAD tasks used in this are:
# invert, selfcal, clean, obsrms, maths, restor, imstat 
 
# INVERT Default Parameters
invert = lib.miriad('invert')
invert.keywords()
invert.vis = 'vis'
invert.robust = '-2'
invert.slop= '0.5'
invert.imsize='1500'
invert.cell = 4
invert.options='mfs,double'

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
clean.go()

# MATHS
maths = lib.miriad('maths')
maths.exp = 'map'
maths.mask = 'map.gt.1e-3'
maths.out = 'mask'

# RESTOR
restor = lib.miriad('restor')

# IMSTAT
imstat = lib.miriad('imstat')
