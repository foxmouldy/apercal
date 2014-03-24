from apercal import mirexecb
from optparse import OptionParser 
import sys
import os

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--cals", '-c', type='string', dest = 'cals', default=None,
	help = 'Comma separated list of calibrator visiblities to do mfcal and to copy over solutions and to apply Tsys [None]')
parser.add_option('--refant', '-r', type='int', dest='refant', default=1, 
	help = 'Reference antenna')
(options, args) = parser.parse_args();

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);

def mfcal(v, refant):
	mfcal = mirexecb.TaskMfCal();
	mfcal.vis = v; 
	mfcal.refant = refant;
	mfcal.interval = 100000;
 	o = mfcal.snarf();
	print o; 

def gpcopy(v):
	gpcopy = mirexecb.TaskGPCopy();
	for i in range(len(v)-1):
		gpcopy.vis = v[i];
		gpcopy.out = v[0];
		gpcopy.options = 'nopass';
		gpcopy.merge = 'nopass';
		o = gpcopy.snarf();
		print o

if __name__=="__main__":
	for c in options.cals.split(','):
		mfcal(c, options.refant);
	if len(options.cals)>1.:
		gpcopy(options.cals.split(','));
