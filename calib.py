import re
import aplpy
import mirexec
from mirexec import *
import sys 
import pylab as pl
import os 

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
	TaskInvert(vis = U['vis'], map = U['map'], beam = U['beam'], imsize =
		U['imsize'], cell = U['cell'], options = U['invert_options']).run();

def make_clean(U):
	TaskClean(map = U['map'], beam = U['beam'], out = U['model'], cutoff =
		U['cutoff'], niters = U['niters']).run();
	TaskRestore(model = U['model'], beam = U['beam'], map = U['map'], 
		mode = 'residual', out = U['out']+'.res').run()
	TaskRestore(model = U['model'], beam = U['beam'], map = U['map'], 
		out = U['out']).run()

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
