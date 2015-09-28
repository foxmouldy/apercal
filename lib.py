#Monday, 28 September 2015
import mirexecb
import mirexecb as mirexec
import logging
from ConfigParser import SafeConfigParser
import subprocess
import mynormalize
import pylab as pl
import os
import sys
import logging
# Needs astropy for querying the NVSS
from astroquery.vizier import Vizier
from astropy.coordinates import Angle, ICRS, Distance, SkyCoord
import astropy.coordinates as coord
from astropy import units as u
from astropy.io import ascii
deg2rad = pl.pi/180.
# Its rather messy to reload the logging library, but is necessary if the logger is going to work.
reload(logging)

def write2file(header, text2write, file2write):
    '''
    write2file writes the output of some task to a textfile.
    '''
    f = open(file2write, 'a')
    f.writelines(header)
    f.writelines('\n')
    for t in text2write.split('\n'):
            f.writelines(t+'\n')
    f.writelines('\n---- \n')
    f.close()

def setup_logger(level='info', logfile=None):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False 
    
    fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
            datefmt='%m/%d/%Y %I:%M:%S %p')
    if logfile is None:
        fh = logging.FileHandler('log_filename.txt')
    else:
        fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    
    ch_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    ch = logging.StreamHandler()
    if level=='info':
        ch.setLevel(logging.INFO)
    if level=='debug':    
        ch.setLevel(logging.DEBUG)
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)
    logger.info("Logging started!")
    return logger


class FatalMiriadError(Exception):
    '''
    Custom  Exception for Fatal MIRIAD Errors
    '''
    def __init__(self, error=None):
        if error is None:
            self.message = "Fatal MIRIAD Task Error"
        else:
            self.message = "Fatal MIRIAD Task Error: \n"+error
        super(FatalMiriadError, self).__init__(self.message)
        sys.exit(self.message)

def exceptioner(O, E):
    '''
    exceptioner(O, E) where O and E are the stdout outputs and errors.
    A simple and stupid way to do exception handling.
    '''
    for e in E.split('\n'):
        if "FATAL" in e.upper()>0:
            raise FatalMiriadError(E)

def str2bool(s):
    if s.upper() == 'TRUE' or s.upper()=="T" or s.upper()=="Y":
         return True
    elif s.upper() == 'FALSE' or s.upper()=='F' or s.upper()=='N':
         return False
    else:
         raise ValueError # evil ValueError that doesn't tell you what the wrong value was

def mkdir(path):
    '''
    mkdir(path)
    Checks if path exists, and creates if it doesn't exist.
    '''
    if not os.path.exists(path):
        print path
        print os.path.exists(path)
        print 'Making Path'
        o, e = basher('mkdir '+path)
        print o, e

def masher(task=None, **kwargs):
    '''
    masher - Miriad Task Runner
    Usage: masher(task='sometask', arg1=val1, arg2=val2)
    Example: masher(task='invert', vis='/home/frank/test.uv/', options='mfs,double', ...)
    Each argument is passed to the task through the use of the keywords.
    '''
    logger = logging.getLogger('masher')
    if task!=None:
        argstr = " "
        for k in kwargs.keys():
            if str(kwargs[k]).upper()!='NONE':
                argstr += k + '=' + str(kwargs[k])+ ' '

        cmd = task + argstr
        logger.debug(cmd)
        if ("-k" in cmd) is True:
            out, err = basher(cmd, showasinfo=True)
        else:
            out, err = basher(cmd, showasinfo=False)
        exceptioner(out, err)
        # Used to log twice. Not anymore!
        return out
    else:
        print "Usage = masher(task='sometask', arg1=val1, arg2=val2...)"

def basher(cmd, showasinfo=False):
    '''
    basher: shell run - helper function to run commands on the shell.
    '''
    logger = logging.getLogger('basher')
    logger.debug(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr = subprocess.PIPE, shell=True)
    out, err = proc.communicate()

    if len(out)>0:
        if showasinfo==True:
            logger.info("Command = "+out)
        else:
            logger.debug("Command = "+out)
    if len(err)>0:
        logger.warning(err)
    # NOTE: Returns the STD output.
    return out, err

