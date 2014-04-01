from apercal import mirexecb
from optparse import OptionParser 
import sys
import os

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--vises", '-v', type='string', dest = 'vis', default='*.UV',
	help = 'UV Wildcard for merging and splitting [None]')
parser.add_option('--srcs', '-s', type='string', dest = 'srcs', default=None, 
	help = 'Comma separated list of sources to be merged and split [None]')

(options, args) = parser.parse_args();

def mergensplit(vis, src):
	uvcat = mirexecb.TaskUVCat();
	uvcat.vis = vis;
	uvcat.select='source('+src+')';
	uvcat.out = src+'.UV'
	o = uvcat.snarf();

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);

if __name__=="__main__":
	for src in options.srcs.split(','):
		mergensplit(options.vis, src);
