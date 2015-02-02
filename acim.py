import re
import mirexec
from mirexec import *
import sys 
import pylab as pl
import os 

def implot(imname, vmin=None, vmax=None):
	'''
	Plots a single plane image using imshow. 
	'''
	pl.figure(figsize=(10,10))
	I = miriad.ImData(imname);
	I = I.open('rw');
	Iarr = I.readPlane()
	pl.imshow(Iarr, cmap='YlOrRd', vmin=vmin, vmax=vmax);
	pl.colorbar();
	I.close()