def get_source_names(vis=None):
    '''
    get_source_names (vis=None)
    Helper function that uses the MIRIAD task UVINDEX to grab the name of the
    sources from a MIRIAD visibility file.
    '''
    if vis!=None:
        uvindex = mirexecb.TaskUVIndex ()
        uvindex.vis = vis
        u = uvindex.snarf ()
        i = [i for i in range(0,len(u[0])) if "pointing" in u[0][i]]
        N = len(u[0])
        s_raw = u[0][int(i[0]+2):N-2]
        sources = []
        for s in s_raw:
            sources.append(s.replace('  ', ' ').split(' ')[0])
        return sources
    else:
        print "get_source_names needs a vis!"

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    def __getitem__(self, key):
        return getattr(self, key)

class settings:
    def __init__(self, filename):
        self.filename = filename
        self.parser = SafeConfigParser ()
        self.parser.read(self.filename)

    def set(self, section, **kwds):
        '''
        settings.set(section, keyword1=value1, keyword2=value2)
        Change settings using this method.
        '''
        parser = self.parser
        for k in kwds:
            parser.set(section, k, kwds[k])
        self.save()

    def show(self, section=None):
        '''
        settings.show(section=None)
        Output the settings, by section if necessary.
        '''
        logger = logging.getLogger('settings.show') 
        parser = self.parser
        try:
                if section!=None:
                    print "["+section+"]"
                    for p in parser.items(section):
                        print p[0], " : ", p[1]
                    print "\n"
                else:
                    for s in parser.sections ():
                        print "["+s+"]"
                        for p in parser.items(s):
                            print p[0], " : ", p[1]
                        print "\n"
        except:
            logger.error("Settings - Section doesn't exist.")

    def get(self, section=None, keyword=None):
        logger = logging.getLogger('settings.get')
        parser = self.parser
        try:
            if section is not None and keyword is not None:
                if len(parser.get(section, keyword).split(';'))>1:
                    return parser.get(section, keyword).split(';')
                else:
                    return parser.get(section, keyword)
            else:
                return get_params(parser, section)
        except:
            logger.error("Settings - Either section or keyword does not exist.")

    def update(self):
        '''
        Read the file again.
        '''
        logger = logging.getLogger('settings.update')  
        logger.info("Settings - Updated.")
        self.parser.read(self.filename)

    def save(self):
        '''
        settings.save()
        Saves the new settings.
        '''
        parser = self.parser
        parser.write(open(self.filename, 'w'))

    def full_path(self, dirx):
        '''
        Uses rawdata and base to make the full working path, when necessary.
        '''
        #full_path = self.get('data', 'working')+self.get('data', 'base')
        full_path = self.get('data', 'working')+dirx
        return full_path

def get_params(config_parser, section):
    params = Bunch()
    for p in config_parser.items(section):
        setattr(params, p[0], p[1])
    return params

def ms2uvfits(inms=None, outuvf=None):
    '''
    ms2uvfits(inms=None, outuvf=None)
    Utility to convert inms to outuvf in the same directory. If outuvf is not specified, then
    inms is used with .MS replaced with .UVF.
    '''
    if outuvf==None:
        outuvf = inms.replace(".MS", ".UVF")
    cmd = "ms2uvfits ms="+inms+" fitsfile="+outuvf+" writesyscal=T multisource=T combinespw=T"
    basher(cmd)
    print inms, "--> ms2uvfits --> ", outuvf

def iteri(params, i):
    params.map = params.vis+'_map'+str(i)
    params.beam = params.vis+'_beam'+str(i)
    params.mask = params.vis+'_mask'+str(i)
    params.model = params.vis+'_model'+str(i)
    params.image = params.vis+'_image'+str(i)
    params.lsm = params.vis+'_lsm'+str(i)
    params.residual = params.vis+'_residual'+str(i)
    return params

def mkim(settings0):
    '''
    Makes the 0th image.
    '''
    #print "Making Initial Image"
    params = settings0.get('image')
    os.chdir(settings0.get('data', 'working'))
    #params.vis = settings0.get('data', 'working') + params.vis
    params.vis = params.vis
    params = iteri(params, 0)
    invout = invertr(params)
    print "Done INVERT"
    immax, imunits = getimmax(params.map)
    maths(params.map, immax/float(params.c0), params.mask)
    print "Done MATHS"
    params.cutoff = get_cutoff(settings0, cutoff=immax/float(params.c0))
    clean(params)
    print "Done CLEAN"
    restor(params)
    print "Done RESTOR"

