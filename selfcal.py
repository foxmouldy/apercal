import mirexec
import pylab as pl
from optparse import OptionParser
import sys
import os
from ConfigParser import SafeConfigParser
import imp

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
parser.add_option("--settings", "-s", type = 'string', dest='settings', default=None, 
	help = 'Settings file to be used [None]')
parser.add_option('--lsm', '-l', action='store_true', dest='lsm', default=False,
	help = "Use LSM for calibration [False]")
parser.add_option('--nloops', '-n', type='int', dest='n', default=0, 
	help = 'Number of Selfcal Loops [0]')
parser.add_option('--bdsm', '-b', action='store_true', dest='bdsm', default=False, 
	help = 'Use PyBDSM to create Gaussian LSM0 [False]')
parser.add_option('--mkim0', '-m', action='store_true', dest='mkim0', default=False, 
	help = 'MFS-Image the VIS and exit [False].')
parser.add_option('--par', '-p', type='string', dest='par', default=None, 
	help = 'Overwrite a single parameter: --par <par>:<value>;<par2>:<value2>')

(options, args) = parser.parse_args();

if __name__=="__main__":
	if len(sys.argv)==1: 
		parser.print_help();
		dummy = sys.exit(0);

options.n = int(options.n)

class Bunch: 
	def __init__(self, **kwds): 
		self.__dict__.update(kwds)

def getimmax(image):
	imstat = mirexec.TaskImStat()
	imstat.in_ = image;
	imstats = imstat.snarf();
	immax = float(imstats[0][10][51:61]);
	imunits = imstats[0][4];
	return immax, imunits

def invertr(params):
	invert = mirexec.TaskInvert()
	invert.vis = params.vis
	invert.select = params.select
	invert.line = params.line
	os.system('rm -r '+params.map)
	os.system('rm -r '+params.beam)
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
	return tout

def clean(params):
	clean = mirexec.TaskClean()
	clean.map = params.map
	clean.beam = params.beam
	clean.cutoff = params.cutoff
	if params.mask!=None:
		clean.region='mask('+params.mask+')'
		clean.niters = 10000000
	else:
		clean.niters = 1000
	os.system('rm -r '+params.model)
	clean.out = params.model 
	tout = clean.snarf()

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

	os.system('rm -r '+restor.out)
	tout = restor.snarf()
	
def maths(image, cutoff, mask):
	os.system('rm -r '+mask)
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
	if params.clip!=None:
		selfcal.clip = params.clip
	tout = selfcal.snarf()
	return tout

def wgains(params):
	uvcat = mirexec.TaskUVCat()
	uvcat.vis = params.vis
	uvcat.out = '.temp'
	tout = uvcat.snarf()
	os.system('rm -r '+params.vis)
	os.system('mv .temp '+params.vis)

def get_cutoff(rms=1e-3, fac=2., imax=1e-2, invout=None):
	'''
	Simple function to calculate the cutoff
	'''
	# invout is the text array from invert.
	if invout!=None:
		rmstr = [s for s in invout[0] if 'Theoretical rms noise:' in s]
		noise = 3.*float(str(rmstr[0]).split(':')[1])
	else:
		noise = 5.*float(rms)
	if imax/fac > noise:
		return imax/fac
	else:
		return noise

#def selfcal_cycle(j=1):
def image_cycle(j=1):
	c1 = pl.linspace(3.,9.,3.)*(j*4.)
	c2 = c1/10.
	#c2 = pl.linspace(3.,9.,3.)*j
	invout = invertr(params)
	immax, imunits = getimmax(params.map)
	maths(params.map, immax/c1[0], params.mask)
	params.cutoff = get_cutoff(invout = invout, fac=c2[0])
	clean(params)
	restor(params)
	immax, imunits = getimmax(params.image)
	maths(params.image, immax/c1[1], params.mask)
	params.cutoff = get_cutoff(invout = invout, fac=c2[1])
	clean(params)
	restor(params)
	immax, imunits = getimmax(params.image)
	maths(params.image, immax/c1[2], params.mask)
	params.cutoff = get_cutoff(invout = invout, fac=c2[2])
	clean(params)
	restor(params)
	cmmax, cmunits = getimmax(params.model)
	params.clip = cmmax/(100.*j)
	restor(params, mode='residual')
	# Selfcal
	#tout = selfcal(params) 
	#print 'Selfcal Output:'
	#print ("\n".join(map(str, tout[0])))



