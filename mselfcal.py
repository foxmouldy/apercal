import mirexec
import pylab as pl
from optparse import OptionParser
import sys
from ConfigParser import SafeConfigParser
import imp
from apercal import mirexecb 
import threading 
import time
import subprocess

#Check if PyBDSM is installed
try:
	imp.find_module('lofar')
	isbdsm = True
	from lofar import bdsm
except ImportError:
	isbdsm = False

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--vis", "-v", type = 'string', dest = 'vis', default=None, 
	help = "Vis to be selfcal'd [None]");
parser.add_option("--config", "-c", type = 'string', dest='config', default=None, 
	help = 'Config file to be used [None]')
parser.add_option('--lsm', '-l', action='store_true', dest='lsm', default=False,
	help = "Use LSM for calibration [False]")
parser.add_option('--nloops', '-n', type='int', dest='nloops', default=0, 
	help = 'Number of Selfcal Loops [0]')
parser.add_option('--bdsm', '-b', action='store_true', dest='bdsm', default=False, 
	help = 'Use PyBDSM to create Gaussian LSM0 [False]')
parser.add_option('--mkim0', '-m', action='store_true', dest='mkim0', default=False, 
	help = 'MFS-Image the VIS and exit [False].')
parser.add_option('--par', '-p', type='string', dest='par', default=None, 
	help = 'Overwrite a single parameter: --par <par>:<value>;<par2>:<value2>')
parser.add_option("--cleanup", action='store_true', dest='cleanup', default=False,
	help = 'Remove old gains and start from scratch [False]')
parser.add_option("--imall", action='store_true', dest='imall', default=False,
	help = "Make a wide-band image with all visibilities and exit [False]")
(options, args) = parser.parse_args()	

class Bunch:
	'''
	Dummy container for the parameters.
	'''
	def __init__(self, **kwds): 
		self.__dict__.update(kwds)

def getimmax(image):
	imstat = mirexec.TaskImStat()
	imstat.in_ = image;
	imstats = imstat.snarf();
	immax = float(imstats[0][10][51:61]);
	imunits = imstats[0][4];
	return immax, imunits

def shrun(cmd):
	'''
	shrun: shell run - helper function to run commands on the shell. 
	'''
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, shell=True)
	out, err = proc.communicate()
	# NOTE: Returns the STD output. 
	return out, err

def invertr(params):
	invert = mirexec.TaskInvert()
	invert.vis = params.vis
	invert.select = params.select
	invert.line = params.line
	shrun('rm -r '+params.map)
	shrun('rm -r '+params.beam)
	invert.map = params.map
	invert.beam = params.beam
	invert.options = params.iopts 
	invert.slop = 0.5
	invert.stokes = 'ii'
	invert.imsize = 1500
	invert.cell = 4
	invert.fwhm = params.fwhm
	invert.robust= params.robust 
	tout = invert.snarf()
	#print ("\n".join(map(str, tout[0])))
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
	maths.exp = image
	maths.mask = image+".gt."+str(cutoff)
	maths.out = mask
	tout = maths.snarf()

def selfcal(params):
	selfcal = mirexec.TaskSelfCal()
	selfcal.vis = params.vis 
	selfcal.select = params.select
	selfcal.model = params.model
	selfcal.options = params.sopts
	selfcal.interval = params.interval
	selfcal.line = params.line
	if params.clip!='':
		selfcal.clip = params.clip
	tout = selfcal.snarf()
	return tout

def wgains(params):
	uvcat = mirexec.TaskUVCat()
	uvcat.vis = params.vis
	uvcat.out = '.temp'
	tout = uvcat.snarf()
	shrun('rm -r '+params.vis)
	shrun('mv .temp '+params.vis)

def get_cutoff(params, cutoff=1e-3):
	'''
	This uses OBSRMS to calculate the theoretical RMS in the image.
	'''
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