def getimmax(image):
    imstat = mirexec.TaskImStat()
    imstat.in_ = image;
    imstats = imstat.snarf();
    immax = float(imstats[0][10][51:61]);
    imunits = imstats[0][4];
    return immax, imunits

def get_cutoff(settings0, cutoff=1e-3):
    '''
    This uses OBSRMS to calculate the theoretical RMS in the image.
    '''
    params = settings0.get('obsrms')
    obsrms = mirexecb.TaskObsRMS()
    obsrms.tsys = params.tsys
    obsrms.jyperk = 8.
    obsrms.freq = 1.4 # Does not depend strongly on frequency
    obsrms.theta = 12. # Maximum resolution in arcseconds
    obsrms.nants = params.nants
    obsrms.bw = params.bw # In MHz!
    obsrms.inttime = params.inttime
    obsrms.antdiam = 25.
    rmsstr = obsrms.snarf()
    rms = rmsstr[0][3].split(";")[0].split(":")[1].split(" ")[-2]
    noise = float(params.nsigma)*float(rms)/1000.
    # NOTE: Breakpoints to check your noise.
    #print "Noise = ", noise
    #print "cutoff = ", cutoff
    if cutoff > noise:
        # NOTE: More Breakpoints.
        #print "cutoff > noise"
        return cutoff
    else:
        # NOTE: More Breakpoints.
        #print "cutoff < noise"
        return noise

def invertr(params):
    invert = mirexec.TaskInvert()
    invert.vis = params.vis
    if params.select!='':
        invert.select = params.select
    if params.line!='':
        invert.line = params.line
    basher('rm -r '+params.map)
    basher('rm -r '+params.beam)
    invert.map = params.map
    invert.beam = params.beam
    invert.options = params.options
    invert.slop = 0.5
    invert.stokes = 'ii'
    invert.imsize = params.imsize
    invert.cell = params.cell
    invert.robust= params.robust
    tout = invert.snarf()
    return tout

def clean(params):
    clean = mirexec.TaskClean()
    clean.map = params.map
    clean.beam = params.beam
    clean.cutoff = params.cutoff
    if params.mask!=None:
        clean.region='mask('+params.mask+')'
        clean.niters = 100000
    else:
        clean.niters = 1000
    basher('rm -r '+params.model)
    clean.out = params.model
    tout = clean.snarf()
    #print ("\n".join(map(str, tout[0])))
    return tout

def restor(params, mode='clean'):
    restor = mirexec.TaskRestore()
    restor.beam = params.beam
    restor.map = params.map
    restor.model = params.model
    if mode!='clean':
        restor.out = params.residual
        restor.mode = 'residual'
    else:
        restor.out = params.image
        restor.mode = 'clean'

    basher('rm -r '+restor.out)
    tout = restor.snarf()

def maths(image, cutoff, mask):
    basher('rm -r '+mask)
    maths = mirexec.TaskMaths()
    maths.exp = '<'+image+'>'
    maths.mask = '<'+image+'>'+".gt."+str(cutoff)
    maths.out = mask
    tout = maths.snarf()

def uvflag(vis, select, flagval='flag'):
    '''
    Utility to flag your data
    '''
    path = os.path.split(vis)
    os.chdir(path[0])
    O, E = masher(task = 'uvflag', vis = path[1], select=select, flagval = flagval)
    if len(E)>1:
        sys.exit(E)

##############################################################
# The following sections are for querying the NVSS

def ann_writer(options, x):
    annfile = options.outfile+'.ann'
    ann = open(annfile, 'w')
    ann.writelines("COORD W\n")
    ann.writelines("PA STANDARD\n")
    ann.writelines("COLOR ORANGE\n")
    ann.writelines("FONT hershey14\n")
    for i in range(0,len(x)):
        line = "CROSS "+str(x[i]["_RAJ2000"])+" "+str(x[i]["_DEJ2000"])+" 0.05 0.05 45.\n"
        ann.writelines(line)
    ann.close()

def fixra(ra0):
    R = ''
    s = 0
    for i in ra0:
        if i==':':
            if s==0:
                R+='h'
                s+=1
            else:
                R+='m'
        else:
            R+=i
    return R