def bdsm():
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
	print params
	sys.exit(0)
	tout = selfcal(params)
	print 'Selfcal Output Using PyBDSM:'
	print ("\n".join(map(str, tout[0])))


def lsm():
	c = "python mk-nvss-lsm.py -i "+params.map+" -o "+params.lsm
	os.system(c)
	print 'Made LSM'
	params.model = params.lsm
	params.sopts='mfs,phase'
	params.interval='5'
	tout = selfcal(params) 
	print 'Selfcal Output Using LSM:'
	print ("\n".join(map(str, tout[0])))


global params
	
def iteri(i):
	params.map = params.tag+'_map'+str(i)
	params.beam = params.tag+'_beam'+str(i)
	params.mask = params.tag+'_mask'+str(i)
	params.model = params.tag+'_model'+str(i)
	params.image = params.tag+'_image'+str(i)
	params.lsm = params.tag+'_lsm'+str(i)
	params.residual = params.tag+'_residual'+str(i)


# Setup the parameters 
params = Bunch(vis=options.vis, select='-uvrange(0,1)', tag = 'sc', map='map_temp', beam='beam_temp', 
	mask = 'mask_temp', model='model_temp', image = 'image_temp', residual = 'residual_temp', robust='-2.0',
	lsm='lsm_temp', line='channel,900,1,1,1', sopts='mfs,phase', iopts='mfs,double', interval=5,
	fwhm='', cutoff=1e-2, clip=None)

if options.par!=None:
	pars = options.par.split(';')
	for par in pars:
		p = par.split(':')	
		setattr(params, p[0], p[1])

# Make the initial image.

def mkim0():
	'''
	Makes the 0th image.
	'''
	print "Making Initial Image"
	invout = invertr(params)
	immax, imunits = getimmax(params.map)
	maths(params.map, immax/3, params.mask)
	params.cutoff = get_cutoff(invout = invout, fac=4)
	clean(params)
	restor(params)

if options.mkim0!=False:
	iteri(i=0)
	mkim0()
	sys.exit(0)
else:
	iteri(i=0)
	mkim0()

if options.bdsm!=False:
	params.lsm = params.tag+'_bdsm'
	print 'Using PyBDSM to make LSM'
	bdsm()

if options.lsm!=False:
	params.lsm = params.tag+'_lsm'
	params.model = params.lsm
	print 'Making LSM'
	lsm()

R = [] # Ratio of actual to theoretical noise

if options.n!=0:
	for i in range(0, options.n):
		print 'Selfcal Cycle '+str(i+1)
		iteri(i+1)
		image_cycle(j=i+1)
		tout = selfcal(params) 
		'Selfcal Output: '+str(i+1)
		print ("\n".join(map(str, tout[0])))
		ratstr = [s for s in tout[0] if 'Ratio of Actual to Theoretical noise:' in s]
		R.append(float(str(ratstr[0]).split(':')[1]))

	R = pl.array(R)
	pl.plot(R, 'k-', lw=2)
	pl.xlabel("Run #")
	pl.ylabel("Ratio of Actual to Theoretical Noise")
	pl.savefig(params.tag+'.scratio.pdf', dpi=300)
	pl.close()
	# Make the final image after selfcal
	otag = params.tag
	params.tag+='_asc'
	iteri(i='')
	image_cycle(j=i+1)	
