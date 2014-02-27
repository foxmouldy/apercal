from apercal import mirexecb
from optparse import OptionParser 
import sys
import os

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--vis", '-v', type='string', dest = 'vis', default=None,
	help = 'Comma separated list of visibilities to be imaged [None]')

(options, args) = parser.parse_args();

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);

def imager(v, i):
	# INVERT
	invert = mirexecb.TaskInvert();
	invert.vis = v; 
	invert.stokes='ii';
	invert.options='double,mfs';
	invert.robust=-2;
	invert.imsize=1050
	invert.cell=4.;
	invert.map = 'map';
	invert.beam = 'beam';
	invert.slop = '0.5';
	invert.select = 'window('+str(i)+')';
	o = invert.snarf();
	# IMSTAT
	cutoff = 1e-3;
	# CLEAN
	clean = mirexecb.TaskClean()
	clean.map = 'map';
	clean.beam = 'beam';
	clean.out = 'model';
	clean.cutoff = cutoff;
	clean.niters = 10000;
	o = clean.snarf();
	# RESTOR
	restor = mirexecb.TaskRestore();
	restor.model = 'model';
	restor.map = 'map';
	restor.beam = 'beam';
	restor.out = v.replace('.UV', 'W'+str(i)+'.IM');
	restor.snarf();
	# Clean up
	os.system('rm -r beam');
	os.system('rm -r map');
	os.system('rm -r model')

def imcat(images, image):
	os.system('imcat in='+images+' out='+image+' options=relax');
	os.system('rm -r ACF*W*.IM');

if __name__=="__main__":
	for v in options.vis.split(','):
		for i in range(0,8):
			imager(v, i+1);
		imcat(options.vis.replace('.UV','W*.IM'), options.vis.replace('.UV','.IM'));

