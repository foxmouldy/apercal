#!/usr/bin/python
# Bradley Frank, ASTRON, 2015
import mirexec
import pylab as pl
from optparse import OptionParser
import sys
from ConfigParser import SafeConfigParser
import imp
from apercal import mirexecb 
import threading 
import time
import subprocess

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

def getimmax(image):
	imstat = mirexec.TaskImStat()
	imstat.in_ = image;
	imstats = imstat.snarf();
	immax = float(imstats[0][10][51:61]);
	imunits = imstats[0][4];
	return immax, imunits

def invertr(params):
	invert = mirexec.TaskInvert()
	invert.vis = params.vis
	invert.select = params.select
	invert.line = params.line
	shrun('rm -r '+params.map)
	shrun('rm -r '+params.beam)
	invert.map = params.map
	invert.beam = params.beam
	invert.options = params.options
	invert.slop = params.slop
	invert.stokes = params.stokes
	invert.imsize = params.imsize
	invert.cell = params.cell
	invert.fwhm = params.fwhm
	invert.robust= params.robust 
	tout = invert.snarf()
	return tout

def clean(params):
	clean = mirexec.TaskClean()
	clean.map = params.map
	clean.beam = params.beam
	clean.cutoff = params.cutoff
	if params.mask!=None:
		clean.region='mask('+params.mask+')'
		clean.niters = params.niters 
	else:
		clean.niters = 1000
	shrun('rm -r '+params.model)
	clean.out = params.model 
	tout = clean.snarf()
	return tout

def restor(params, mode='clean'):	
	restor = mirexec.TaskRestore()
	restor.beam = params.beam
	restor.map = params.map
	restor.model = params.model
	if mode!='clean':
		restor.out = params.residual
		restor.mode = 'residual'
	else:
		restor.out = params.image
		restor.mode = 'clean'

	shrun('rm -r '+restor.out)
	tout = restor.snarf()

def image(settings, i=0, **kwargs):
	params = settings.get('image')
	for k in kwargs:
		setattr(params, k, kwargs[k])
	if type(settings.get('selfcal', 'vis'))!=str:
		for v in settings.get('selfcal', 'vis'):
			params.vis = settings.get('data', 'working') + settings.get('selfcal', 'pointing') + '/' + v
			print params.vis
			params.map = params.vis+'_map'+str(i)
			params.beam = params.vis+'_beam'+str(i)
			params.image = params.vis+'_image'+str(i)
			params.mask = params.vis+'_mask'+str(i)
			params.residual = params.vis+'_residual'+str(i)
			invertr(params)
			clean(params)
			restor(params)
			restor(params, mode='residual')
	else:
		params.vis = settings.get('data', 'working') +  settings.get('selfcal', 'pointing') + '/' + settings.get('selfcal', 'vis')
		print params.vis
		params.map = params.vis+'_map'+str(i)
		params.beam = params.vis+'_beam'+str(i)
		params.image = params.vis+'_image'+str(i)
		params.mask = params.vis+'_mask'+str(i)
		params.residual = params.vis+'_residual'+str(i)
		invertr(params)
		clean(params)
		restor(params)
		restor(params, mode='residual')
	return params

def get_params(configfile=None):
	if configfile!=None:
		config_parser = SafeConfigParser()
		config_parser.read(configfile)
		params = Bunch()
		for p in config_parser.items('selfcal'):
			setattr(params, p[0], p[1])
		return params
