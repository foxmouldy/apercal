#!/usr/bin/python
'''
Bradley Frank, ASTRON 2015
crosscal.py
This script automates the commonly used method for cross-calibrating WSRT data. 
Usage:
python crosscal.py
You need to have a config file to specify all the inputs. 
'''
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
parser.add_option("--pgflag", "-p", action="store_true", dest="pgflag", default=False,
	help = "Use PGFLAG for automated flagging [False]")
parser.add_option("--commands", dest="commands", default="filer,calr", 
	help = "Calibration steps to make [filer,calr]")

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
	o = uvcat.snarf();

def get_params(configfile):
	config_parser = SafeConfigParser()
	config_parser.read(configfile)
	params = Bunch()
	for p in config_parser.items('crosscal'):
		setattr(params, p[0], p[1])
	return params

def filer(params):
	# Import the files and then do the Tsys calibration
	ms2uvfits(params.msfiles)
	for m in params.msfiles.split(','):
		infits(m.upper().replace('.MS', '.UVF'))
	for c in params.cals.split(","):
		mergensplit(params.msfiles.replace(".MS",".UV"), c)
	for s in params.srcs.split(","):
		mergensplit(params.msfiles.replace(".MS",".UV"), s)

def calr(params):
	# Actually do the calibration.
	for c in params.cals.split(","):
		if options.pgflag!=False:
			#NOTE: Only do PGFLAG if activated from command line.
			pgflag(c+".UV", params.pgflag)
		mfcal(c+".UV")
	
	cal0 = params.cals.split(",")[0]

	# Copy it over to the Sources
	for s in params.srcs.split(","):
		cal2srcs(cal0+".UV", s+".UV")
		#NOTE: Only do PGFLAG if activated from command line.
		if options.pgflag!=False:
			pgflag(s+".UV", params.flagpar)
	for s in params.srcs.split(","):
		mergensplit(s+".UV", src=s, out=s+".UVc")

def splitr(params):
	"""
	Splits each corrected visfile into subbands.
	"""
	for s in params.srcs.split(','):
		print "Splitting ", s, " into subbands"
		cmd = "uvsplit vis="+s+".UVc"
		print cmd
		print "Moving subbands into ", s
		os.system(cmd)
		cmd = "mkdir "+s
		print cmd
		os.system(cmd)
		cmd = "mv "+s.lower()+".* "+s+"/"
		print cmd
		os.system(cmd)

if __name__=="__main__":
	
	# Get the parameters
	params = get_params(options.config)
	for c in options.commands.split(','):
		exec(c+"(params)")
	# Import the files and then do the Tsys calibration

#	ms2uvfits(params.msfiles)
#	for m in params.msfiles.split(','):
#		infits(m.upper().replace('.MS', '.UVF'))
#	for c in params.cals.split(","):
#		mergensplit(params.msfiles.replace(".MS",".UV"), c)
#	for s in params.srcs.split(","):
#		mergensplit(params.msfiles.replace(".MS",".UV"), s)
#	
	# Do Calcals
	print "\n"
	print "\n"
	
#		
#	for c in params.cals.split(","):
#		if options.pgflag!=False:
#			#NOTE: Only do PGFLAG if activated from command line.
#			pgflag(c+".UV", params.pgflag)
#		mfcal(c+".UV")
#	
#	cal0 = params.cals.split(",")[0]
#
#	# Copy it over to the Sources
#	print "\n"
#	print "\n"
#	for s in params.srcs.split(","):
#		cal2srcs(cal0+".UV", s+".UV")
#		#NOTE: Only do PGFLAG if activated from command line.
#		if options.pgflag!=False:
#			pgflag(s+".UV", params.flagpar)
#	for s in params.srcs.split(","):
#		mergensplit(s+".UV", src=s, out=s+".UVc")
