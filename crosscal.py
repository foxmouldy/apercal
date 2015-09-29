#Monday, 28 September 2015

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
logger = logging.getLogger('crosscal')

def dummy(message1, message2):
    logger.info(message1)
    logger.debug(message2)

def calcals(settings=None):
    '''
    Does MFCAL on the calibrator visibilities provided, for all the calibrators in the
    directory.
    Changes into the working directory, and does MFCAL on all the calibrator files in there.
    '''
    # Setting up and exception handling.
    logger = logging.getLogger('calcals')
    logger.info("CALCALS: MFCALS on all Calibrator Visibilities")
    if settings is None:
        logger.error("Settings Not Provided!")
        sys.exit(0)

    params = settings.get('mfcal')
    try:
        os.chdir(settings.get('data', 'working'))
        logger.info("Moved to path "+settings.get('data', 'working'))
    except:
        logger.error("Error: path does not exist!")
        sys.exit(0)
    # Get the name of the calibrator files
    uvfiles = settings.get('data', 'cals')
    # Repeat MFCAL for each of the calibrator files.
    for v in uvfiles:
        output = lib.masher(task='mfcal', refant=params.refant, vis=v,
                interval=params.interval, edge=params.edge,
                select='"'+params.select+'"')
        logger.info("Completed MFCAL on "+v)
    logger.info("CALCALS Done!")

def cal2srcs(settings=None):
    '''
    Copies the gains from the cal2copy visibility to the source visibilities defined in
    settings.get('data', 'srcs')
    '''
    logger = logging.getLogger('cal2srcs')
    # Initial Exception Handling 
    logger.info("CAL2SRCS: Module to copy the gain table from a calibrator to the source visibilities")
    if settings is None:
        logger.error("Settings Not Provided!")
        sys.exit(0)

    # Get the settings, check that the working directory is present and, if so, move to
    # it. 

    try:
        os.chdir(settings.get('data', 'working'))
        logger.info("Moved to path "+settings.get('data', 'working'))
    except:
        logger.error("Error: path does not exist!")
        sys.exit(0)

    # Define local variables to match those in params for use in the module.  

    params = settings.get('data')
    cal2copy = params.cal2copy
    srcs = lib.basher('ls -d '+params.working+params.calprefix+'*.uv')
    srcs = srcs[0].split('\n')[0:-1]

    # Loop over all the source visibilities, updating the header and copying the gains over as
    # we go.
    for s in srcs:

        logger.debug("PUTHD: Adding /restfreq=1.420405752 to "+s)
        o = lib.masher(task='puthd', in_=s+'/restfreq', value='1.420405752')
        
        logger.debug('PUTHD: Adding /interval=1.0 to '+s)
        o = lib.masher(task='puthd', in_=s+'/interval', value='1.0', type='double')

        logger.info('GPCOPY: Copying gain tables from '+cal2copy+' to '+s)
        o = lib.masher(task='gpcopy', vis=cal2copy, out=s)
    logger.info("CAL2SRCS: Appears to have ended successfully.")

def source_split(settings=None):
    '''
    This splits the source files src1.uv, src2.uv, src3.uv, ..., into a visibility file per source.
    '''
    logger = logging.getLogger("source_split")
    if settings is None:
        logger.error("Settings not provided!")
        sys.exit(0)
    try:
        os.chdir(settings.get('data', 'working'))
        logger.info("Moved to path "+settings.get('data', 'working'))
    except:
        logger.error("Error: path does not exist!")
        sys.exit(0)
    vises = settings.get('data', 'srcprefix')+'*.uv'
    try:
        sources = lib.get_source_names(settings.get('data', 'srcs')[0])
    except:
        logger.critical("Source file not found?")
        sys.exit(0)
    outvises = ''
    for s in sources:
        outvis = s+'.uv'
        if not os.path.exists(outvis):
            lib.masher(task='uvcat', vis=vises, select="'source("+s+")'", out=outvis)
            outvises+=outvis+';'
        else:
            logger.error(outvis+" already exists!")
            break
    settings.set('data', srcsplit=outvises[0:-1])
    logger.info("source_split: appears to have ended successfully.")

