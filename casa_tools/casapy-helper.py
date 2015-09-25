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
parser.add_option("--calls", "-c", type='string', dest='calls',
	default=None, help="Module to be run (flag, exportms) [None]")
parser.add_option("--files", "-f", type = 'string', dest = 'files', default=None, 
	help = 'CSV List of input UV files');

parser.add_option("--spw", "-s", type = 'string', dest = 'spw', default='0', 
	help = 'Spectral window to extract for work. ');

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

global files;
if options.files!=None:
	files = options.files.split(',');
else: 
	files=None;

global spw;
spw = options.spw;

def flag():
	if files==None:
		print "No files found. Please use the --files option to define the files to operate on. "
		sys.exit(0);
	else:
		print "flag: importuvfits->flagdata->exportuvfits"
		for u in files:
			ext = u.split('.')[1]
			vis = u.replace(ext, 'MS');
			uvfitsout = u.replace(ext,'.UVFl')
			#1 First, import the uvfits file. 
			importuvfits(fitsfile=u, vis=vis);
			
			#2 Flag the autocorrelations.
			flagdata(vis=vis, mode='manual', spw=spw, autocorr=True);
			
			#3 Run the tfcrop on the MS
			flagdata(vis=vis, mode='tfcrop', spw=spw);
		
			#4 Export the new uvfits file
			exportuvfits(vis=vis, fitsfile=uvfitsout, spw=spw);

def exportms():
	if files==None:
		print "No files found. Please use the --files option to define the files to operate on. "
		sys.exit(0);
	else:
		print "exportms: exportuvfits"
		for m in files:
			ext = m.split('.')[1];
			vis = m;
			fitsfile = m.replace(ext, '.uvfits2');
			datacolumn='data';
			exportuvfits(vis=vis, fitsfile=fitsfile, spw=spw);
			print "Exported "+vis+" to "+fitsfile;

if options.calls!=None:
	for c in options.calls.split(','):
		print "Running "+c+'\n';
		exec(c+'()');
else:
	print "You fail.\nPlease specify module to be run."
