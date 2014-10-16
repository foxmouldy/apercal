import pylab as pl
import time
import os
import threading
import sys
import mirexec
from apercal import mirexecb
from optparse import OptionParser
import wskalib as wl
from ConfigParser import SafeConfigParser
config = SafeConfigParser()

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

# O1 for Option 
parser.add_option("--p", type = '--parset', dest = 'parset', default=None, 
	help = 'Parset for the calibration');

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

if __name__=="__main__":
	if len(sys.argv)==1: 
		parser.print_help()
		dummy = sys.exit(0)
	config.read(options.parset)
	calls = config.get('system', 'calls')
	for c in calls:
		cmd = 'wskalib.'+c+'(config)'
	print cmd
	exec(cmd)