import re
import aplpy
import mirexec
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
