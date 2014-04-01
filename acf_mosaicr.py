from apercal import mirexecb
import os 
from optparse import OptionParser 
import sys
import os

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--tag", '-t', type='string', dest = 'tag', default=None,
	help = 'Source tag for the mosaic, e.g. ACF2G3 [None]')

(options, args) = parser.parse_args();

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);

def mosaicr(tag):
	mosdir = tag+'.IMOS';
	os.system('mkdir '+mosdir)
	linmos = mirexecb.TaskLinMos();#
	for w in range(1,9):
		infiles = '';
		for p in range(1,5):
			infiles += tag+'P'+str(p)+'.IM'+'/'+tag+'P'+str(p)+'W'+str(w)+'.IM,'
			outfile = mosdir+'/'+tag+'W'+str(w)+'.IM'
		linmos.in_ = infiles[0:-1];
		linmos.out = outfile;
		linmos.snarf();
		print "Mosaic'd "+outfile;

if __name__=="__main__":
	mosaicr(options.tag);
