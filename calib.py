import re
import aplpy
#import mirexec
#from mirexec import *
import sys 
import pylab as pl
import os 
import imp
import acos

try:
	imp.find_module('mirexec');
	found = True;
except ImportError:
	found = False;
if found:
	from mirexec import *
	import mirexec


def tkout(key, mirtout):
	'''
	Returns the value for a [key] and miriad task output [mirtout].
	If a miriad task is run from miriad-python as 
	$ mirtout = task.snarf() 
	we can extract a value corresponding to the [key] from the
	[mirtout] output.
	The output is a dictionary corresponding to the input [key], and
	should be handled appropriately.
	
	!!! This is costly in terms of performance, since it loops over
	every line of [mirtout] in order to grab the matching line. 
	'''
	for i in range(len(mirtout[0])):
		if re.search(key, mirtout[0][i]):
			l = mirtout[0][i];
			l = dict(u.split(":") for u in l.split(","));
			print l;	
	return l;

def implot(imfile, plot):
	'''
	Uses aplpy and the fits task to make a simple plot of the image
	[imfile]

	!!! Converts the miriad file to a fits file, plots it and then
	deletes the fits file!
	'''
	t = mirexec.TaskFits();
	t.in_ = imfile;
	t.out = imfile+'_temp.fits';
	t.op = 'xyout';
	if not os.path.exists(t.out):
		tout = t.snarf();
	f = aplpy.FITSFigure(t.out, dimensions=[0,1], slices=[0,0]);
	f.show_colorscale();
	os.system('rm '+t.out);
	if plot: 
		pl.savefig(plot);

def scal(U):
	tout = TaskSelfcal(vis = U.vis, select = U.sc_select, model = U.sc_model,
		options = U.sc_options).snarf();
	return tout;

def make_dirty(U):
	tout = TaskInvert(vis = U['vis'], map = U['map'], beam = U['beam'], imsize =
		U['imsize'], cell = U['cell'], options = U['invert_options']).snarf();
	return tout;


def read_inps(fname):
	'''
	This reads in the inputs from the text file fname. Each line in the text file should
	contain the desired user-input. For example:
	spw = 0:100~200
	will produce ui['spw'] = '0:100~200'
	'''
	f = open(fname, 'r');
	U = {};
	for line in f:
		k,v = line.strip().split('=');
		U[k.strip()] = v.strip();
	f.close();
	return(U);

def invert(settings, fname):
	invert = mirexec.TaskInvert()
	invert.vis = settings.name
	invert.map = settings.map
	invert.beam = settings.beam
	invert.imsize = settings.imsize;
	invert.cell = settings.cell;
	invert.options=settings.invert_options;
	tout = invert.snarf()
	acos.taskout(invert, tout, fname);

def clean(settings, fname):
	clean = mirexec.TaskClean()
	clean.map = settings.map;
	clean.beam = settings.beam;
	clean.out = settings.model;
	clean.cutoff = round(settings.cutoff, 6);
	clean.niters = settings.niters;
	tout = clean.snarf()
	acos.taskout(clean, tout, fname);

def restorim(settings, fname, mode='clean'):
	restor = mirexec.TaskRestore();
	restor.model = settings.model;
	restor.map = settings.map;
	restor.beam = settings.beam;
	restor.out = settings.image;
	restor.mode = mode;
	tout = restor.snarf();
	acos.taskout(restor, tout, fname);

def restores(settings, fname, mode='residual'):
	restor = mirexec.TaskRestore();
	restor.model = settings.model;
	restor.map = settings.map;
	restor.beam = settings.beam;
	restor.out = settings.res;
	restor.mode = mode;
	tout = restor.snarf();
	acos.taskout(restor, tout, fname);

def maths(settings, fname):
	settings.gt = round(settings.gt,6);
	maths = mirexec.TaskMaths();
	maths.exp = settings.image;
	maths.mask = settings.image+'.gt.'+str(settings.gt);
	maths.out = settings.mask;
	tout = maths.snarf();
	acos.taskout(maths, tout, fname);

def clean_deeper(settings, fname, df=3):
	'''
	Runs clean using the mask. The settings.cutoff is divided by df. 
	'''
	clean = mirexec.TaskClean()
	clean.map = settings.map;
	clean.beam = settings.beam;
	clean.region = 'mask('+settings.mask+')';
	clean.out = settings.m4s;
	clean.cutoff = round(settings.cutoff/df,6);
	clean.niters = settings.niters;
	tout = clean.snarf()
	acos.taskout(clean, tout, fname);

def imstat(image, fname):
	'''
	Performs imstat on settings.image
	'''
	imstat = mirexec.TaskImStat();
	imstat.in_ = image;
	tout = imstat.snarf();
	acos.taskout(imstat, tout, fname);

def selfcal(settings, fname):
	selfcal = mirexec.TaskSelfCal()
	selfcal.vis = settings.vis;
	selfcal.options = settings.selfcal_options;
	selfcal.model = settings.m4s;
	tout = selfcal.snarf();
	acos.taskout(selfcal, tout, fname);

def infits(I, O):
	'''
	Reads in the uvfits file I and exports it to the miriad-uv file O,
	using the carma-miriad task wsrtfits.
	'''
	cmd = 'wsrtfits in='+I+' out='+O+' op=uvin velocity=optbary';
	print "Import "+I+" -> "+O;
	os.system(cmd);
	print "Tsys Calibration on "+O;
	cmd = 'attsys vis='+O+' out=_tmp_vis';
	os.system(cmd);
	cmd = 'mv _tmp_vis '+O;
	os.system(cmd);
	uvflag = mirexec.TaskUVFlag();
	uvflag.vis = O;
	uvflag.select = 'auto,or,shadow(27),or,ant(6)';
	uvflag.flagval = 'flag';
	tout = uvflag.snarf();
	acos.taskout(uvflag, tout, 'uvflag.txt')
	print "Done."

def calcals(cals):
	mfcal = mirexec.TaskMfcal();
	for c in cals:
		mfcal.vis = c;
		mfcal.interval = 1000000.;
		tout = mfcal.snarf();
		acos.taskout(mfcal, tout, 'mfcal.txt');
		print "MFCAL Done on "+c;
		
