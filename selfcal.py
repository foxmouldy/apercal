#!/usr/bin/python
# Bradley Frank, ASTRON, 2015
import pylab as pl
from optparse import OptionParser
import sys
import imp
from apercal import lib
import threading 
import time
import subprocess
import lib
import os
import logging
logger = logging.getLogger('selfcal')
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
 	o, e = lib.mirrun(task='imstat', in_=image)
	immax = float(o.split('\n')[10][51:61])
	imunits = o.split('\n')[4]
	return immax, imunits

def invertr(settings, spars):
	'''
	output = invertr(settings, spars)
	Runs MIRIAD's invert on spars.vis, using settings.get('image'). Returns the output from
	mirrun.

	'''
	vis = spars.vis 
	lpars = settings.get('image')
	#NOTE: Clean up
	o, e = lib.shrun('rm -r '+spars.map)
	o, e = lib.shrun('rm -r '+spars.beam)
	mirout, mirerr = lib.mirrun(task='invert', vis=vis, select=lpars.select,
			line=lpars.line, map = spars.map, beam=spars.beam, options=lpars.options,
			slop=lpars.slop, stokes=lpars.stokes, imsize=lpars.imsize, cell=lpars.cell,
			fwhm=lpars.fwhm, robust=lpars.robust)
	lib.exceptioner(mirout, mirerr)
	return mirout
		
def clean(lpars):
	'''
	output = clean(lpars)
	Runs MIRIAD's clean, using standard settings.
	'''
	#NOTE: Cleanup
	o, e = lib.shrun("rm -r "+lpars.model)
	if lpars.mask!=None:
		#NOTE: Use mask if provided. 
		mirout, mirerr = lib.mirrun(task='clean', map=lpars.map, beam=lpars.beam,
				out=lpars.model, cutoff=lpars.cutoff,
				region="'mask("+lpars.mask+")'", niters=100000)
		lib.exceptioner(mirout, mirerr)
	else:
		#NOTE: Do a 'light' clean if no mask provided.
		mirout, mirerr = lib.mirrun(task='clean', map=lpars.map, beam=lpars.beam,
				out=lpars.model, cutoff=lpars.cutoff, niters=1000)
		lib.exceptioner(mirout, mirerr)
	return mirout

def restor(lpars, mode='clean'):	
	'''
	output = restor(params, mode='clean')
	Uses the MIRIAD task restor to restor a model image, creating either an image or a
	residual.
	'''
	if mode.upper()!="CLEAN":
		# Make the residual
		# Cleanup
		o, e = lib.shrun('rm -r '+lpars.residual)
		mirout, mirerr = lib.mirrun(task='restor', beam=lpars.beam, map=lpars.map,
				model=lpars.model, out=lpars.residual, mode='residual')
	else:
		# Make the image
		# Cleanup
		o, e = lib.shrun('rm -r '+lpars.image)
		mirout, mirerr = lib.mirrun(task='restor', beam=lpars.beam, map=lpars.map,
				model=lpars.model, out=lpars.image, mode=mode)

	return mirout	
	
def make_mask(image, cutoff, mask):
	'''
	output = make_mask(image, cutoff, mask)
	Uses the MIRIAD task MATHS to make a threshold mask. The input <image> is thresholded with
	cutoff, and a <mask> is created.
	'''
	# Cleanup
	o, e = lib.shrun('rm -r '+mask)
	# NOTE: MATHS is stupid and doesn't know how to follow paths. So we have to make a symbolic
	# link to the images.
	lib.shrun('ln -s '+image) 	
	mirout, mirerr = lib.mirrun(task='maths', exp=os.path.split(image)[1],
			mask=os.path.split(image)[1]+".gt."+str(cutoff),
			out=mask)
	lib.exceptioner(mirout, mirerr)
	# Remove the symbolic link
	lib.shrun('rm '+os.path.split(image)[-1]) 	

	# Climb up back to the original path

	return mirout

def selfcal(vis, settings):
	'''
	output = selfcal(lpars)
	Uses the MIRIAD task selfcal to do... well... selfcal. 
	'''
	lpars = settings.get('selfcal')
	mirout, mirerr = lib.mirrun(task='selfcal', vis=vis, select=lpars.select,
				model=lpars.model, options=lpars.options, interval=lpars.interval,
				line=lpars.line, clip=lpars.clip)
	return mirout		

