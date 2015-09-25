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
    cmd = "~/ms2uvfits ms="+inms+" fitsfile="+outuvf+" writesyscal=T multisource=T combinespw=T"
    print cmd
    #print "Converted ", outuvf
    o, e =shrun(cmd)
    print o, e

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

def calcals(settings):
	'''
	Does MFCAL on all the calibrators. 
	'''
	stdout = apercal.shrun('ls -d '+settings.get('data', 'working')+settings.get('data', 'calprefix')+'*')
	uvfiles = stdout[0].split('\n')[0:-1]

	mfcal = mirexec.TaskMfCal()
	mfcal.refant = settings.get('mfcal', 'refant')
	mfcal.interval = float(settings.get('mfcal', 'interval'))
	mfcal.edge = settings.get('mfcal', 'edge')
	mfcal.select = settings.get('mfcal', 'select')
	o = []
	for v in uvfiles:
		mfcal.vis = v
		o.append( mfcal.snarf())
		print "MFCAL'd ", v 
	return o
	
def cal2srcs(cal, settings):
	'''
	Cals = 'cal1,cal2'
	Srcs = 'src1,src2'
	'''
	for s in srcs.split(','):
		puthd = mirexec.TaskPutHead()
		puthd.in_ = s+'/restfreq'
		puthd.value = 1.420405752
		o = puthd.snarf()
		
		puthd.in_ = s+'/interval'
		puthd.value = 1.0
		puthd.type = 'double'
		o = puthd.snarf()
	
		gpcopy  = mirexec.TaskGPCopy()
		gpcopy.vis = cal
		gpcopy.out = s
		o = gpcopy.snarf()

def mergensplit(vis, out, src):
	uvcat = mirexec.TaskUVCat()
	uvcat.vis = vis
	uvcat.select='source('+src+')'
	if out!=None:
		uvcat.out = out
	else:
		uvcat.out = src+'.UV'
	os.system("rm -r "+uvcat.out)
	o = uvcat.snarf()

def hann_split(settings):
	'''
	Uses UVCAL to smooth and split sources. 
	'''

	# Get the file names.
	srcprefix = settings.get('data', 'srcprefix')
	stdout = apercal.shrun('ls -d '+settings.get('data', 'working')+'src*.uv')
	uvfiles = stdout[0].split('\n')[0:-1]
	source_names = apercal.get_source_names(uvfiles[0])

	uvcal = mirexec.TaskUVCal ()
	uvcal.vis = settings.get('data', 'working')+srcprefix+'*.uv'
	uvcal.options = 'hanning'
	o = []
	for s in source_names:
		print "Splitting ", s
		uvcal.select = "source("+s+")"
		uvcal.out = settings.get('data', 'working')+s+'.uv'
		o.append(uvcal.snarf ())
		print uvcal.vis, "split into", uvcal.out
	return o 

def source_split(settings):
	'''
	Splits sources without doing any smoothing.
	'''
	# Get the file names.
	srcprefix = settings.get('data', 'srcprefix')
	stdout = apercal.shrun('ls -d '+settings.get('data', 'working')+'src*.uv')
	uvfiles = stdout[0].split('\n')[0:-1]
	source_names = apercal.get_source_names(uvfiles[0])

	uvcat = mirexec.TaskUVCal ()
	uvcat.vis = settings.get('data', 'working')+srcprefix+'*.uv'
	o = []
	for s in source_names:
		print "Splitting ", s
		uvcat.select = "source("+s+")"
		uvcat.out = settings.get('data', 'working')+s+'.uv'
		o.append(uvcat.snarf ())
		print uvcat.vis, "split into", uvcat.out
	return o 

#def sbsplit(settings):
#	'''
#	Creates subdirectory structure for each source/pointing, and splits the parent UV file into
#	spectral windows. This is usually necessary for the selfcal module. 
#	'''
#	srcprefix = settings.get('data', 'srcprefix')
#	stdout = apercal.shrun('ls -d '+settings.get('data', 'working')+'src*.uv')
#	uvfiles = stdout[0].split('\n')[0:-1]
#	source_names = apercal.get_source_names(uvfiles[0])
#
#	for s in source_names:
#		print "Splitting ", s, " into subbands"
#		out, err = shrun("uvsplit vis="+settings.get('data', 'working')+s+".uv")
#		#print "Moving subbands into ", s
#		shrun("mkdir "+settings.get('data', 'working')+s)
#		#print "mkdir "+settings.get('data', 'working')+s
#		shrun("mv "+s.lower()+".* "+settings.get('data', 'working')+s+"/")
#		#print "mv "+s.lower()+".* "+settings.get('data', 'working')+s+"/"
#	print "Subband Split DONE"
#	return 1