def image_cycle(params, j=1):
	c1 = pl.linspace(float(params.c0), float(params.c0)+2.*float(params.dc), 3)*(j)
	c2 = c1*10.
	invout = invertr(params)
	immax, imunits = getimmax(params.map)
	maths(params.map, immax/c1[0], params.mask)
	params.cutoff = get_cutoff(params, cutoff=immax/c2[0])
	clean(params)
	restor(params)
	immax, imunits = getimmax(params.image)
	maths(params.image, immax/c1[1], params.mask)
	params.cutoff = get_cutoff(params, cutoff=immax/c2[1])	
	clean(params)
	restor(params)
	immax, imunits = getimmax(params.image)
	maths(params.image, immax/c1[2], params.mask)
	params.cutoff = get_cutoff(params, cutoff=immax/c2[2])
	clean(params)
	restor(params)
	cmmax, cmunits = getimmax(params.model)
	params.clip = cmmax/(100.*j)
	restor(params, mode='residual')


def bdsm(params):
	'''
	This runs PyBDSM on the image to make a mask from the Gaussian output from the source
	finder. 
	'''
	# Export the Image as Fits
	fits = mirexec.TaskFits()
	fits.in_ = params.image
	fits.op = 'xyout'
	fits.out = params.image+'.fits'
	fits.snarf()

	# Run PyBDSM on the Image
	img = bdsm.process_image(params.image+'.fits')
	img.export_image(outfile = params.image+'gaus_model.fits', im_type='gaus_model')
	img.write_catalog(outfile = params.image+'gaus_model.txt')
	
	# Use the Gaussian Image File as a Model
	fits.in_ = params.image+'gaus_model.fits'
	fits.op = 'xyin'
	fits.out = params.lsm
	fits.snarf()
	params.model = params.lsm
	#print params
	sys.exit(0)
	tout = selfcal(params)
	#print 'Selfcal Output Using PyBDSM:'
	#print ("\n".join(map(str, tout[0])))

def lsm(params):
	c = "python mk-nvss-lsm.py -i "+params.map+" -o "+params.lsm
	shrun(c)
	#print 'Made LSM'
	tout = selfcal(params) 
	#print 'Selfcal Output Using LSM:'
	#print ("\n".join(map(str, tout[0])))


#global params
	
def iteri(params, i):
	params.map = params.tag+'_map'+str(i)
	params.beam = params.tag+'_beam'+str(i)
	params.mask = params.tag+'_mask'+str(i)
	params.model = params.tag+'_model'+str(i)
	params.image = params.tag+'_image'+str(i)
	params.lsm = params.tag+'_lsm'+str(i)
	params.residual = params.tag+'_residual'+str(i)


# Setup the parameters 

# First, check if we want to use a config file

def get_params(configfile=None):
	if configfile!=None:
		config_parser = SafeConfigParser()
		config_parser.read(configfile)
		params = Bunch()
		for p in config_parser.items('selfcal'):
			setattr(params, p[0], p[1])
		return params
	else:
		params = Bunch(vis=options.vis, 
		select='-uvrange(0,1)', 
		tag = 'sc', 
		map='map_temp', 
		beam='beam_temp', 
		mask = 'mask_temp', 
		model='model_temp', 
		image = 'image_temp', 
		residual = 'residual_temp', 
		robust='-2.0',
		lsm='lsm_temp', 
		line='channel,900,1,1,1', 
		sopts='mfs,phase', 
		iopts='mfs,double', 
		interval=5,
		fwhm='', 
		cutoff=1e-2, 
		clip='', 
		nloops=None, 
		nsigma=3,
		c0=2.5,
		dc=3.0, 
		inttime=1., 
		tsys = 30., 
		bw = 20.)
		return params


def mkim0(params):
	'''
	Makes the 0th image.
	'''
	#print "Making Initial Image"
	invout = invertr(params)
	immax, imunits = getimmax(params.map)
	maths(params.map, immax/float(params.c0), params.mask)
	params.cutoff = get_cutoff(params, cutoff=immax/float(params.c0))
	clean(params)
	restor(params)

