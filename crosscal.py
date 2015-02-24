import mirexec
from ConfigParser import SafeConfigParser
from optparse import OptionParser 
import sys
import os

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--config", "-c", type='string', dest='config', default="None", 
	help = "Config for input values [None]")
(options, args) = parser.parse_args();

class Bunch: 
	def __init__(self, **kwds): 
		self.__dict__.update(kwds)

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);

def ms2uvfits(msfiles):
	for m in msfiles:
		inms = m
		outuvf = m.upper().replace(".MS",".UVF")
		os.sytem("ms2uvfits ms="+inms+" fitsfile="+outuvf+" writesyscal=T multisource=T combinespw=T")

def wsrtfits(uvf):
	os.system('wsrtfits in='+uvf+' op=uvin velocity=optbary out='+uvf.replace('.UVF', '.UV'));
	return uvf.replace('.UVF','.UV');

def uvflag(uv, flags='an(6),shadow(25),auto'):
	uvflag = mirexecb.TaskUVFlag();
	for f in flags.split(','):
		uvflag.vis = uv; 
		uvflag.select=f;
		uvflag.flagval='flag'
		o = uvflag.snarf();
		print o;
	
def attsys(uv):
	os.system("attsys vis="+uv+" out=temp")
	os.system('rm -r '+uv);
	os.system('mv temp '+uv);
	os.system('rm -r temp');

def pgflag(params):
	if params.log==None:
		# This default naming convention is a little clumsy, but at
		# least its clear what's happening here. 
		params.log = params.vis+'.pgflaglog.txt';
	pgflag = mirexecb.TaskPGFlag();
	pgflag.vis = params.vis;
	pgflag.select = params.select;
	pgflag.stokes = 'qq' 
	pgflag.flagpar = params.flagpar;
	pgflag.options = 'nodisp'
	
	# This specifies the SumThresholding command.
	pgflag.command = '<';
	tout = pgflag.snarf();
	acos.taskout(pgflag, tout, options.log)

def mfcal(v, refant):
	mfcal = mirexecb.TaskMfCal();
	mfcal.vis = v; 
	mfcal.refant = refant;
	mfcal.interval = 100000;
 	o = mfcal.snarf();
	print mfcal.commandLine()
	print o; 

def gpcopy(v):
	gpcopy = mirexecb.TaskGPCopy();
	for i in range(len(v)-1):
		gpcopy.vis = v[0];
		gpcopy.out = v[i];
		gpcopy.options = 'nopass';
		gpcopy.merge = 'nopass';
		o = gpcopy.snarf();
		print o

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

def mergensplit(vis, src):
	uvcat = mirexecb.TaskUVCat();
	uvcat.vis = vis;
	uvcat.select='source('+src+')';
	uvcat.out = src+'.UV'
	o = uvcat.snarf();

def get_params(configfile):
	config_parser = SafeConfigParser()
	config_parser.read(configfile)
	params = Bunch()
	for p in config_parser.items('crosscal'):
		setattr(params, p[0], p[1])
	return params

if __name__=="__main__":
	params = get_params(options.config)
	ms2uvfits(params.msfiles)
