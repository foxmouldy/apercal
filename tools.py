import mirexecb
import mirexecb as mirexec
from ConfigParser import SafeConfigParser
import subprocess
import mynormalize
import pylab as pl
import os 
import sys

def invertr(settings):
    '''
    Function to do invert on a visibility file.
    '''
    # Get the relevant settings
    print "Getting the IMAGE settings"
    params = settings.get('image')
    # Get the vis file from the data settings:
    vis = settings.get('data', 'vis')
    
    # Move to the correct directory
    full_path = settings.full_path()
    print "Operating in "+full_path

    if not os.path.exists(full_path):
        o, e = shrun('mkdir '+full_path)
        print o, e
        os.chdir(full_path)
        print 'making path'
    else:
        os.chdir(full_path)
    
    # Cleanup                
    shrun('rm -r map')
    shrun('rm -r beam')
    
    # Run the taskl
    O, E = mirrun(task='invert', vis = '../'+vis, line=params.line, 
               select=params.select, slop=params.slop, map = 'map', beam = 'beam', 
               options = params.options, stokes=params.stokes, imsize=params.imsize,
               cell = params.cell, robust=params.robust)
    print O, E

def exceptioner(O, E):
    '''
    exceptioner(O, E) where O and E are the stdout outputs and errors. 
    A simple and stupid way to do exception handling. 
    '''
    if len(E)>0:
        print O
        print "\n"
        print "Possible Error"
        print E
    else:
        print "Seems to have ended normally"
        print O+"\n"
        print E

def clean(settings):
    '''
    Module to clean a visibility set. 
    '''
    # Get the relevant settings
    print "Getting the IMAGE settings"

    params = settings.get('image')
    
    # Move to the correct directory
    full_path = settings.full_path()
    print "Operating in "+full_path
    if not os.path.exists(full_path):
        o, e = shrun('mkdir '+full_path)
        print o, e
        os.chdir(full_path)
        print 'making path'
    else:
        os.chdir(full_path)
    
    # Cleanup                
    shrun('rm -r model')
    
    # CLEAN
    if not os.path.exists(full_path+'mask'):
        O, E = mirrun(task='clean', map = 'map', beam = 'beam', niters='10000', 
                      out = 'model', cutoff = params.cutoff)
    else:
        O, E = mirrun(task='clean', map = 'map', beam = 'beam', niters='10000', 
                      out = 'model', cutoff = params.cutoff, region='"mask(mask)"')

    # Exception handling, Print the output    
    exceptioner(O, E)
    
    # Cleanup
    shrun('rm -r image')
    
    # RESTOR to make the image or residual
    O, E = mirrun(task='restor', map = 'map', beam = 'beam', 
                  model = 'model', out='image') 
    shrun('rm -r residual')
    O, E = mirrun(task='restor', map = 'map', beam = 'beam', 
                  model = 'model', out='residual', mode = 'residual') 
    # Print the output
    exceptioner(O, E)    
    
def maths(settings):
    '''
    Module to make the mask. 
    '''
    print "Getting the IMAGE parameters"
    params = settings.get('image')
    
    full_path = settings.full_path()
    print "Operating in "+full_path

    if not os.path.exists(full_path):
        o, e = shrun('mkdir '+full_path)
        print o, e
        os.chdir(full_path)
        print 'making path'
    else:
        os.chdir(full_path)
    
    print "Removing old mask..."
    shrun('rm -r mask')
    
    O, E = mirrun(task='maths', exp='image', mask='image.gt.'+str(params.mcutoff), out='mask')
    exceptioner(O, E)
    
def get_params(config_parser, section):
    params = Bunch()
    for p in config_parser.items(section):
        setattr(params, p[0], p[1])
    return params

def move2dir(path):
    '''
    move2dir(path)
    Check if the path exists. If not, then make the path. If so, then change to it. 
    '''
    if not os.path.exists(path):
        o, e = shrun('mkdir '+path)
        print o, e
        os.chdir(path)
        print 'making path'
    else:
        os.chdir(path)

def mirrun(task=None, verbose=False, **kwargs):
    '''
    mirrun - Miriad Task Runner
    Usage: mirrun(task='sometask', arg1=val1, arg2=val2)
    Example: mirrun(task='invert', vis='/home/frank/test.uv/', options='mfs,double', ...)
    Each argument is passed to the task through the use of the keywords. 
    '''
    if task!=None:
        argstr = " "
        for k in kwargs.keys():
            argstr += k + '=' + kwargs[k]+ ' '
        cmd = task + argstr
        out, err = shrun(cmd)        
        if verbose!=False:
               print cmd
               print out, err
        return out, err
    else:
        print "Usage = mirrun(task='sometask', arg1=val1, arg2=val2...)"

def selfcal(settings):
    '''
    Module to run selfcal
    '''
    
    print "Getting the SELFCAL parameters"
    params = settings.get('selfcal')
    
    vis = settings.get('data', 'vis')
    full_path = settings.full_path()
    
    print "Doing SELFCAL on: "+vis
    
    print "Operating in "+full_path
    if not os.path.exists(full_path):
        o, e = shrun('mkdir '+full_path)
        print o, e
        os.chdir(full_path)
        print 'making path'
    else:
        os.chdir(full_path)
        
    O, E = mirrun(task='selfcal', vis='../'+vis, model='model',
                  select='"'+params.select+'"', interval=params.interval, 
                  clip = params.clip, options=params.options, minants=params.minants, 
                  refant = params.refant, line=params.line)
    exceptioner(O, E)
    
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

def flag(settings):
	'''
	UVFLAG: Gets variables from settings.get('flag'). Flags settings.get('flag', 'flags') on 
	visibilities settings.get('flag', 'vis')
	'''
	vis = settings.get('flag', 'vis')
	flags = settings.get('flag', 'flags')
	for v in vis.split(','):
		for f in flags:
			o, e = mirrun(task='uvflag', vis=v, select=f, flagval='flag')
			exceptioner(o, e)
