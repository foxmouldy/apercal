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

parser.add_option("--spw", "-s", type = 'string', dest = 'spw', default=None, 
	help = 'Spectral window to extract for work. ');

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

uvfiles = options.uvfiles.split(',');
spw = '0:600~900';

for u in uvfiles:
	vis = u.replace('.muvfits', '.MS');
	uvfitsout = u.replace('.muvfits','.uvfl')
	#1 First, import the uvfits file. 
	importuvfits(fitsfile=u, vis=vis);
	
	#2 Flag the autocorrelations.
	flagdata(vis=vis, mode='manual', spw=spw, autocorr=True);
	
	#3 Run the tfcrop on the MS
	flagdata(vis=vis, mode='tfcrop', spw=spw);

	#4 Export the new uvfits file
	exportuvfits(vis=vis, fitsfile=uvfitsout, spw=spw);