def wgains(lpars):
	'''
	Write the gains into a new file.
	'''
	mirout, mirerr = lib.mirrun(task='uvcat', vis=lpars.vis, out='.temp') 
	#tout = uvcat.snarf()
	o, e = lib.shrun('rm -r '+lpars.vis)
	o, e = lib.shrun('mv .temp '+lpars.vis)

def get_cutoff(lpars, cutoff=1e-3):
	'''
	This uses OBSRMS to calculate the theoretical RMS in the image.
	'''
	#lpars = settings.get('obsrms')

	mirout, mirerr = lib.mirrun(task='obsrms', tsys=lpars.tsys, jyperk=lpars.jperk,
			freq=lpars.freq, theta=lpars.theta, nants=lpars.nants, bw=lpars.bw,
			inttime=lpars.inttime, antdiam=lpars.antdiam)

	rms = mirout.split('\n')[3].split(";")[0].split(":")[1].split(" ")[-2]
	noise = float(lpars.nsigma)*float(rms)/1000.	
	# NOTE: Breakpoints to check your noise. 
	if cutoff > noise:
		# NOTE: More Breakpoints. 
		#print "cutoff > noise"
		return cutoff
	else:
		# NOTE: More Breakpoints. 
		#print "cutoff < noise"
		return noise

def image_cycle(settings, params, j=1):
	c1 = pl.linspace(float(params.c0), float(params.c0)+2.*float(params.dc), 3)*(j)
	c2 = c1*10.
	invout = invertr(settings, params)
	immax, imunits = getimmax(params.map)
	make_mask(params.map, immax/c1[0], params.mask)
	params.cutoff = get_cutoff(settings.get('obsrms'), cutoff=immax/c2[0])
	clean(params)
	restor(params)
	immax, imunits = getimmax(params.image)
	make_mask(params.image, immax/c1[1], params.mask)
	params.cutoff = get_cutoff(settings.get('obsrms'), cutoff=immax/c2[1])	
	clean(params)
	restor(params)
	immax, imunits = getimmax(params.image)
	make_mask(params.image, immax/c1[2], params.mask)
	params.cutoff = get_cutoff(settings.get('obsrms'), cutoff=immax/c2[2])
	clean(params)
	restor(params)
	cmmax, cmunits = getimmax(params.model)
	params.clip = cmmax/(100.*j)
	restor(params, mode='residual')


def bdsm(lpar):
	'''
	This runs PyBDSM on the image to make a mask from the Gaussian output from the source
	finder. 
	'''
	# Export the Image as Fits
	mirout, mirerr = lib.mirrun(task='fits', in_=lpars.image, op='xyout',
		out=lpars.image+'.fits') 

	# Run PyBDSM on the Image
	img = bdsm.process_image(params.image+'.fits')
	img.export_image(outfile = params.image+'gaus_model.fits', im_type='gaus_model')
	img.write_catalog(outfile = params.image+'gaus_model.txt')
	
	# Use the Gaussian Image File as a Model
	mirout, mirerr = lib.mirrun(task='fits', in_=params.image+'gaus_model.fits', op='xyin',
			out=lpars.lsm)
	lpars.model = lpars.lsm
	tout = selfcal(lpars)

def make_nvss_lsm(params):
	#TODO: NVSS needs to be integrated here!!!!
	c = "python mk-nvss-lsm.py -i "+params.map+" -o "+params.lsm
	o, e = lib.shrun(c)
	tout = selfcal(params) 
	#print 'Selfcal Output Using LSM:'
	#print ("\n".join(map(str, tout[0])))


#global params
	
def iteri(lpars, i, tag=''):
	lpars.map = lpars.output_path+lpars.vis+'_'+tag+'_map'+str(i)
	lpars.beam = lpars.output_path+lpars.vis+'_'+tag+'_beam'+str(i)
	lpars.mask = lpars.output_path+lpars.vis+'_'+tag+'_mask'+str(i)
	lpars.model = lpars.output_path+lpars.vis+'_'+tag+'_model'+str(i)
	lpars.image = lpars.output_path+lpars.vis+'_'+tag+'_image'+str(i)
	lpars.lsm = lpars.output_path+lpars.vis+'_'+tag+'_lsm'+str(i)
	lpars.residual = lpars.output_path+lpars.vis+'_'+tag+'_residual'+str(i)

