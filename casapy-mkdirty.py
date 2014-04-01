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
parser.add_option("--vis", "-v", type = 'string', dest = 'vis', default=None, 
	help = 'CSV List of input vis files');

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

def mkdirty(vis, field, niter=0, imsize=1050, cell='4.0arcsec', weighting='briggs',
robust=-2., spw='0', mode='mfs'):
	imagename=vis.replace('.MS', '_f'+field+'_spw'+spw+'.dirty');
	clean(vis=vis, field=field, imagename=imagename,
		niter=niter, imsize=imsize, cell=cell, weighting=weighting, 
		robust=robust, spw=spw, mode=mode);
	return imagename;

def cleanup(tag):
	os.system('rm -r '+tag+'.flux');
	os.system('rm -r '+tag+'.model');
	os.system('rm -r '+tag+'.residual');

def getfields(vis):
	visheader = vishead(vis=vis, mode='list');
	return visheader['field'][0];

if __name__ == "__main__":
	for v in options.vis.split(','):
		print "mkdirty --> "+v; 
		fields = getfields(v);
		for f in fields:
			print "Field: "+f;
			tag = mkdirty(vis=v, field=f);
			cleanup(tag);
