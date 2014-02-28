import sys
from tasks import *
from taskinit import *
import casac
import pylab as pl
import os
from optparse import OptionParser
import subprocess

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

# O1 for Option 
parser.add_option("--vis", "-v", type = 'string', dest = 'vis', default=None, 
	help = 'CSV List of input vis files [None]');
parser.add_option("--file", "-f", type='string', dest='file', default=None,
	help = "File to print the output [None]");
parser.add_option('-w', action='store_true', dest='verbose', default=False,
	help = 'Use ms2uvfits to write the data to UVF [False]')

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

def getfields(vis):
	visheader = vishead(vis=vis, mode='list');
	return visheader['field'][0];

def ms2uv(msfile, uvfile):
	os.system('ms2uvfits ms='+msfile+' fitsfile='+uvfile+' writesyscal=T multisource=T combinespw=T');


if __name__=="__main__":
	towrite = [];
	vises = options.vis.split(',');
	for v in vises:
		fields = getfields(v);
		towrite.append(v+'\n');
		for f in fields:
			towrite.append(f+',');
		towrite.append('\n')
		if options.verbose==True:
			ms2uv(v, v.replace('.MS', '.UVF'));
	if options.file!=None:
		F = open(options.file, 'a');
		for tw in towrite:
			F.writelines(tw);
		F.close();
	else:
		for tw in towrite:
			print tw;
