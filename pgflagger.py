import sys
import miriad
import mirexec
import mirexec2
import aplpy
import pylab as pl
import numpy
from apercal import calib
from apercal import acim
from apercal import acos
import os
from optparse import OptionParser 

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--vis", '-v', type='string', dest='vis', default=None,
	help = 'Visibility to be flagged.');
parser.add_option('--select', '-s', type='string', dest='select',
	default=None, help = 'Selection');
parser.add_option('--log', '-l', type='string', dest='log', default=None, 
	help='Log file in which to save the flagging results.')
parser.add_option('--stokes', type='string', dest='stokes', default='qq', 
	help='Stokes to operate on. [qq]');
parser.add_option('--flagpar', '--f', type='string', dest='flagpar', 
	default='2,10,20,10,5,3', help='Flagpar for SumThresholding [2,10,20,10,5,3]');
parser.add_option('--options', '-o', type='string', dest='options', 
	default='nodisp', help = 'PGFLAG options [nodisp].'); 

(options, args) = parser.parse_args();

if len(sys.argv)==1:
	# Run or Import
	if __name__=="__main__":
		print "pgflagger.py: This uses miriad's pgflag to perform SumThresholding on a visibility. "
		parser.print_help();
		dummy = sys.exit(0);

p2w = os.getcwd();

def pgflag(params):
	if params.log==None:
		# This default naming convention is a little clumsy, but at
		# least its clear what's happening here. 
		params.log = params.vis+'.pgflaglog.txt';
	pgflag = mirexec2.TaskPGFlag();
	pgflag.vis = params.vis;
	pgflag.select = params.select;
	pgflag.stokes = params.stokes; 
	pgflag.flagpar = params.flagpar;
	pgflag.options = params.options;
	
	# This specifies the SumThresholding command.
	pgflag.command = '<';
	tout = pgflag.snarf();
	acos.taskout(pgflag, tout, options.log)

# Run or Import
if __name__ == "__main__":
	pgflag(options);
