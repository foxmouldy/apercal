import mirexecb 
import acos
import acim
import plot
import uvpltr
#import re
#import sys 
#import pylab as pl
#import os 
#from optparse import OptionParser 
#import calib
#
#usage = "usage: %prog options"
#parser = OptionParser(usage=usage);
#
#parser.add_option("--settings", "-s", type = 'string', dest = 'sfile', default=None,
#	help = 'Settings file');
#parser.add_option("--calls", type='string', dest = 'calls', default=None,
#help = 'Custom pipeline (input each block in sequence)')
#
#
#(options, args) = parser.parse_args();
#
#if len(sys.argv)==1:
#	parser.print_help();
#	dummy = sys.exit(0);
#
#global U;
#
#U = calib.read_inps(options.sfile);
#if options.calls!=None:
#	for c in options.calls.split(','):
#		exec('calib.'+c+'(U)');
