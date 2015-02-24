#import mirexec
from apercal import acos
from apercal import mirexecb as mirexec
from ConfigParser import SafeConfigParser
from optparse import OptionParser 
import sys
import os

global options
global args
global params

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
	for m in msfiles.split(','):
		print m
		inms = m
		outuvf = m.upper().replace(".MS",".UVF")
		cmd = "ms2uvfits ms="+inms+" fitsfile="+outuvf+" writesyscal=T multisource=T combinespw=T"
		print cmd
		os.system(cmd)
	
def infits(uvf):
	# Import the fits file
	cmd = 'wsrtfits in='+uvf+' op=uvin velocity=optbary out='+uvf.replace('.UVF', '.UV')
	print cmd
	os.system(cmd);

	# UVFLAG the Static Flags
	uv = uvf.replace('.UVF','.UV')
	uvflag = mirexec.TaskUVFlag()
	for f in params.flags.split(','):
		uvflag.vis = uv 
		uvflag.select=f
		uvflag.flagval='flag'
		print uvflag.__dict__
		o = uvflag.snarf()

	# Tsys Calibration
	os.system("attsys vis="+uv+" out=temp")
	os.system('rm -r '+uv)
	os.system('mv temp '+uv);
	os.system('rm -r temp')

def pgflag(vis, flagpar):
	if params.log==None:
		params.log = vis+'.pgflag.txt' 
	pgflag = mirexec.TaskPGFlag()
	pgflag.vis = vis
	#if params.select!='':
	#	pgflag.select = params.select
	#	print 'blank'
	pgflag.stokes = params.stokes
	pgflag.flagpar = flagpar
	pgflag.options = 'nodisp'

	# This specifies the SumThresholding command.
	pgflag.command = '<'
	print pgflag.__dict__
	tout = pgflag.snarf();
	acos.taskout(pgflag, tout, params.log)

def mfcal(v):
	mfcal = mirexec.TaskMfCal()
	mfcal.vis = v
	mfcal.refant = params.refant
	mfcal.interval = 100000
	mfcal.edge = params.edge
	print mfcal.__dict__
 	o = mfcal.snarf()

def gpcopy(v):
	gpcopy = mirexec.TaskGPCopy();
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
		puthd = mirexec.TaskPutHead();
		puthd.in_ = s+'/restfreq';
		puthd.value = 1.420405752;
		print puthd.__dict__
		o = puthd.snarf();
		
		puthd.in_ = s+'/interval'
		puthd.value = 1.0
		puthd.type = 'double'
		print puthd.__dict__
		o = puthd.snarf();
	
		gpcopy  = mirexec.TaskGPCopy();
		gpcopy.vis = cal;
		gpcopy.out = s;
		print gpcopy.__dict__
		o = gpcopy.snarf();

def mergensplit(vis, src, out=None):
	uvcat = mirexec.TaskUVCat();
	uvcat.vis = vis;
	uvcat.select='source('+src+')';
	if out!=None:
		uvcat.out = out
	else:
		uvcat.out = src+'.UV'
	print uvcat.__dict__
	o = uvcat.snarf();

def get_params(configfile):
	config_parser = SafeConfigParser()
	config_parser.read(configfile)
	params = Bunch()
	for p in config_parser.items('crosscal'):
		setattr(params, p[0], p[1])
	return params

if __name__=="__main__":
	
	# Get the parameters
	params = get_params(options.config)
	
	# Import the files and then do the Tsys calibration
	ms2uvfits(params.msfiles)
	for m in params.msfiles.split(','):
		infits(m.upper().replace('.MS', '.UVF'))
	for c in params.cals.split(","):
		mergensplit(params.msfiles.replace(".MS",".UV"), c)
	for s in params.srcs.split(","):
		mergensplit(params.msfiles.replace(".MS",".UV"), s)
	
	# Do Calcals
	print "\n"
	print "\n"
	for c in params.cals.split(","):
		mfcal(c+".UV")
		pgflag(c+".UV", params.flagpar)
		mfcal(c+".UV")
		pgflag(c+".UV", params.flagpar2)
		mfcal(c+".UV")
	cal0 = params.cals.split(",")[0]

	# Copy it over to the Sources
	print "\n"
	print "\n"
	for s in params.srcs.split(","):
		cal2srcs(cal0+".UV", s+".UV")
		pgflag(s+".UV", params.flagpar)
	for s in params.srcs.split(","):
		mergensplit(s+".UV", src=s, out=s+".UVc")
