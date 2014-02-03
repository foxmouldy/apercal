import os
import sys
from optparse import OptionParser 

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--working", '-w', type='string', dest='working', default=None,
	help = 'Path to working directory. [None]');


(options, args) = parser.parse_args();

if len(sys.argv)==1:
	# Run or Import
	if __name__=="__main__":
		print "setup.py: Copies over the relevant scripts and example settings files. "
		parser.print_help();
		dummy = sys.exit(0);

#p2w = os.getcwd();

files = ['kal.py', 
	'peel.py', 
	'pgflagger.py', 
	'settings/src.uv.dat',
	'setings/src.uv_chan0.dat']

for f in files: 
	cmd = 'cp '+f+' '+working;
