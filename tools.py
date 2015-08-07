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
    params = settings.get('image')
    
    # Move to the correct directory
    full_path = settings.full_path()
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
    O, E = mirrun(task='invert', vis = '../'+params.vis, line=params.line, 
               select=params.select, slop=params.slop, map = 'map', beam = 'beam', 
               options = params.options, stokes=params.stokes, imsize=params.imsize,
               cell = params.cell, robust=params.robust)
    print O, E

def clean(settings):
    '''
    '''
    # Get the relevant settings
    params = settings.get('image')
    
    # Move to the correct directory
    full_path = settings.full_path()
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

    # Print the output    
    print O, E                    
    
    # Cleanup
    shrun('rm -r image')
    
    # RESTOR to make the image or residual
    O, E = mirrun(task='restor', map = 'map', beam = 'beam', 
                  model = 'model', out='image') 
    shrun('rm -r residual')
    O, E = mirrun(task='restor', map = 'map', beam = 'beam', 
                  model = 'model', out='residual', mode = 'residual') 
    # Print the output
    print O, E    

    
def maths(settings):
    '''
    Module to make the mask. 
    '''
    params = settings.get('image')
    
    full_path = settings.full_path()
    
    if not os.path.exists(full_path):
        o, e = shrun('mkdir '+full_path)
        print o, e
        os.chdir(full_path)
        print 'making path'
    else:
        os.chdir(full_path)
    
    shrun('rm -r mask')
    
    O, E = mirrun(task='maths', exp='image', mask='image.gt.'+str(params.mcutoff), out='mask')
    print O, E
    
    #maths = mirexec.TaskMaths()
    #maths.exp = '<'+image+'>'
    #maths.mask = '<'+image+'>'+".gt."+str(cutoff)
    #maths.out = mask
    #tout = maths.snarf()
    
    
    
    
def get_params(config_parser, section):
    params = Bunch()
    for p in config_parser.items(section):
        setattr(params, p[0], p[1])
    return params

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