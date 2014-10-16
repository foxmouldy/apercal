import pylab as pl
import time
import os
import threading
import sys
import mirexec
from apercal import mirexecb
from optparse import OptionParser


def getimmax(imname):
	imstat = mirexec.TaskImStat()
	imstat.in_ = imname;
	imstats = imstat.snarf();
	immax = float(imstats[0][10][51:61]);
	imunits = imstats[0][4];
	return immax, imunits


def pgflag(config):
	pgflag = mirexecb.TaskPGFlag();
	pgflag.vis = config.get('files', 'vis')
	pgflag.stokes = config.get('settings', 'stokes')
	pgflag.flagpar = config.get('flag', 'flagpar')
	pgflag.options = 'nodisp';
	pgflag.command = '<';
	pgflag.snarf();

def calcals(config):
	mfcal = mirexec.TaskMfCal();
	for p in config.items('mfiles')[0:-1]:
		mfcal.vis = config.get('mfiles', p[0]);
		mfcal.edge = config.get('mfcal', 'edge')
		mfcal.line = config.get('mfcal', 'line')
		mfcal.interval = 1000000.;
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
		I = p[0]
		O = config.get('mfiles', p[0])
		flags = config.get('flag', 'flags')
		wsrtfits = mirexecb.TaskWSRTFits()
		wsrtfits.in_ = 
		wsrtfits.out = O
		wsrtfits.velocity = 'optbary'
		attsys = mirexeb.TaskAttsys()
		attsys.vis = O
		attsys.optons='apply'
		attsys.out = '_tmp_vis'
		cmd = 'rm -r '+O;
		os.system(cmd);
		cmd = 'mv _tmp_vis '+O;
		os.system(cmd);
		for f in flags:
			uvflag = mirexec.TaskUVFlag();
			uvflag.vis = O;
			uvflag.select = f
			uvflag.flagval = 'flag';
			uvflag.snarf();

def uvlin(config):
	vis = config.get('mfiles', 'src')
	chans = config.get('settings', 'chans')
	order = int(config.get('settings', 'order'))
	mode = config.get('settings', 'mode')
	out = config.get('mfiles', 'src_line')
	uvlin = mirexecb.TaksUVLin()
	uvlin.vis = vis
	uvlin.chans = chans
	uvlin.order = order
	uvlin.mode = mode
	uvlin.out = out
	uvlin.snarf()

def imager(config)
	vis = config.get('imaging', 'vis')
	select = config.get('imaging', 'select')
	mapname = config.get('imaging', 'map')
	beamname = config.get('imaging' 'beam')
	imname = config.get('imaging', 'image')
	modelname = config.get('imaging', 'model')
	maskname = config.get('imaging', 'maskname')
	cutoff = config.get('imaging', 'cutoff')
	line = config.get('imaging', 'line')
	invertr(vis, select, mapname, beamname);
	clean(mapname, beamname, modelname)
	restor(mapname, beamname, modelname, imname);
	immax, imunits = getimmax(imname);
	maths(imname, immax/10, maskname);
	clean(mapname, beamname, modelname, maskname, cutoff)
	restor(mapname, beamname, modelname, imname);

def invertr(vis, select, mapname, beamname, robust=-2.0, line=''):
	invert = mirexec.TaskInvert()
	invert.vis = vis;
	invert.select = select;
	invert.line = line;
	os.system('rm -r '+mapname)
	os.system('rm -r '+beamname)
	invert.map = mapname
	invert.beam = beamname
	invert.options = 'double,mfs';
	invert.slop = 0.5
	invert.stokes = 'ii'
	invert.imsize = 1500
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
