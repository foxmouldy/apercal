import mirexec
from optparse import OptionParser
import sys
import os

usage = "usage: %prog options"
parser = OptionParser(usage=usage);
# O1 for Option 
parser.add_option("--image", type = 'string', dest = 'imname', default=None, 
	help = 'Name of Image');
parser.add_option("--vis", "-v", type = 'string', dest = 'vis', default=None, 
	help = "Vis to be selfcal'd [None]");
parser.add_option("--select", type = 'string', dest='select', default='', 
	help = 'UV selection [None]');
parser.add_option('--tag', '-t', type='string', dest='tag', default='', 
	help = 'Naming tag to be carried [None]')
parser.add_option('--defmcut', '-d', type='string', dest='defmcut', default='1e-2',
	help = 'Default Cutoff for Masking, used if nan is returned as max [1e-2]')
parser.add_option('--mode', '-m', type='string', dest='mode', default='selfcalr',
	help = "Mode of Selfcal, either phase-selfcal [pselfcalr] or amp-selfcal (aselfcalr)")
parser.add_option('--ergs', '-e', type='string', dest='ergs', default='',
	help = "Extra arguments to be passed to the functions.")
(options, args) = parser.parse_args();

def getimmax(imname):
	imstat = mirexec.TaskImStat()
	imstat.in_ = imname;
	imstats = imstat.snarf();
	#print imstats;
	immax = float(imstats[0][10][51:61]);
	imunits = imstats[0][4];
	return immax, imunits

def invertr(vis, select, mapname, beamname):
	invert = mirexec.TaskInvert()
	invert.vis = vis;
	invert.select = select;
	os.system('rm -r '+mapname)
	os.system('rm -r '+beamname)
	invert.map = mapname
	invert.beam = beamname
	invert.options = 'double,mfs';
	invert.slop = 0.5
	invert.stokes = 'ii'
	invert.imsize = 1500
	invert.cell = 4
	invert.robust= -2
	tout = invert.snarf();

def clean(mapname, beamname, modelname, maskname=None, cutoff=0.0):
	clean = mirexec.TaskClean()
	clean.map = mapname;
	clean.beam = beamname;
	clean.cutoff = cutoff;
	if maskname!=None:
		clean.region='mask('+maskname+')';
		clean.niters = 10000000
	else:
		clean.niters = 1000
	os.system('rm -r '+modelname);
	clean.out = modelname; 
	tout = clean.snarf()

def dclean(vis, mapname, beamname, modelname):
	clean = mirexec.TaskClean()
	clean.map = mapname;
	clean.beam = beamname;
	clean.niters = 100000000
	os.system('rm -r '+modelname);
	clean.out = modelname; 
	tout = clean.snarf()

def restor(mapname, beamname, modelname, imname):
	os.system('rm -r '+imname)
	restor = mirexec.TaskRestore()
	restor.beam = beamname;
	restor.map = mapname
	restor.model = modelname
	restor.out = imname
	tout = restor.snarf()

def maths(imname, cutoff, maskname):
	os.system('rm -r '+maskname);
	maths = mirexec.TaskMaths()
	maths.exp = imname;
	maths.mask = imname+'.gt.'+str(cutoff);
	maths.out = maskname;
	tout = maths.snarf()

def selfcal(vis, select, modelname, interval=1.0, so = 'mfs,phase'):
	selfcal = mirexec.TaskSelfCal();
	selfcal.vis = vis; 
	selfcal.select = select;
	selfcal.model = modelname;
	selfcal.options = so;
	selfcal.interval = interval;
	tout = selfcal.snarf()

#def pselfcalr(options, mapname, beamname, imname, modelname, maskname, so='mfs,phase', interval='1'):
def pselfcalr(options, so='mfs,phase', interval='1'):
	mapname = options.vis+options.tag+'.map'
	beamname = options.vis+options.tag+'.beam'
	imname=options.vis+options.tag+'.image';
	modelname = options.vis+options.tag+'.model'
	maskname = options.vis+options.tag+'.mask'

	imager(options.vis, options.select, mapname, beamname, imname, modelname, maskname=maskname, cutoff=0.0);
	immax, imunits = getimmax(imname);
	if str(immax)=='nan':
		immax = float(options.defmcut);
	maths(imname, immax/10, maskname);
	imager(options.vis, options.select, mapname, beamname, imname, modelname, maskname=maskname, cutoff=immax/30.);
	#immax, imunits = getimmax(imname);
	#if str(immax)=='nan':
	#	immax = options.defmcut;
	#maths(imname, immax/20., maskname);
	#imager(options.vis, options.select, mapname, beamname, imname, modelname, maskname=maskname, cutoff=immax/60.);
	selfcal(options.vis, options.select, modelname, so=so, interval=interval);
	imager(options.vis, options.select, mapname, beamname, imname, modelname, maskname=maskname, cutoff=immax/60.);
	uvcatr(options.vis)

#def aselfcalr(options, mapname, beamname, imname, modelname, maskname, so='mfs,amp', interval='100000'):
def aselfcalr(options, so='mfs,amp', interval='100000'):
	mapname = options.vis+options.tag+'.map'
	beamname = options.vis+options.tag+'.beam'
	imname=options.vis+options.tag+'.image';
	modelname = options.vis+options.tag+'.model'
	maskname = options.vis+options.tag+'.mask'

	imager(options.vis, options.select, mapname, beamname, imname, modelname, maskname=maskname, cutoff=0.0);
	immax, imunits = getimmax(imname);
	if str(immax)=='nan':
		immax = float(options.defmcut);
	maths(imname, immax/10, maskname);
	imager(options.vis, options.select, mapname, beamname, imname, modelname, maskname=maskname, cutoff=immax/30.);
	immax, imunits = getimmax(imname);
	#if str(immax)=='nan':
	#	immax = options.defmcut;
	#maths(imname, immax/20., maskname);
	#imager(options.vis, options.select, mapname, beamname, imname, modelname, maskname=maskname, cutoff=immax/60.);
	selfcal(options.vis, options.select, modelname, so=so, interval=interval);
	imager(options.vis, options.select, mapname, beamname, imname, modelname, maskname=maskname, cutoff=immax/60.);
	uvcatr(options.vis)
	
def uvcatr(fname):
	uvcat = mirexec.TaskUVCat()
	uvcat.vis = fname
	uvcat.out = fname+'.tmp'
	print	'Writing in Gains for '+str(fname)
	uvcat.snarf()
	print 	'Deleting Temp File'
	os.system('rm -r '+fname)
	os.system('mv '+fname+'.tmp '+fname)

#

def imager(vis, select, mapname, beamname, imname, modelname, maskname='', cutoff=0.0):
	invertr(vis, select, mapname, beamname);
	clean(mapname, beamname, modelname)
	restor(mapname, beamname, modelname, imname);
	immax, imunits = getimmax(imname);
	maths(imname, immax/10, maskname);
	clean(mapname, beamname, modelname, maskname, cutoff)
	restor(mapname, beamname, modelname, imname);


if __name__=="__main__":
	if len(sys.argv)==1: 
		parser.print_help();
		dummy = sys.exit(0);
	#mapname = options.vis+options.tag+'.map'
	#beamname = options.vis+options.tag+'.beam'
	#imname=options.vis+options.tag+'.image';
	#modelname = options.vis+options.tag+'.model'
	#maskname = options.vis+options.tag+'.mask'
	#print options
	cmd = options.mode+'(options, '+options.ergs+')'
	print cmd
	#sys.exit(0)
	#selfcalr(options, mapname, beamname, imname, modelname, maskname);
	print cmd
	exec(cmd)