# Make the Initial Image

class mselfcal(threading.Thread):
	def __init__(self, params):
		threading.Thread.__init__(self)
		self.params = params

	def run(self):
		'''
		This is the selfcal engine that gets farmed out to multiple threads. 
		'''
		params = self.params
		print "SelfCal on ", params.vis, ' in this thread for target ', params.tag
		#sys.exit(0)
		if options.mkim0!=False:
			iteri(params, i=0)
			image_cycle(params)
			sys.exit(0) # Perhaps this is the most appropriate?
		else:
			#NOTE: This seemingly defunct piece of code is necessary for vizquery to have a
			#reference.
			iteri(params, i=0)
			mkim0(params)
		
		# Use PyBDSM. Deprecated. DO NOT USE!
		if options.bdsm!=False:
			params.lsm = params.tag+'_bdsm'
			print 'Using PyBDSM to make LSM'
			bdsm(params)
		
		#NOTE: Use the NVSS as the LSM. Not always successful. 
		if options.lsm!=False:
			params.lsm = params.tag+'_lsm'
			params.model = params.lsm
			print 'Making LSM'
			lsm(params)
		
		R = [] #NOTE: Ratio of actual to theoretical noise
		
		
		# NOTE: Figure out how many loops to run, command line parameters **always** trump file
		# parameters.
		if options.nloops!=0:
			nloops = int(options.nloops)
		else:
			nloops = int(params.nloops)
		
		#print "Running ", nloops, " SelfCal Iterations."
		if nloops!=0:
			for i in range(0, nloops):
				#print 'Selfcal Cycle '+str(i+1)
				iteri(params, i+1)
				image_cycle(params, j=i+1)
				tout = selfcal(params) 
				'Selfcal Output: '+str(i+1)
				#print ("\n".join(map(str, tout[0])))
				ratstr = [s for s in tout[0] if 'Ratio of Actual to Theoretical noise:' in s]
				R.append(float(str(ratstr[0]).split(':')[1]))
		
			#NOTE: Make the final image after selfcal, using the mask and cutoffs from the last run.
			otag = params.tag
			params.tag+='_asc'
			iteri(params, i='')
			image_cycle(params, j=i+1)

nt = 0

params0 = get_params(configfile=options.config)
# NOTE: Command line parameters **always** trumps file parameters.
if options.par!=None:
	print "Setting up Custom Params..."
	pars = options.par.split(';')
	for par in pars:
		p = par.split(':')	
		setattr(params0, p[0], p[1])

visfiles = params0.vis

if __name__=="__main__":
	if len(sys.argv)==1: 
		parser.print_help()
		dummy = sys.exit(0)
	else:
		if options.imall!=False:
			print "Making Wide Band Image..."
			params0.line=""
			#NOTE: Increase the CLEAN depth by the nominal increase in sensitivity.
			params0.dc = float(params0.dc) * pl.sqrt(8.)
			#NOTE: Increase the BW
			params0.bw = float(params0.bw) * 8.
			for i in range(0,int(params0.nloops)):
				print "Loop=", str(i)
				iteri(params0, i=i+1)
				image_cycle(params0, j=i+1)
			print "Completed Wide Band Image"
			sys.exit(0)

		options.nloops = int(options.nloops)
		THREADS = []
		for v in visfiles.split(','):
			if options.cleanup!=False:
				shrun("rm -r "+v+"/gains")
				shrun("rm -r "+v+"_*")
			print "Running Thread ", nt, " for ", v
			nt+=1
			pars = get_params(configfile=options.config)
			pars.vis = v
			pars.tag = v
			THREADS.append(mselfcal(pars))
		for T in THREADS:
			print "Starting ", T
			T.start()
		
		for T in THREADS:
			time.sleep(1)
			print "Joining ", T
			T.join()

		print "DONE."
