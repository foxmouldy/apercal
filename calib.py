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

def invert(settings, fname):
	invert = mirexec.TaskInvert()
	invert.vis = settings.name
	invert.map = settings.map
	invert.beam = settings.beam
	invert.imsize = settings.imsize;
	invert.cell = settings.cell;
	invert.options=settings.invert_options;
	invert.robust = settings.robust;
	tout = invert.snarf()
	acos.taskout(invert, tout, fname);

def clean(settings, fname):
	clean = mirexec.TaskClean()
	clean.map = settings.map;
	#clean.region = settings.clean_region;
	clean.beam = settings.beam;
	clean.out = settings.model;
	clean.cutoff = round(settings.cutoff, 10);
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
	settings.gt = round(settings.gt,10);
	maths = mirexec.TaskMaths();
	maths.exp = settings.image;
	maths.mask = settings.image+'.gt.'+str(settings.gt);
	maths.out = settings.mask;
	#maths.region=settings.clean_region;
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
	clean.cutoff = settings.cutoff;
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
	selfcal.interval = settings.selfcal_interval;
	selfcal.select = settings.selfcal_settings;
	tout = selfcal.snarf();
	acos.taskout(selfcal, tout, fname);

def iofits(I, O):
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
	cmd = 'rm -r '+O;
	os.system(cmd);
	cmd = 'mv _tmp_vis '+O;
	os.system(cmd);
	flags = ['auto', 'shadow(25)', 'an(6)'];
	for f in flags:
		uvflag = mirexec.TaskUVFlag();
		uvflag.vis = O;
		uvflag.select = f; #'auto,or,shadow(27),or,ant(6)';
		uvflag.flagval = 'flag';
		tout = uvflag.snarf();
		acos.taskout(uvflag, tout, 'uvflag.txt')
	print "Done."

def exfits(I, O):
	'''
	Reads in the 
	'''
	print "Exporting "+I+" to "+O;
	fits = mirexec.TaskFits();
	fits.in_ = I;
	fits.out = O;
	fits.op = 'uvout';
	tout = fits.snarf();
	acos.taskout(fits, tout, 'fits.txt');
	


def calcals(cals):
	mfcal = mirexec.TaskMfCal();
	for c in cals:
		mfcal.vis = c;
		mfcal.interval = 1000000.;
		tout = mfcal.snarf();
		acos.taskout(mfcal, tout, 'mfcal.txt');
		print "MFCAL Done on "+c;
	
def cal2srcs(cals, srcs):
	'''
	Cals = 'cal1,cal2'
	Srcs = 'src1,src2'
	'''
	#cals = cals.split(',');
	#srcs = srcs.split(',');
	# uvcat on src files
	if os.path.exists(srcs[2])==False:
	#try:
	#	with open(srcs[2]):
	#		isthere=True;
	#except IOError:
	#	isthere=False;
	#
	#if isthere==False:
		uvcat = mirexec.TaskUVCat();
		uvcat.vis = srcs[0]+','+srcs[1];
		uvcat.out = srcs[2];
		uvcat.options='unflagged';
		tout = uvcat.snarf();
		acos.taskout(uvcat, tout, 'cal2srcs.txt');
	

	# puthd on src
	puthd = mirexec.TaskPutHead();
	puthd.in_ = srcs[2]+'/restfreq';
	puthd.value = 1.420405752;
	tout = puthd.snarf();
	acos.taskout(puthd, tout, 'cal2srcs.txt');
	
	puthd.in_ = srcs[2]+'/interval'
	puthd.value = 1.0
	puthd.type = 'double'
	tout = puthd.snarf();
	acos.taskout(puthd, tout, 'cal2srcs.txt');

	# gpcopy cal1 -> src
	gpcopy  = mirexec.TaskGPCopy();
	gpcopy.vis = cals[0];
	gpcopy.out = srcs[2];
	tout = gpcopy.snarf();
	acos.taskout(gpcopy, tout, 'cal2srcs.txt');
	
	# gpcopy cal2 -> src
	#gpcopy  = mirexec.TaskGPCopy();
	#gpcopy.vis = cals[1];
	#gpcopy.out = srcs[2];
	#gpcopy.mode = 'merge'; 
	#gpcopy.options = 'nopass';
	#tout = gpcopy.snarf();
	#acos.taskout(gpcopy, tout, 'cal2srcs.txt');

def specr(f, S):
	'''
	Uses uvaver to cut-out a spectral range. 
	'''
	uvaver = mirexec.TaskUVAver();
	uvaver.vis = f; 
	uvaver.line = S.line;
	uvaver.out = '_tmp_specr'
	tout = uvaver.snarf();
	os.system('rm -r '+f);
	os.system('mv _tmp_specr '+f)
	acos.taskout(uvaver, tout, 'uvaver.txt');
