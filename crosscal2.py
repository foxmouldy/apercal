#!/usr/bin/python
'''
Bradley Frank, ASTRON 2015
crosscal.py
This script automates the commonly used method for cross-calibrating WSRT data. 
Usage:
python crosscal.py
You need to have a config file to specify all the inputs. 
'''
from apercal import acos
from apercal import mirexecb as mirexec
from ConfigParser import SafeConfigParser
from optparse import OptionParser 
import sys
import os
import apercal
import subprocess
global options
global args
global params

if __name__=="__main__":
	
	usage = "usage: %prog options"
	parser = OptionParser(usage=usage);
	
	parser.add_option("--config", "-c", type='string', dest='config', default="None", 
		help = "Config for input values [None]")
	parser.add_option("--pgflag", "-p", action="store_true", dest="pgflag", default=False,
		help = "Use PGFLAG for automated flagging [False]")
	parser.add_option("--commands", dest="commands", default="filer,mns,calr,splitr", 
		help = "Calibration steps to make [filer,calr]")
	parser.add_option("--doms2uvfits", action='store_true', dest='doms2uvfits', default=False,
		help = "Do ms2uvfits? [False]")
	parser.add_option("--mkconf", action="store_true", dest="mkconf", default=False, 
		help = "Make a new config file? [False]")
	
	(options, args) = parser.parse_args();
	if len(sys.argv)==1:
		parser.print_help()
		dummy = sys.exit(0)
	# Get the parameters
	if options.mkconf!=False:
		# Get the directory of the script:
		sdir = os.path.dirname(os.path.realpath(__file__))
		config_parser = SafeConfigParser()
		config_parser.read(sdir+"/default.txt")
		cdir = os.getcwd()
		with open(cdir+'/default.txt', 'w') as newfile:
			config_parser.write(newfile)
		newfile.close()
		print "Made default.txt"
		print "Edit (and rename) default.txt before proceeding."
		sys.exit(1)

	params = get_params(options.config)
	for c in options.commands.split(','):
		exec(c+"(params)")
	print "\n"
	print "\n"

def ms2uvfits(inms=None):
	'''
	ms2uvfits(inms=None)
	Utility to convert inms to a uvfile
	'''
	outuvf = inms.replace(".MS", ".UVF")
	cmd = "ms2uvfits ms="+inms+" fitsfile="+outuvf+" writesyscal=T multisource=T combinespw=T"
	print "Converted ", outuvf
	shrun(cmd)	

def shrun(cmd):
	'''
	shrun: shell run - helper function to run commands on the shell.
	'''
	#print cmd
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        	stderr = subprocess.PIPE, shell=True)
	out, err = proc.communicate()
	# NOTE: Returns the STD output.
	return out, err

def wsrtfits(uvf, uv=None):
	# NOTE: Import the fits file
	if uv==None:
		uv = uvf.replace('.UVF','.UV')
	cmd = 'wsrtfits in='+uvf+' op=uvin velocity=optbary out='+uv
	shrun(cmd)
	# NOTE: Tsys Calibration
	shrun("attsys vis="+uv+" out=temp")
	shrun('rm -r '+uv)
	shrun('mv temp '+uv);
	shrun('rm -r temp')

def uvflag(vis, flags):
	'''
	UVFLAG: Make the standard flags.
	'''
	uvflg = mirexec.TaskUVFlag()
	for f in flags:
		uvflg.vis = vis
		uvflg.select = f
		uvflg.flagval = 'flag'
		o = uvflg.snarf()

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

def mfcal(vis, params=None):
	mfcal = mirexec.TaskMfCal()
	mfcal.refant = params.refant
	mfcal.interval = float(params.interval)
	mfcal.edge = params.edge
	if len(params.select)>2:
		mfcal.select = params.select
	mfcal.vis = vis
	o = mfcal.snarf ()
	return o

def calcals(parfile):
	'''
	calcals - Calibrate the calibrators
	CAL.UV -> UVFLAG -> MFCAL -> DONE
	'''
	return None

def mergensplit(vis, out, src):
	uvcat = mirexec.TaskUVCat();
	uvcat.vis = vis;
	uvcat.select='source('+src+')';
	if out!=None:
		uvcat.out = out
	else:
		uvcat.out = src+'.UV'
	os.system("rm -r "+uvcat.out)
	o = uvcat.snarf();

def uvcal(invis, outvis, select=None):
	uvcal = mirexec.TaskUVCal ()
	uvcal.vis = invis
	uvcal.out = outvis
	uvcal.options = 'hanning'
	if select!=None:
		uvcal.select = "source("+select+")"
	o = uvcal.snarf ()