def subband_split(settings=None, hanning=False):
    '''
    Sometimes observations of multiple sources are split chronologically into a few visibility
    files - e.g. for mosaics. This module splits the source <src> out of the visibility <vis>
    and produces an output <src>.UV.
    Uses the MIRIAD task UVSPLIT with options=nowindow.
    Uses UVCAL to do Hanning smoothing if hanning=True (default is no Hanning smoothing)
    '''
    # 1: Report the name of the module, and check that settings and other variables have
    # been provided.
    logger = logging.getLogger('subband_split')
    logger.info("Subband Split: Source Splitting")
    logger.warn("I will clobber your old files. Be warned!")
    lib.query_yes_no("Do you really want to proceed?")
    logger.info("Log messages about files found/overwritten is available on the DEBUG level.")
    if settings is None:
        logger.error("Inputs missing!")
        sys.exit(0)
    # 2: Get the settings, check that the working directory is present and, if so, move to
    # it. 

    # There are two possibilities here. First, a single visibility is given, and this needs to
    # be split into its constituents. Second, split several visibility files into their
    # constituents using the settings object.
    
    if settings is None:
        logger.error("Settings not found!")
        sys.exit(0)

    try:
        os.chdir(settings.get('data', 'working'))
        logger.info("Moved to path "+settings.get('data', 'working'))
    except:
        logger.error("Error: path does not exist!")
        sys.exit(0)

    path2vis = settings.get('data', 'working') 

    for vis in settings.get('data', 'srcsplit'):
        # Now we're going to sort these files in a directory structure.
        logger.info("Attempting to split "+path2vis+vis)
        text_output = lib.masher(task='uvsplit', vis=vis, options='clobber')
        for t in text_output.split('\n'):
            if "Creating" in t:
                filename = t.replace('Creating ', '').replace(' ', '')
                f = filename.split('.')
                outdir = f[0]+'/'+f[1]

                if os.path.exists(path2vis+outdir+'/vis'):
                    logger.debug(path2vis+outdir+'/vis'+" exists. I'm going to remove this.")
                    lib.basher('rm -r '+path2vis+outdir+'/vis')
                settings.set(f[0], f[1], path2vis+outdir)
                # Make the first level
                if os.path.exists(path2vis+f[0]) is False:
                    logger.info('Making '+f[0])
                    lib.basher("mkdir "+f[0])
                else:
                    logger.debug('Found '+f[0])
                # Make the second level
                if os.path.exists(path2vis+outdir) is False:
                    logger.info("Making "+f[1])
                    lib.basher("mkdir "+outdir)
                else:
                    logger.debug("Found "+f[1])
                # Move the original file into vis
                # Hanning option
                if hanning==True:
                    logger.info("Hanning selected")
                    logger.info("Using UVCAL to do Hanning smoothing on "+filename+" to make "+outdir+'/vis')
                    try:
                        lib.masher(task='uvcal', options='hanning', out=outdir+'/vis')
                    except:
                        lib.error("Task UVCAL Failed")
                else:
                    logger.debug("No Hanning")
                    logger.info("Moving "+filename+" to "+outdir+'/vis')
                    lib.basher("mv "+filename+" "+outdir+'/vis')

    logger.info("subband_split: Appears to have ended successfully.")


def ms2uv(settings=None):
    '''
    ms2uv(settings)
    Function that converts MS to MIRIAD UV files, also does Tsys correction.
    Loops over all calfiles and srcfiles.
    '''
    logger = logging.getLogger('ms2uv')
    logger.info('ms2uv: Converting MS files to MIRIAD UV files')
    if settings is None:
        logger.error("Settings not found!")
        sys.exit(0)
    # First, do the calfiles.
    
    try:
        os.chdir(settings.get('data', 'rawdata'))
        logger.info("Moved to path "+settings.get('data', 'rawdata'))
    except:
        logger.error("Error: path does not exist!")
        sys.exit(0)

    inpath = settings.get('data', 'rawdata')
    outpath = os.path.relpath(settings.get('data', 'working'), inpath)

    calprefix = settings.get('data', 'calprefix')
    calfiles = settings.get('data', 'calfiles')
    cals = ''
    for i in range(0, len(calfiles)):
        # NOTE: MS2UVFITS: MS -> UVFITS (in rawdata)
        msfile = calfiles[i]
        logger.info("Converting "+msfile)
        lib.ms2uvfits(ms = msfile)
        uvfitsfile = msfile.replace('.MS', '.UVF')
        #uvfile = settings.get('data', 'working') + calprefix + str(i+1) + '.uv'
        uvfile = calprefix + str(i+1) + '.uv'
        cals+=uvfile+";"
        # NOTE: UVFITS: rawdata/UVFITS -> working/UV
        lib.importuvfitsys(uvfitsfile, outpath+'/'+uvfile)
    settings.set('data', cals=cals[0:-1])

    # Second, do the srcfiles.
    srcprefix = settings.get('data', 'srcprefix')
    srcfiles = settings.get('data', 'srcfiles')
    srcs = ''
    for i in range(0, len(srcfiles)):
        # NOTE: MS2UVFITS: MS -> UVFITS (in rawdata)
        msfile = srcfiles[i]
        logger.info("Converting "+msfile)
        lib.ms2uvfits(ms = msfile)
        uvfitsfile = msfile.replace('.MS', '.UVF')
        uvfile = srcprefix + str(i+1) + '.uv'
        srcs+= uvfile+';'
        # NOTE: UVFITS: rawdata/UVFITS -> working/UV
        lib.importuvfitsys(uvfitsfile, outpath+'/'+uvfile)
     
    settings.set('data', srcs=srcs[0:-1])
    logger.info('ms2uv: Appears to have ended successfully.')
