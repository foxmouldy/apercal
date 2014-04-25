import pylab as pl
import sys
from optparse import OptionParser

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--infile", type='string', dest='infile', default=None, 
	help = "Input file of results to be plotted [None]");
parser.add_option("--fig", type='string', dest='fig', default=None, 
	help = "Name of output figure [infile].eps");

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

if options.fig==None:
	options.fig = options.infile+'.eps';

def plot(options):
	'''
	Module which plots the result of watch_family.py. This plots the percentage
	CPU and MEM usage as a function of user time. 
	'''
	X = pl.loadtxt(options.infile);
	pl.subplot(311);
	pl.step(X[:,0], X[:,2], 'r-', lw=2, alpha=0.8, label="%CPU");
	pl.step(X[:,0], X[:,3], 'b-', lw=2, alpha=0.8, label="%MEM");
	pl.legend(loc=2);
	pl.ylabel('%');
	pl.subplot(312);
	pl.step(X[:,0], X[:,4], 'r-', lw=2, alpha=0.8, label='read_count');
	pl.step(X[:,0], X[:,5], 'b-', lw=2, alpha=0.8, label='write_count');
	pl.legend(loc=4);
	pl.subplot(313);
	pl.step(X[:,0], X[:,6]/(1024.*1024*1024.), 'r-', lw=2, alpha=0.8, label='read_bytes');
	pl.step(X[:,0], X[:,7]/(1024.*1024*1024), 'b-', lw=2, alpha=0.8, label='write_bytes');
	pl.ylabel('GB')
	pl.legend(loc=4);
	pl.savefig(options.fig);
	pl.xlabel('User Time [s]');

if __name__=="__main__":
	plot(options);

