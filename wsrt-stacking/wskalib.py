import pylab as pl
import time
import os
import threading
import sys
import mirexec
from apercal import mirexecb
from optparse import OptionParser

def cleanup(config):
	for p in config.items('mfiles'):
		os.system('rm -r '+p[0]+'*')
		os.system('rm -r '+p[1]+'*')

def getimmax(imname):
	imstat = mirexec.TaskImStat()
	imstat.in_ = imname;
	imstats = imstat.snarf();
	immax = float(imstats[0][10][51:61]);
	imunits = imstats[0][4];
	return immax, imunits


def pgflag(config):
	pgflag = mirexecb.TaskPGFlag();
	for p in config.items('mfiles')[0:-1]:
		pgflag.vis = config.get('mfiles', p[0])
		pgflag.stokes = config.get('flag', 'stokes')
		pgflag.flagpar = config.get('flag', 'flagpar')
		pgflag.options = 'nodisp';
		pgflag.command = '<';
		pgflag.snarf();

def calcals(config):
	mfcal = mirexec.TaskMfCal();
	for p in config.items('mfiles')[0:-2]:
		mfcal.vis = config.get('mfiles', p[0]);
		if config.get('mfcal', 'edge').upper()!='NONE':
			mfcal.edge = config.get('mfcal', 'edge')
		if config.get('mfcal', 'line').upper()!='NONE':
			mfcal.line = config.get('mfcal', 'line')
		mfcal.interval = 10000;
		mfcal.refant = config.get('mfcal', 'refant')
		mfcal.snarf();

def cal2srcs(config):
	'''
	'''
	# puthd on src
	cal = config.get('mfiles', 'cal1')
	src = config.get('mfiles', 'src')
	puthd = mirexec.TaskPutHead();
	puthd.in_ = src+'/restfreq';
	puthd.value = 1.420405752;
	puthd.snarf();
	
	puthd.in_ = src+'/interval'
	puthd.value = 1.0
	puthd.type = 'double'
	puthd.snarf();

	# gpcopy cal1 -> src
	gpcopy  = mirexec.TaskGPCopy();
	gpcopy.vis = cal;
	gpcopy.out = src;
	gpcopy.snarf();

def iofits(config):
	'''
	Reads in the uvfits file I and exports it to the miriad-uv file O,
	using the carma-miriad task wsrtfits.
	'''
	for p in config.items('uvfits'):
		I = p[1]
		O = config.get('mfiles', p[0])
		flags = config.get('flag', 'flags')
		#TODO: Fix the wsrtfits and attsys modules
		#wsrtfits = mirexecb.TaskWSRTFits()
		#wsrtfits.in_ = I 
		#wsrtfits.out = O
		#wsrtfits.op = 'uvin'
		#wsrtfits.velocity = 'optbary'
		#wsrtfits.snarf()
		cmd = 'wsrtfits in='+I+' out='+O+' op=uvin velocity=optbary';
		os.system(cmd);
		#attsys = mirexecb.TaskAttsys()
		#attsys.vis = O
		#attsys.optons='apply'
		#attsys.out = '_tmp_vis'
		#attsys.snarf()
		cmd = 'attsys vis='+O+' out=_tmp_vis';
		os.system(cmd);
		cmd = 'rm -r '+O;
		os.system(cmd);
		cmd = 'mv _tmp_vis '+O;
		os.system(cmd);
		for f in flags.split(','):
			uvflag = mirexec.TaskUVFlag();
			uvflag.vis = O;
			uvflag.select = f
			uvflag.flagval = 'flag';
			uvflag.snarf();

def uvlin(config):
	vis = config.get('mfiles', 'src')
	chans = config.get('settings', 'chans')
	order = config.get('settings', 'order')
	mode = config.get('settings', 'mode')
	out = config.get('mfiles', 'src_line')
	cmd = 'uvlin vis='+vis+' chans='+chans+' order='+order+' mode='+mode+' out='+out;
	os.system(cmd)
	#uvlin = mirexecb.TaskUVLin()
	#uvlin.vis = vis
	#uvlin.chans = chans
	#uvlin.order = order
	#uvlin.mode = mode
	#uvlin.out = out
	#uvlin.snarf()

def imager(config):
	vis = config.get('imaging', 'vis')
	select = config.get('imaging', 'select')
	mapname = config.get('imaging', 'map')
	beamname = config.get('imaging', 'beam')
	imname = config.get('imaging', 'image')
	modelname = config.get('imaging', 'model')
	maskname = config.get('imaging', 'mask')
	cutoff = config.get('imaging', 'cutoff')
	line = config.get('imaging', 'line')
	robust = config.get('imaging', 'robust')
	options = config.get('imaging', 'options')
	imsize = config.get('imaging', 'imsize')
	invertr(vis, select, mapname, beamname,  options, imsize, robust, line)
	clean(mapname, beamname, modelname)
	restor(mapname, beamname, modelname, imname);
	immax, imunits = getimmax(imname);
	maths(imname, immax/10, maskname);
	clean(mapname, beamname, modelname, maskname, cutoff)
	restor(mapname, beamname, modelname, imname);

def invertr(vis, select, mapname, beamname, options, imsize, robust=-2.0, line='', ):
	invert = mirexec.TaskInvert()
	invert.vis = vis;
	if select.upper()!='NONE':
		invert.select = select;
	invert.line = line;
	os.system('rm -r '+mapname)
	os.system('rm -r '+beamname)
	invert.map = mapname
	invert.beam = beamname
	invert.options = options
	invert.slop = 0.5
	invert.stokes = 'ii'
	invert.imsize = imsize
	invert.cell = 4
	invert.robust= robust 
	tout = invert.snarf();

def clean(mapname, beamname, modelname, maskname=None, cutoff=0.0, niters=1000):
	clean = mirexec.TaskClean()
	clean.map = mapname;
	clean.beam = beamname;
	clean.cutoff = cutoff;
	if maskname!=None:
		clean.region='mask('+maskname+')';
		clean.niters = niters
	else:
		clean.niters = niters
	os.system('rm -r '+modelname);
	clean.out = modelname; 
	clean.snarf()


def restor(mapname, beamname, modelname, imname):
	os.system('rm -r '+imname)
	restor = mirexec.TaskRestore()
	restor.beam = beamname;
	restor.map = mapname
	restor.model = modelname
	restor.out = imname
	restor.snarf()

def maths(imname, cutoff, maskname):
	os.system('rm -r '+maskname);
	maths = mirexec.TaskMaths()
	maths.exp = imname;
	maths.mask = imname+'.gt.'+str(cutoff);
	maths.out = maskname;
	maths.snarf()
