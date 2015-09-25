from apercal import mirexecb
from optparse import OptionParser 
import sys
import os

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--cal", '-c', type='string', dest = 'cal', default=None,
	help = 'Calibrator over which to copy over solutions [None]')
parser.add_option("--srcs", '-s', type='string', dest = 'srcs', default=None,
	help = 'Comma separated source uv files for which the calibrators should be copied. [None]')

(options, args) = parser.parse_args();

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);

def cal2srcs(cal, srcs):
	'''
	Cals = 'cal1,cal2'
	Srcs = 'src1,src2'
	'''
	for s in srcs.split(','):
		puthd = mirexecb.TaskPutHead();
		puthd.in_ = s+'/restfreq';
		puthd.value = 1.420405752;
		o = puthd.snarf();
		print o;
		
		puthd.in_ = s+'/interval'
		puthd.value = 1.0
		puthd.type = 'double'
		o = puthd.snarf();
		print o; 
	
		gpcopy  = mirexecb.TaskGPCopy();
		gpcopy.vis = cal;
		gpcopy.out = s;
		o = gpcopy.snarf();
		print o; 

if __name__=="__main__":
	cal2srcs(options.cal, options.srcs);