def mkim0(settings, lpars):
	'''
	Makes the 0th image.
	'''
	invout = invertr(settings, lpars)
	immax, imunits = getimmax(lpars.map)
	make_mask(lpars.map, immax/float(lpars.c0), lpars.mask)
	lpars.cutoff = get_cutoff(settings.get('obsrms'), cutoff=immax/float(lpars.c0))
	clean(lpars)
	restor(lpars)


class selfcal_main(threading.Thread):
	def __init__(self, vis, settings):
		threading.Thread.__init__(self)
		# NOTE: Now params is just the mpars defined below, which is a unit of spars. I use
		# the name params to disambiguate it from mpars.
		self.vis = vis
		# NOTE: settings is attached to the config file and contains all the generic
		# information.
		self.settings = settings

	def run(self):
		'''
		This is the selfcal engine that gets farmed out to multiple threads. 
		'''
		# TODO: Need to make a new directory for the outputs  
		settings = self.settings
		params = settings.get('selfcal_multi')
		params.vis = self.vis
		print "SelfCal on "+params.vis+' in this thread'

		# NOTE: Setup Output Directory and move to the directory that contains all the
		# visibilities.
		output_path = settings.full_path(params.pointing+'/'+params.vis+"_sc")
		lib.mkdir(output_path)
		params.output_path = params.vis+"_sc/" 
		working_path = settings.full_path(params.pointing+'/')
		os.chdir(working_path)
		# Now - we will dump the results in whatever path we're in.

		if lib.str2bool(params.mkim0)!=False:
			iteri(params, i=0)
			image_cycle(settings, params)
			sys.exit(0) # Perhaps this is the most appropriate?
		else:
			#NOTE: This seemingly defunct piece of code is necessary for vizquery to have a
			#reference.
			iteri(params, i=0)
			mkim0(settings, params)
		
		# Use PyBDSM. Deprecated. DO NOT USE!
		if lib.str2bool(params.bdsm)!=False:
			params.lsm = params.vis+'_bdsm'
			print 'Using PyBDSM to make LSM'
			bdsm(params)
		
		#NOTE: Use the NVSS as the LSM. Not always successful. 
		if lib.str2bool(params.nvss)!=False:
			params.lsm = params.vis+'_lsm'
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
				image_cycle(settings, params, j=i+1)
				selfcal_out = selfcal(params.vis, settings) 
		
			#NOTE: Make the final image after selfcal, using the mask and cutoffs from the last run.
			iteri(params, i='', tag='final')
			image_cycle(settings, params, j=i+1)

def selfcal_multi(settings):
	'''
	Main module that controls the multi-threaded selfcal. 

	selfcal_main(settings), where settings is grabbed from a config file through:
	settings = apercal.lib.settings('someconfigfile.txt')
	'''
	logger  = logging.getLogger('selfcal_multi')
	logger.setLevel(logging.DEBUG)
	# NOTE: The script parameters, spars, are grabbed here and used throughout the script.
	spars = settings.get('selfcal_multi')
	nt = 0
	if lib.str2bool(spars.imall)!=False:
		print "Making Wide Band Image..."
		spars.line=""
		#NOTE: Increase the CLEAN depth by the nominal increase in sensitivity.
		spars.dc = float(spars.dc) * pl.sqrt(8.)
		#NOTE: Increase the BW
		spars.bw = float(spars.bw) * 8.
		for i in range(0,int(spars.nloops)):
			print "Loop=", str(i)
			iteri(spars, i=i+1)
			image_cycle(settings, spars, j=i+1)
		print "Completed Wide Band Image"
		sys.exit(0)

	spars.nloops = int(spars.nloops)
	THREADS = []
	
	for v in spars.vis.split(','):
		# NOTE: Here we make the new directory and move to it. 
		if lib.str2bool(spars.cleanup)!=False:
			o, e = lib.shrun("rm -r "+v+"/gains")
			o, e = lib.shrun("rm -r "+v+"_*")
		logger.info("Assigned Thread "+str(nt)+" for "+v)
		nt+=1
		# NOTE: Now mpars only exists in this for loop, and is reserved for the
		# farming of the threads. It is a copy of spars 
		#mpars = spars
		#mpars.vis = v 
		#mpars.tag = v
		THREADS.append(selfcal_main(v, settings))
		time.sleep(1)
	for T in THREADS:
		logger.info("Starting "+str(T))
		T.start()
	
	for T in THREADS:
		time.sleep(1)
		logger.info("Joining "+ str(T))
		T.join()

	logger.info("DONE.")

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
		selfcal_multi(params)
