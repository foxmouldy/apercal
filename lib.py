import mirexecb
import mirexecb as mirexec
from ConfigParser import SafeConfigParser
import subprocess
import mynormalize
import pylab as pl
import os 
import sys
#import mselfcal

def mirrun(task=None, verbose=False, **kwargs):
    '''
    mirrun - Miriad Task Runner
    Usage: mirrun(task='sometask', arg1=val1, arg2=val2)
    Example: mirrun(task='invert', vis='/home/frank/test.uv/', options='mfs,double', ...)
    Each argument is passed to the task through the use of the keywords. 
    '''
    if task!=None:
        argstr = " "
        for k in kwargs.keys():
            argstr += k + '=' + kwargs[k]+ ' '
        cmd = task + argstr
        out, err = shrun(cmd)        
        if verbose!=False:
               print cmd
               print out, err
        return out, err
    else:
        print "Usage = mirrun(task='sometask', arg1=val1, arg2=val2...)"

def shrun(cmd):
	'''
	shrun: shell run - helper function to run commands on the shell.
	'''
	#print cmd
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        	stderr = subprocess.PIPE, shell=True)
	out, err = proc.communicate()
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
        self.show(section=section)
        self.save()
    
    def show(self, section=None):
        '''
        settings.show(section=None)
        Output the settings, by section if necessary.
        '''
        parser = self.parser
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
    def get(self, section, keyword=None):
        parser = self.parser
        if keyword!=None:
            if len(parser.get(section, keyword).split(','))>1:
                return parser.get(section, keyword).split(',')
            else:
                return parser.get(section, keyword)
        else:
            return get_params(parser, section)
    
    def update(self):
        '''
        Read the file again. 
        '''
        print "Updated"
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
	shrun(cmd)	
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
    shrun('rm -r '+params.map)
    shrun('rm -r '+params.beam)
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
	shrun('rm -r '+params.model)
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

	shrun('rm -r '+restor.out)
	tout = restor.snarf()
	
def maths(image, cutoff, mask):
	shrun('rm -r '+mask)
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
    O, E = mirrun(task = 'uvflag', vis = path[1], select=select, flagval = flagval)
    if len(E)>1:
        sys.exit(E)
    