def getradec(infile):
    '''
    getradec: module to extract the pointing centre ra and dec from a miriad image file. Uses
    the PRTHD task in miriad
    inputs: infile (name of file)
    returns: c, an instance of the astropy.coordinates SkyCoord class which has a few convenient
    attributes.
    '''
    o, e = masher(task='prthd', in_=infile)
    #prthd = mirexec.TaskPrintHead()
    #prthd.in_ = infile
    #p = prthd.snarf()
    rastring = [s for s in p[0] if "RA---" in s]
    decstring = [s for s in p[0] if "DEC--" in s]
    print rastring
    ra0 = rastring[0][15:32].replace(' ','')
    ra0 = list(ra0)
    ra0 = fixra(ra0)
    dec0 = decstring[0][15:32].replace(' ','')
    coords = [ra0, dec0]
    c = SkyCoord(ICRS, ra=ra0, dec=dec0, unit=(u.deg,u.deg))
    return c

def query_nvss(options, ra0, dec0, s=">0.0", proj='SIN'):
    '''
    query_nvss: module which queries the NVSS using the Vizier protocol.
    inputs: ra0, dec0, s="<20"
    ra0 = the central ra in degrees
    dec0 = the central dec in degrees
    s = the flux cutoff
    returns L, M (relative coordinates in degrees), N (number of sources), S (1.4GHz Flux
    Density in mJy)
    '''
    v = Vizier(column_filters={"S1.4":s})
    v.ROW_LIMIT = 10000
    result = v.query_region(coord.SkyCoord(ra=ra0, dec=dec0, unit=(u.deg, u.deg), frame='icrs'),
        radius=Angle(1, "deg"), catalog='NVSS')
    ra = result[0]['_RAJ2000']
    dec = result[0]['_DEJ2000']
    N = len(result[0])
    if proj.upper()=='SIN':
        L = (ra-ra0)*pl.cos(dec*deg2rad)
        M = dec-dec0
    if proj.upper()=='NCP':
        L = 57.2957795*pl.cos(deg2rad*dec)*pl.sin(deg2rad*(ra-ra0))
        M = 57.2957795*(pl.cos(deg2rad*dec0) - pl.cos(deg2rad*dec)*pl.cos(deg2rad*(ra-ra0)))/pl.sin(deg2rad*dec0)
    S = result[0]['S1.4']
    ascii.write(result[0], options.outfile+'.dat', format='tab')
    ann_writer(options, result[0])
    return L, M, N, S

def mk_lsm(options):
    '''
    mk_lsm: The module that makes the NVSS LSM using the miriad task IMGEN.
    Needs options.infile (template) and options.outfile (name of output point source model)
    '''

    # NOTE: Classic cos^6 model of the WSRT PB used to calculate apparent fluxes. Here we use c=68.
    PB = lambda c, v, r: (pl.cos(c*v*r))**6

    # NOTE: Grab the central coordinates from the template file.
    c = getradec(options.infile)
    print c
    ra0 = c.ra.deg
    dec0 =     c.dec.deg

    # NOTE: Query the NVSS around the central pointing
    L, M, N, S = query_nvss(options, ra0, dec0, s='>10.', proj='NCP')
    L_asec = L*3600.
    M_asec = M*3600.
    pl.scatter(L_asec, M_asec, c=S*1000, s=S)
    pl.xlabel('L offset (arcsec)')
    pl.ylabel('M offset (arcsec)')
    pl.colorbar()
    pl.savefig(options.infile+'-nvss-lsm.pdf', dpi=300)
    pl.close()
    n = 20
    modfiles = ''
    # NOTE: Make the LSM!
    imgen = mirexec.TaskImGen()
    for j in range(0,1+N/n):
        imgen.in_ = options.infile
        imgen.out = 'tmod'+str(j)
        os.system('rm -r '+str(imgen.out))
        objs = ''
        spars = ''
        for i in range(0,n):
            if (i+j*n<N):
                objs+= 'point,'
                d2point = L[i+j*n]**2+M[i+j*n]**2
                S_app = S[i+j*n]*PB(c=68, v=1.420, r=d2point)
                spars+= str(S_app/1e3)+','+str(L_asec[i+j*n])+','+str(M_asec[i+j*n])+','
        imgen.factor=0
        imgen.object = objs[:-1]
        imgen.spar = spars[:-1]
        imgen.snarf()
        modfiles+='<'+imgen.out+'>+'
    maths = mirexec.TaskMaths()
    maths.exp = modfiles[0:-1]
    os.system('rm -r '+options.outfile)
    maths.out = options.outfile
    maths.snarf()
    os.system('rm -r tmod*')
