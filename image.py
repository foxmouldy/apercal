#!/usr/bin/python
# Bradley Frank, ASTRON, 2015
# image.py
# This library contains modules for you to image visibilities.
import logging
from ConfigParser import SafeConfigParser
import pylab as pl
import os
import sys
import lib
logger = logging.getLogger('image')

###################################################
# IMAGING
###################################################
def mkim(vis=None, settings=None, deep=True):
    '''
    Main function that makes the image.
    '''
    logger = logging.getLogger('mkim')
    logger.info('mkim - imaging tool.')
    if vis is None or settings is None:
        logger.error("Please specify inputs!")
        sys.exit(0)
    # Split the path to vis
    path2vis = os.path.split(vis)[0]
    vis = os.path.split(vis)[1]
    if path2vis!='':
        try:
            os.chdir(path2vis)
            logger.info("Moved to path "+path2vis)
        except:
            logger.error("Error: Directory or vis does not exist.")
            sys.exit(0)
    outdir = settings.get('data', 'output')
    if os.path.exists(outdir):
        logger.info(outdir+" exists. Output will be dumped here. Old images will be removed." )
    else:
        logger.info(outdir+" does not exist. Making...")
        o = lib.basher("mkdir "+outdir)
    logger.info("Moving to "+outdir+". This makes things a little easier.")
    os.chdir(outdir)    
    # params = container for the output files, directories and imaging inputs
    params = make_outputs(vis, settings)
    if deep is True:
        # Deep Image
        logger.info("Deep Image")
        deep_image(params, settings)
    else:   
        # Standard Imaging
        logger.info("Standard Image")
        invertr(params)
        params.mask = "None"
        clean(params)
        restor(params)
    logger.info("Image done!")

def make_outputs(vis, settings):
    '''
    Add file attributes to the imaging bunch that gets extracted from the settings.
    '''
    params = settings.get('image')
    params.vis = '../'+vis
    params.image = 'image'
    params.residual = 'residual'
    params.map = 'map'
    params.beam = 'beam'
    params.mask = 'mask'
    params.model = 'model'
    return params

def deep_image(params, settings):
    '''
    deep_image - performs three iterations of imaging. 
    '''
    logger = logging.getLogger('deep_image')
    c1 = pl.linspace(float(params.c0), float(params.c0)+2.*float(params.dc), 3)
    c2 = c1*10.
    logger.info("Mask threshold: IMAX"+str(c1))
    logger.info("Clean threshold: IMAX/"+str(c2)+" or "+str(settings.get('obsrms','nsigma'))+"*noise")
    logger.info("Making Dirty Image")
    invertr(params)
    immax, imunits = getimmax(params.map)
    make_mask(params.map, immax/c1[0], params.mask)
    params.cutoff = get_cutoff(settings.get('obsrms'), cutoff=immax/c2[0])
    logger.info("CLEAN 1")
    clean(params)
    restor(params)
    immax, imunits = getimmax(params.image)
    make_mask(params.image, immax/c1[1], params.mask)
    params.cutoff = get_cutoff(settings.get('obsrms'), cutoff=immax/c2[1])
    logger.info("CLEAN 2")
    clean(params)
    restor(params)
    immax, imunits = getimmax(params.image)
    make_mask(params.image, immax/c1[2], params.mask)
    params.cutoff = get_cutoff(settings.get('obsrms'), cutoff=immax/c2[2])
    logger.info('CLEAN 3')
    clean(params)
    restor(params)
    restor(params, mode='residual')
    logger.info("DONE!")

def invertr(params):
    '''
    output = invertr(settings, spars)
    Runs MIRIAD's invert on spars.vis, using settings.get('image'). Returns the output from
    masher.
    
    '''
    vis = params.vis 
    #NOTE: Clean up
    out = lib.basher('rm -r '+params.map)
    out = lib.basher('rm -r '+params.beam)
    out = lib.masher(task='invert', vis=vis, select=params.select,
        line=params.line, map = params.map, beam=params.beam, options=params.options,
        slop=params.slop, stokes=params.stokes, imsize=params.imsize, cell=params.cell,
        fwhm=params.fwhm, robust=params.robust)

