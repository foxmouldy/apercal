import mirexec
from optparse import OptionParser
import sys
import os
from ConfigParser import SafeConfigParser

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--vis", "-v", type = 'string', dest = 'vis', default=None, 
	help = "Vis to be selfcal'd [None]");
parser.add_option("--settings", "-s", type = 'string', dest='settings', default=None, 
	help = 'Settings file to be used [None]')

(options, args) = parser.parse_args();

if __name__=="__main__":
	if len(sys.argv)==1: 
		parser.print_help();
		dummy = sys.exit(0);

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

def restor(params):	
	os.system('rm -r '+params.image)
	restor = mirexec.TaskRestore()
	restor.beam = params.beam
	restor.map = params.map
	restor.model = params.model
	restor.out = params.image
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

def wgains(params):
	uvcat = mirexec.TaskUVCat()
	uvcat.vis = params.vis
	uvcat.out = '.temp'
	tout = uvcat.snarf()
	os.system('rm -r '+params.vis)
	os.system('mv .temp '+params.vis)
# params should be replaced by a settings file. 



params = Bunch(vis=options.vis, select='-uvrange(0,1)', 
	map='map_temp', beam='beam_temp', mask = 'mask_temp', model='model_temp', image = 'image_temp', 
	robust='-2.0', lsm='lsm_temp', line='channel,60,2,1,1', sopts='mfs,phase',
	iopts='mfs,double', interval=5, fwhm='', cutoff=1e-2, clip=None)

# Calibration Using the LSM
params.map=params.vis.replace('.uv','')+'_'+params.map
params.beam=params.vis.replace('.uv','')+'_'+params.beam
params.mask=params.vis.replace('.uv','')+'_'+params.mask
params.model=params.vis.replace('.uv','')+'_'+params.model
params.image=params.vis.replace('.uv','')+'_'+params.image
params.lsm=params.vis.replace('.uv','')+'_'+params.lsm

#print "LSM Calibration"
#params.fwhm='45'
#params.robust='-1'
invertr(params)
#c = "python mk-nvss-lsm.py -i "+params.map+" -o "+params.lsm
#os.system(c)
print 'made lsm'
params.model = params.lsm
params.sopts='mfs,phase'
params.interval='1'
selfcal(params)
#wgains(params)
#params.fwhm='12'
#params.robust = '-1'
params.sopts='mfs,phase'
#params.interval='1'

# Selfcal 1
#print "Selfcal 1"
#params.model=params.vis.replace('.uv','')+'_model_temp'
#invertr(params)
#immax, imunits = getimmax(params.map)
#maths(params.map, immax/3, params.mask)
#params.cutoff = immax/10
#clean(params)
#restor(params)
#immax, imunits = getimmax(params.image)
#maths(params.image, immax/9, params.mask)
#params.cutoff=immax/100
#clean(params)
#restor(params)
#immax, imunits = getimmax(params.image)
#maths(params.image, immax/12, params.mask)
#params.cutoff=immax/100
#clean(params)
#restor(params)
#cmmax, cmunits = getimmax(params.model)
#params.clip = cmmax/20
#selfcal(params) 
#
## Selfcal 2
#print "Selfcal 2"
#invertr(params)
#immax, imunits = getimmax(params.map)
#maths(params.map, immax/3, params.mask)
#params.cutoff=immax/10
#clean(params)
#restor(params)
#immax, imunits = getimmax(params.image)
#maths(params.image, immax/9, params.mask)
#params.cutoff=immax/100
#clean(params)
#immax, imunits = getimmax(params.image)
#maths(params.image, immax/12, params.mask)
#params.cutoff=immax/100
#clean(params)
#restor(params)
#selfcal(params) 
#
## Selfcal 3
#print "Selfcal 3"
#invertr(params)
#immax, imunits = getimmax(params.map)
#maths(params.map, immax/3, params.mask)
#params.cutoff=immax/10
#clean(params)
#restor(params)
#immax, imunits = getimmax(params.image)
#maths(params.image, immax/9, params.mask)
#params.cutoff = immax/100
#clean(params)
#restor(params)
#immax, imunits = getimmax(params.image)
#maths(params.image, immax/12, params.mask)
#params.cutoff=immax/100
#clean(params)
#restor(params)
#selfcal(params)
#invertr(params)
#clean(params)
