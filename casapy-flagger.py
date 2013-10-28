import sys
from tasks import *
from taskinit import *
import casac
import pylab as pl
import os
from optparse import OptionParser

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

# O1 for Option 
parser.add_option("--uvfiles", "-u", type = 'string', dest = 'uvfiles', default=None, 
	help = 'CSV List of input UV files');

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

uvfiles = options.uvfiles.split(',');
spw = '0:300~600';

for u in uvfiles:
	vis = u.replace('.UVF', '.MS');
	uvfitsout = u.replace('.UVF','.UVfl')
	#1 First, import the uvfits file. 
	importuvfits(fitsfile=u, vis=vis);
	
	#2 Flag the autocorrelations.
	flagdata(vis=vis, mode='manual', spw=spw, autocorr=True);
	
	#3 Run the tfcrop on the MS
	flagdata(vis=vis, mode='tfcrop', spw=spw);

	#4 Export the new uvfits file
	exportuvfits(vis=vis, fitsfile=uvfitsout, spw=spw);