def sbsplit(settings):


def ms2uv(settings):
	'''
	ms2uv(settings)
	Function that converts MS to MIRIAD UV files, also does Tsys correction.
	Loops over all calfiles and srcfiles. 
	'''
	# First, do the calfiles.
	calprefix = settings.get('data', 'calprefix')
	calfiles = settings.get('data', 'calfiles')
	print 
	for i in range(0, len(calfiles)):
		# NOTE: MS2UVFITS: MS -> UVFITS (in rawdata)
		msfile = settings.get('data', 'rawdata') + calfiles[i]
		ms2uvfits(inms = msfile)
		uvfitsfile = msfile.replace('.MS', '.UVF')
		uvfile = settings.get('data', 'working') + calprefix + str(i+1) + '.uv'
		# NOTE: UVFITS: rawdata/UVFITS -> working/UV
		wsrtfits(uvfitsfile, uvfile)

	# Second, do the srcfiles.
	srcprefix = settings.get('data', 'srcprefix')
	srcfiles = settings.get('data', 'srcfiles')
	for i in range(0, len(srcfiles)):
		# NOTE: MS2UVFITS: MS -> UVFITS (in rawdata)
		msfile = settings.get('data', 'rawdata') + srcfiles[i]
		ms2uvfits(inms = msfile)
		uvfitsfile = msfile.replace('.MS', '.UVF')
		uvfile = settings.get('data', 'working') + srcprefix + str(i+1) + '.uv'
		# NOTE: UVFITS: rawdata/UVFITS -> working/UV
		wsrtfits(uvfitsfile, uvfile)
	return 0 

def quack(uv):
	'''
	quack(uv)
	Wrapper around the MIRIAD task QVACK. Uses the standard settings. 
	'''
	# TODO: This section is a little defunct and doesn't quite work properly. Needs to be fixed.
	quack = mirexec.TaskQuack()
	quack.vis = uv
	o = quack.snarf()
	return o 

def sflag(settings, prefix):
	'''
	sflags(settings, prefix) 
	UVFLAG the static flags in the files defined by the given <prefix> - e.g. cal or src.
	This refers to the prefix that you have assigned to the file, and **not** the name of the
	variable. 
	'''
	# NOTE: Need to get the names of the calfiles.
	stdout = apercal.shrun('ls -d '+settings.get('data', 'working')+prefix+'*')
	uvfiles = stdout[0].split('\n')[0:-1]
	for i in range(0, len(uvfiles)):
		uvfile = settings.get('data', 'working') + prefix + str(i+1) + '.uv'		
		uvflag(uvfile, settings.get('flag', 'sflags'))
		out, err = shrun("qvack vis="+uvfile+" mode=source")
		#print out, err
		print "Flagged and Quacked ", uvfile
		
def cal2srcs(settings, cal='cal1.uv'):
	'''
	settings: The settings file from your session. This will be used to copy over the solutions.
	cal: the name of the cal file (without full path) which you will use for the gain and
	bandpass calibration. 

	'''
	cal = settings.get('data', 'working')+cal
	srcprefix = settings.get('data', 'srcprefix')
	srcfiles = settings.get('data', 'srcfiles')
	stdout = apercal.shrun('ls -d '+settings.get('data', 'working')+'src*.uv')
	uvfiles = stdout[0].split('\n')[0:-1]
	o = []
	for s in uvfiles:
		puthd = mirexec.TaskPutHead();
		puthd.in_ = s+'/restfreq';
		puthd.value = 1.420405752;
		o.append(puthd.snarf())
		
		puthd.in_ = s+'/interval'
		puthd.value = 1.0
		puthd.type = 'double'
		o.append(puthd.snarf())
	
		gpcopy  = mirexec.TaskGPCopy();
		gpcopy.vis = cal;
		gpcopy.out = s;
		o.append(gpcopy.snarf())
		print "Copied Gains from ", cal, " to ",s
	print "DONE cal2srcs"
	return o 
