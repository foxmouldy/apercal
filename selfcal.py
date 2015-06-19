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
import os

def maths(image, cutoff, mask):
	os.system('rm -r '+mask)
	maths = mirexec.TaskMaths()
	maths.exp = "<"+image+">"
	maths.mask = "<"+image+">"+".gt."+str(cutoff)
	maths.out = mask
	tout = maths.snarf()

def shrun(cmd):
	'''
	shrun: shell run - helper function to run commands on the shell.
	'''
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

def get_cutoff(settings, cutoff=1e-3):
	'''
	This uses OBSRMS to calculate the theoretical RMS in the image.
	'''
	obsrms = mirexecb.TaskObsRMS()

	params = settings.get('obsrms')
	for p in params.__dict__:
		setattr(obsrms, p, params[p])
	rmsstr = obsrms.snarf()
	#print "OBSRMS Output"
	#print ("\n".join(map(str, rmsstr[0])))
	rms = rmsstr[0][3].split(";")[0].split(":")[1].split(" ")[-2]
	noise = float(params.nsigma)*float(rms)/1000.
	if cutoff > noise:
		return cutoff
	else:
		return noise


def invertr(params):
    invert = mirexec.TaskInvert()
    invert.vis = params.vis
    if params.select.upper()!='NONE':
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
	print "IMAGE"
	params = settings.get('image')
	for k in kwargs:
		setattr(params, k, kwargs[k])
	if type(settings.get('selfcal', 'vis'))!=str:
		for v in settings.get('selfcal', 'vis'):
			os.chdir(settings.get('data', 'working'))
			params.vis = settings.get('selfcal', 'pointing') + '/' + v
			print "Imaging ", params.vis
			params.map = params.vis+'_map'+str(i)
			params.beam = params.vis+'_beam'+str(i)
			params.image = params.vis+'_image'+str(i)
			params.mask = params.vis+'_mask'+str(i)
			params.model = params.vis+'_model'+str(i)
			params.residual = params.vis+'_residual'+str(i)
			invertr(params)
			immax, imunits = getimmax(params.map)
			maths(params.map, immax/3, params.mask)
			params.cutoff = get_cutoff(settings, cutoff=immax/30)
			clean(params)
			restor(params)
			restor(params, mode='residual')
	else:
		os.chdir(settings.get('data', 'working'))
		params.vis = settings.get('selfcal', 'pointing') + '/' + settings.get('selfcal', 'vis')
		print params.vis
		params.map = params.vis+'_map'+str(i)
		params.beam = params.vis+'_beam'+str(i)
		params.image = params.vis+'_image'+str(i)
		params.mask = params.vis+'_mask'+str(i)
		params.model = params.vis+'_model'+str(i)
		params.residual = params.vis+'_residual'+str(i)
		invertr(params)
		immax, imunits = getimmax(params.map)
		maths(params.map, immax/3, params.mask)
		params.cutoff = get_cutoff(settings, cutoff=immax/30)
		clean(params)
		restor(params)
		restor(params, mode='residual')
	print "Done!"
	return params

def selfcal(settings):
    '''
    selfcal(settings)
        Utility for running selfcal on one more visibility files. 
        This cd's to your working directory and selfcals the visibility as defined by the vis and pointing
        keywords in the selfcal section of your settings file. 
    '''
    selfcal = mirexec.TaskSelfCal()
    params = settings.get('selfcal')
    for p in params.__dict__:
        setattr(selfcal, p, params[p])
    if params.clip!='':
        selfcal.clip = params.clip
    os.chdir(settings.get('data', 'working'))
    print "SELFCAL: ", settings.get('selfcal', 'vis')
    if type(settings.get('selfcal', 'vis'))!=str:
        for i in range(0, len(settings.get('selfcal', 'vis'))):
            selfcal.vis = settings.get('selfcal', 'pointing') + '/' + settings.get('selfcal','vis')[i]
            print "SELFCAL on ", selfcal.vis
            selfcal.model = settings.get('selfcal', 'pointing') + '/' + settings.get('selfcal', 'model')[i]
            tout = selfcal.snarf()
    else:
        selfcal.vis = settings.get('selfcal', 'pointing') + '/' + settings.get('selfcal', 'vis')
        print "SELFCAL on ", selfcal.vis
        selfcal.model = settings.get('selfcal', 'pointing') + '/' + settings.get('selfcal', 'model')
        tout = selfcal.snarf()
    print "DONE"
    return tout

def get_params(configfile=None):
	if configfile!=None:
		config_parser = SafeConfigParser()
		config_parser.read(configfile)
		params = Bunch()
		for p in config_parser.items('selfcal'):
			setattr(params, p[0], p[1])
		return params
