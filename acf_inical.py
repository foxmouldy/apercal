from apercal import mirexecb
from optparse import OptionParser 
import sys
import os

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--vis", '-v', type='string', dest = 'vis', default=None,
	help = 'Comma separated list of visibilities to import fits and to apply Tsys [None]')
parser.add_option("--flags", '-f', type='string', dest = 'flags', default='an(6),shadow(25),auto', 
	help = 'Comma separated list of flags [an(6),shadow(25),auto]')
(options, args) = parser.parse_args();

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);

def wsrtfits(uvf):
	os.system('wsrtfits in='+uvf+' op=uvin velocity=optbary out='+uvf.replace('.UVF', '.UV'));
	return uvf.replace('.UVF','.UV');

def uvflag(uv, flags='an(6),shadow(25),auto'):
	uvflag = mirexecb.TaskUVFlag();
	#flags = ('an(6)', 'shadow(25)', 'auto');
	for f in flags.split(','):
		uvflag.vis = uv; 
		uvflag.select=f;
		uvflag.flagval='flag'
		o = uvflag.snarf();
		print o;

def attsys(uv):
	tsysmed = mirexecb.TaskTsysmed();
	tsysmed.vis = uv; 
	tsysmed.out = '.temp';
	o = tsysmed.snarf();
	print o; 
	os.system('attsys vis=.temp out=.temp2')
	os.system('rm -r '+uv);
	os.system('mv .temp2 '+uv);
	os.system('rm -r .temp');

if __name__=="__main__":
	for v in options.vis.split(','):
		print v
		w = wsrtfits(v);
		uvflag(w, options.flags);
		attsys(w);
