#!/usr/bin/python
'''
Bradley Frank, ASTRON 2015
crosscal.py
This is a library for the cross-calibration of WSRT/APERTIF data. 
Usage:
import crosscal
'''
import sys
import os
import logging
import lib
#global params
# TODO: params needs to be replaced everywhere. 


def ms2uvfits(ms=None):
    	'''
    	ms2uvfits(ms=None)
    	Utility to convert ms to a uvfits file
    	'''
	# Setup the path and input file name.  
    	path2ms = os.path.split(ms)[0]
	ms = os.path.split(ms)[1]
	logging.info("ms2uvfits: Converting MS to UVFITS Format")
	if ms is None:
		logger.error("MS not specified. Please check parameters")
		sys.exit(0)
	try: 
		os.chdir(path2ms)
		logging.info("Moved to path "+path2ms)
	except:
		logging.error("Error: Directory or MS does not exist!")
		sys.exit(0)
	
	# Start the processing by setting up an output name and reporting the status.	
    	uvfits = ms.replace(".MS", ".UVF")
	# TODO: Decided whether to replace logging.info with logging.debug, since this module is
	# wrapped up. 
	logging.info("MS: "+ms)
	logging.info("UVFITS: "+uvfits)
	logging.info("Directory: "+path2ms)
	# NOTE: Here I'm using masher to call ms2uvfits.  
	o = lib.masher(task='ms2uvfits', ms=ms, fitsfile=uvfits, writesyscal='T',
			multisource='T', combinespw='T')

def importuvfitsys(uvfits=None, uv=None, tsys=True):
	'''
	Imports UVFITS file and does Tsys correction on the output MIRIAD UV file.
	Uses the MIRIAD task WSRTFITS to import the UVFITS file and convert it to MIRIAD UV format.
	Uses the MIRIAD task ATTSYS to do the Tsys correction.

	'''
	# NOTE: Import the fits file
	path2uvfits = os.path.split(uvfits)[0]
	uvfits = os.path.split(uvfits)[1]
	if uv is None:
		# Default output name if a custom name isn't provided.
		uv = uvfits.split('.')[0]+'.UV'
	if uvfits is None:
		logger.error("UVFITS not specified. Please check parameters")
		sys.exit(0)
	try: 
		os.chdir(path2uvfits)
		logging.info("Moved to path "+path2uvfits)
	except:
		logging.error("Error: Directory or UVFITS file does not exist!")
		sys.exit(0)
	#cmd = 'wsrtfits in='+uvf+' op=uvin velocity=optbary out='+uv
	lib.masher(task='wsrtfits', in_=uvfits, out=uv, op='uvin', velocity='optbary')

	# NOTE: Tsys Calibration
	#basher("attsys vis="+uv+" out=temp")
	if tsys is True:
		lib.masher(task='attsys', vis=uv, out='temp')
		lib.basher('rm -r '+uv)
		lib.basher('mv temp '+uv);

def uvflag(vis=None, select=None):
	'''
	vis: visibility file to be flagged
	select: semi-colon separated list of data selections to be flagged
	'''
	# Setup the path and move to it.
	path2vis = os.path.split(vis)[0]
	vis = os.path.split(vis)[1]
	logging.info("uvflag: Flagging Tool")
	if vis is None or select is None:
		logger.error("Vis or Flagsnot specified. Check parameters.")
		sys.exit(0)
	try: 
		os.chdir(path2vis)
		logging.info("Moved to path "+path2vis)
	except:
		logging.error("Error: path to vis does not exist!")
		sys.exit(0)
	# Flag each selection in a for-loop
	for s in select.split(';'):
		o = lib.masher(task='uvflag', vis=vis, select='"'+s+'"', flagval='flag') 
		logging.info(o)

