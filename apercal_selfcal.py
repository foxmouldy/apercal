#!/usr/bin/python
# Bradley Frank, ASTRON, 2015
import mirexec
import pylab as pl
from optparse import OptionParser
import sys
from ConfigParser import SafeConfigParser
import imp
from apercal import mirexecb 
from apercal import lib
import threading 
import time
import subprocess
import lib

#Check if PyBDSM is installed
try:
	imp.find_module('lofar')
	isbdsm = True
	from lofar import bdsm
except ImportError:
	isbdsm = False



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

def invertr(settings, spars):
	lpars = settings.get('image')
	mirrun(task='invert', vis=spars.vis


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
	sys.exit(0)
	tout = selfcal(params)

def lsm(params):
	#TODO: NVSS needs to be integrated here!!!!
	c = "python mk-nvss-lsm.py -i "+params.map+" -o "+params.lsm
	shrun(c)
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

def mkim0(params):
	'''
	Makes the 0th image.
	'''
	invout = invertr(params)
	immax, imunits = getimmax(params.map)
	maths(params.map, immax/float(params.c0), params.mask)
	params.cutoff = get_cutoff(params, cutoff=immax/float(params.c0))
	clean(params)
	restor(params)


class selfcal_multi(threading.Thread):
	def __init__(self, params, settings):
		threading.Thread.__init__(self)
		# NOTE: Now params is just the mpars defined below, which is a unit of spars. I use
		# the name params to disambiguate it from mpars.
		self.params = params
		# NOTE: settings is attached to the config file and contains all the generic
		# information.
		self.settings = settings

	def run(self):
		'''
		This is the selfcal engine that gets farmed out to multiple threads. 
		'''
		# TODO: Need to make a new directory for the outputs  
		params = self.params
		settings = self.settings
		print "SelfCal on ", params.vis, ' in this thread for target ', params.tag

		# NOTE: Move to the new directory.
		full_path = settings.full_path(params.vis+"_sc")
		# Now - we will dump the results in whatever path we're in.

		if bool(params.mkim0)!=False:
			iteri(params, i=0)
			image_cycle(params)
			sys.exit(0) # Perhaps this is the most appropriate?
		else:
			#NOTE: This seemingly defunct piece of code is necessary for vizquery to have a
			#reference.
			iteri(params, i=0)
			mkim0(params)
		
		# Use PyBDSM. Deprecated. DO NOT USE!
		if bool(params.bdsm)!=False:
			params.lsm = params.tag+'_bdsm'
			print 'Using PyBDSM to make LSM'
			bdsm(params)
		
		#NOTE: Use the NVSS as the LSM. Not always successful. 
		if bool(params.lsm)!=False:
			params.lsm = params.tag+'_lsm'
			params.model = params.lsm
			print 'Making LSM'
			lsm(params)
		
		# NOTE: Not needed?
		#R = [] #NOTE: Ratio of actual to theoretical noise
		
		
		# NOTE: Figure out how many loops to run, command line parameters **always** trump file
		# parameters.
		nloops = int(params.nloops)
		
		if nloops!=0:
			for i in range(0, nloops):
				#NOTE: iteri is the function that generates all the relevant names. 
				iteri(params, i+1)
				image_cycle(params, j=i+1)
				tout = selfcal(params) 
		
			#NOTE: Make the final image after selfcal, using the mask and cutoffs from the last run.
			otag = params.tag
			params.tag+='_asc'
			iteri(params, i='')
			image_cycle(params, j=i+1)

def selfcal_main(settings):
	'''
	Main module that controls the multi-threaded selfcal. 

	selfcal_main(settings), where settings is grabbed from a config file through:
	settings = apercal.lib.settings('someconfigfile.txt')
	'''
	# NOTE: The script parameters, spars, are grabbed here and used throughout the script.
	spars = settings.get('selfcal_multi')

		if bool(spars.imall)!=False:
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

		spars.nloops = int(spars.nloops)
		THREADS = []

		for v in spars.vis.split(','):
			# NOTE: Here we make the new directory and move to it. 
			if bool(spars.cleanup)!=False:
				o, e = shrun("rm -r "+v+"/gains")
				o, e = shrun("rm -r "+v+"_*")
			print "Running Thread ", nt, " for ", v
			nt+=1
			# NOTE: Now mpars only exists in this for loop, and is reserved for the
			# farming of the threads. It is a copy of spars 
			mpars = spars
			mpars.vis = v 
			mpars.tag = v
			THREADS.append(selfcal_multi(mpars, settings))
		for T in THREADS:
			print "Starting ", T
			T.start()
		
		for T in THREADS:
			time.sleep(1)
			print "Joining ", T
			T.join()

		print "DONE."

			

if __name__=="__main__":
	'''
	Command Line Usage
	'''
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
	
	if len(sys.argv)==1: 
		parser.print_help()
		dummy = sys.exit(0)
	else:
		params = lib.settings(options.config)
		selfcal_main(params)
