import mirexecb
from optparse import OptionParser 

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--vis", '-v', type='string', dest = 'vis', default=None,
	help = 'Comma separated list of visibilities to import fits and to apply Tsys [None]')

(options, args) = parser.parse_args();

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);

def wsrtfits(uvf)
	wsrtfits = mirexecb.TaskWSRTFits();
	wsrtfits.in_ = uvf; 
	wsrtfits.mode = 'uvin'; 
	wsrtfits.out = uvf.replace('.UVF', '.uv');
	wsrtfits.velocity = 'optbary';
	o = wsrtfits.snarf();
	print o; 

def uvflag(uv):
	uvflag = mirexecb.TaskUVFlag();
	flags = ('an(6)', 'shadow(25)', 'auto');
	for f in flags:
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
	attsys = mirexecb.TaskAttsys();
	attsys.vis = '.temp';
	attsys.out = '.temp2';
	o = attsys.snarf();
	print o;
	os.system('rm -r '+uv);
	os.system('mv .temp2 '+uv);
	os.system('rm -r .temp');

if "__name__"=="__main__":
	for v in options.vis.split(','):
		wsrtfits(options.vis);
		uvflag(options.vis);
		attsys(options.vis);