def pgflag(vis=None, flagpar='6,2,2,2,5,3', settings=None, stokes='qq'):
	'''
	Wrapper around the MIRIAD task PGFLAG, which in turn is a wrapper for the AOFlagger
	SumThreshold algorithm.
	Defaults:  flagpar='6,2,2,2,5,3',  stokes='qq'
	Uses parameters from a settings object if this is provided.
	Outputs are written to a log file, which is in the same directory as vis, and has name
	<vis>.pgflag.txt.
	Note: The considerably long output of PGFLAG is written out with the logger at debug level.
	This may not be ideal if you're having a quick look, so switch the level to info if you want
	to avoid the output of the task appearing in your console. 
	Beware: You could lose a LOT of data if you're not careful!!!
	'''
	# Exception handling and checking
	logging.info("PGFLAG: Automated Flagging using SumThresholding")
	if vis is None and settings is None:
		logging.error("No inputs - please provide either vis and flagpar or settings.")
		sys.exit(0)
	path2vis = os.path.split(vis)[0]
	vis = os.path.split(vis)[1]
	try: 
		os.chdir(path2vis)
		logging.info("Moved to path "+path2vis)
	except:
		logging.error("Error: path to vis does not exist!")
		sys.exit(0)

	# Do pgflag with the settings parameters if provided.
	if settings is not None and vis is not None:
		params = settings.get('pgflag')
		logging.info("Doing PGFLAG on "+vis+" using stokes="+params.stokes+" with flagpar="+params.flagpar)
		logging.info("Output written to "+vis+'.pgflag.txt')
		o = lib.masher(task='pgflag', vis=vis, stokes=params.stokes, flagpar=params.flagpar, 
				options='nodisp', command="'<'")
	# Do PGFLAG with input settings, i.e. no settings file provided.
	if vis is not None and settings is None:
		logging.info("Doing PGFLAG on "+vis+" using stokes "+stokes+" with flagpar="+flagpar)
		o = lib.masher(task='pgflag', vis=vis, stokes=stokes, flagpar=flagpar, options='nodisp', command="'<'")
	logging.info("Writing output "+path2vis+'/'+vis+'.pgflag.txt')
	lib.write2file('pgflag', o, vis+'.pgflag.txt')	
	logging.info("PGFLAG: DONE.")
	
def calcals(settings=None):
	'''
	Does MFCAL on the calibrator visibilities provided, for all the calibrators in the
	directory. 
	Changes into the working directory, and does MFCAL on all the calibrator files in there.
	'''
	# Setting up and exception handling.
	logging.info("CALCALS: MFCALS on all Calibrator Visibilities")	
	if settings is None:
		logging.error("Settings Not Provided!")
		sys.exit(0)

	params = settings.get('mfcal')
	try: 
		os.chdir(settings.get('data', 'working'))
		logging.info("Moved to path "+settings.get('data', 'working'))
	except:
		logging.error("Error: path does not exist!")
		sys.exit(0)
	# Get the name of the calibrator files
	uvfiles = settings.get('data', 'cals')
	# Repeat MFCAL for each of the calibrator files.
	for v in uvfiles:
		output = lib.masher(task='mfcal', refant=params.refant, vis=v,
				interval=params.interval, edge=params.edge,
				select='"'+params.select+'"')
		logging.info("Completed MFCAL on "+v)
	logging.info("CALCALS Done!")	

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
	stdout = apercal.basher('ls -d '+settings.get('data', 'working')+'src*.uv')
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
	stdout = apercal.basher('ls -d '+settings.get('data', 'working')+'src*.uv')
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

def sbsplit(vis=None):
	'''
	Creates subdirectory for each source/pointing. 
	vis is the name of the visibility file to be splitted, or a comma separated list of files to
	be splitted.
	'''
	path2vis = os.path.split(vis)[0]
	vis = os.path.split(vis)[1]
	logging.info("sbsplit: Splitting Visibility in Subbands")
	if vis is None:
		logger.error("Vis not specified. Check parameters.")
	try: 
		os.chdir(path2vis)
		logging.info("Moved to path "+path2vis)
	except:
		logging.error("Error: path2vis does not exist!")
		sys.exit(0)

	for v in vis.split(','):
		logging.info("Splitting "+v)
		output = lib.masher(task='uvsplit', vis=v)
	sb_names = [o.replace('Creating ', '') for o in output.split('\n')[3:-1]]	
	# Assuming that the source name is the same for all SBs:
	source_name = sb_names[0].split('.')[0]
	if not os.path.exists(source_name):
		logging.info("Making directory....")
		lib.basher("mkdir "+source_name)
	for sb in sb_names:
		freq = sb.split('.')[1]
		if not os.path.exists(source_name+"/"+freq):
			logging.info("Making "+source_name+"/"+freq)	
			lib.basher("mkdir "+source_name+"/"+freq)
		logging.info("Moving "+sb+" to "+source_name+"/"+freq+"/vis")
		lib.basher("mv "+sb+" "+source_name+"/"+freq+"/vis")
	logging.info("sbsplit: Done!")

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

def flagnquack(settings, prefix):
	'''
	flagnquacks(settings, prefix) 
	UVFLAG the static flags in the files defined by the given <prefix> - e.g. cal or src.
	This refers to the prefix that you have assigned to the file, and **not** the name of the
	variable. 
	'''
	# NOTE: Need to get the names of the calfiles.
	stdout = lib.basher('ls -d '+settings.get('data', 'working')+prefix+'*')
	uvfiles = stdout[0].split('\n')[0:-1]
	for i in range(0, len(uvfiles)):
		uvfile = settings.get('data', 'working') + prefix + str(i+1) + '.uv'		
		uvflag(uvfile, settings.get('flag', 'flagnquacks'))
		out, err = basher("qvack vis="+uvfile+" mode=source")
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
	stdout = apercal.basher('ls -d '+settings.get('data', 'working')+'src*.uv')
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