def clean(params):
    '''
    output = clean(params)
    Runs MIRIAD's clean, using standard settings.
    '''
    #NOTE: Cleanup
    logger = logging.getLogger('clean')
    o, e = lib.basher("rm -r "+params.model)
    if params.mask.upper()!='NONE':
        #NOTE: Use mask if provided. 
        out = lib.masher(task='clean', map=params.map, beam=params.beam,
            out=params.model, cutoff=params.cutoff,
            region="'mask("+params.mask+")'", niters=100000)
    else:
        #NOTE: Do a 'light' clean if no mask provided.
        logger.debug('Cleaning with 1000 iterations')
        out = lib.masher(task='clean', map=params.map, beam=params.beam,
            out=params.model, cutoff=params.cutoff, niters=1000)

def restor(params, mode='clean'):
    '''
    output = restor(params, mode='clean')
    Uses the MIRIAD task restor to restor a model image, creating either an image or a
    residual.
    '''
    if mode.upper()!="CLEAN":
        # Make the residual
        # Cleanup
        lib.basher('rm -r '+params.residual)
        out = lib.masher(task='restor', beam=params.beam, map=params.map,
            model=params.model, out=params.residual, mode='residual')
    else:
        # Make the image
        # Cleanup
        lib.basher('rm -r '+params.image)
        out = lib.masher(task='restor', beam=params.beam, map=params.map,
            model=params.model, out=params.image, mode=mode)

def make_mask(image, cutoff, mask):
    '''
    output = make_mask(image, cutoff, mask)
    Uses the MIRIAD task MATHS to make a threshold mask. The input <image> is thresholded with
    cutoff, and a <mask> is created.
    '''
    lib.basher("rm -r "+mask)
    lib.masher(task='maths', exp=image, mask=image+".gt."+str(cutoff), out=mask)

def get_cutoff(params, cutoff=1e-3):
    '''
    This uses OBSRMS to calculate the theoretical RMS in the image.
    '''
    out = lib.masher(task='obsrms', tsys=params.tsys, jyperk=params.jperk,
        freq=params.freq, theta=params.theta, nants=params.nants, bw=params.bw,
        inttime=params.inttime, antdiam=params.antdiam)
    rms = out.split('\n')[3].split(";")[0].split(":")[1].split(" ")[-2]
    noise = float(params.nsigma)*float(rms)/1000.
    if cutoff > noise:
        return cutoff
    else:
        #"cutoff < noise"
        return noise    

def getimmax(image):
    '''
    Module to compute the max in an image
    '''
    out = lib.masher(task='imstat', in_=image)
    immax = float(out.split('\n')[10][51:61])
    imunits = out.split('\n')[4]
    return immax, imunits


def selfcal(vis=None, settings=None):
    '''
    output = selfcal(vis, settings)
    Uses the MIRIAD task selfcal to do... well... selfcal. 
    '''
    logger = logging.getLogger('image.selfcal')
    if vis is None or settings is None:
        logger.error("vis or settings not provided!")
        sys.exit(0)
    logger.info("Using input settings to do selfcal on "+vis)
    path2vis = os.path.split(vis)[0]
    vis = os.path.split(vis)[1]
    if path2vis!='':
        try:
            os.chdir(path2vis)
            logger.info('Moved to path '+path2vis)
        except:
            logger.critical("Path not found.")
            sys.exit(0)
    params = settings.get('selfcal')
    model = settings.get('data', 'output')+'/model'
    if not os.path.exists(vis):
        logger.error(vis+' does not exist!')
        sys.exit(0)
    mirout = lib.masher(task='selfcal', vis=vis, select=params.select,
    	model=model, options=params.options, interval=params.interval,
    	line=params.line, clip=params.clip)
