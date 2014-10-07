import mirexec
import os
import sys
from optparse import OptionParser

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

# O1 for Option 
parser.add_option("--vis", "-v", type = 'string', dest = 'vis', default=None, 
	help = 'Visiblity to be flagged [None]');
parser.add_option('--select', '-s', type='string', dest = 'select',
default=None, help = "Selection to be flagged [None]");
parser.add_option('--edge', '-l', type='string', dest='edge', default=None,
help = 'Spectral Line selection to be flagged [None]')
(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

def uvflag(vis, select, edge):
	uvflag = mirexec.TaskUVFlag();
	uvflag.vis = vis;
	uvflag.select = select;
	uvflag.edge = edge;
	uvflag.flagval='flag';
	tout = uvflag.snarf();
	return tout;

if __name__=="__main__":
	tout = uvflag(options.vis, options.select, options.edge); 
	print tout
