"""
mirplot
An apercal utility to embed MIRIAD plots in an IPython Notebook.

The visualizer functions are:
mirplot.uvplt(vis=None, tempdir="~/", **kwargs)
mirplot.uvspec(vis=None, tempdir="~/", **kwargs
mirplot.imview(im=None, tempdir="~/", **kwargs)
    Uses CGDISP
mirplot.gpplt(vis=None, tempdir="~/", **kwargs)

You need to provide the vis and tempdir keywords. 

Additional keyword arguments which are commonly used by these MIRIAD tasks can be passed as follows:
mirplot.uvspec(vis=<yourvis>, tempdir=<somedir>, nxy='2,2', options='avall', stokes='xx', interval='10000')
Each argument (even numbers and integers) need to be strings - e.g. the interval keyword.
"""

# Author: Brad Frank

import pylab as pl
from apercal import lib
import io
from IPython.display import HTML
from IPython.display import Image
from base64 import b64encode
import subprocess
import sys
import os



def check_tempdir(tempdir=None):
    '''
    check_tempdir
        Helper function to validate tempdir
    '''
    if tempdir==None:
        print "Setting tempdir to /home/<user>/"
        print "This could dump a **HUGE** amount of files into /home/<user>/"
        answer = query_yes_no("Are you sure you want to continue?")
        if answer==True:
            tempdir = os.path.expanduser('~')
            return tempdir
        else:
            sys.exit("Make a new tempdir - I suggest /home/<user>/mirtemp/")
    else:
        check = os.path.isdir(tempdir)
        if check!=True:
            sys.exit("tempdir does not exist!")
        else:
            return tempdir

def check_file(f=None):
    '''
    check_file
        Helper function to check that f exists.
    '''
    if f!=None:
        check = os.path.isdir(f)
        if check==False:
            sys.exit("File not found!")
        else:
            return f
    else:
        sys.exit("File not specified!")
        
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def videcon(outname, tempdir = "/home/frank/", r=2.):
    '''
    Uses avconv to make the video!
    '''
    o, e = shrun("avconv -r "+str(r)+" -f image2 -i "+tempdir+"pgplot%d.gif -vcodec libx264 -y "+outname)
    
def shrun(cmd):
	'''
	shrun: shell run - helper function to run commands on the shell.
	'''
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        	stderr = subprocess.PIPE, shell=True)
	out, err = proc.communicate()
	# NOTE: Returns the STD output.
	return out, err

def vidshow(U=None, tempdir="/home/frank/", vidname="some_vid", r=2):
    '''
    vidshow: merge gifs into m4v and construct the HTML embedder for IPython
    '''
    gifs = []
    
    shrun("rm "+tempdir+"*gif*")
    
    U, e = shrun('ls pgplot.gif*')
    U = U.split('\n')
    for i in range(0,len(U)):
        uin  = "pgplot.gif_"+str(i+1)
        uout = "pgplot"+str(i+1)+".gif"
        shrun('mv '+uin+' '+tempdir+'/'+uout)
    shrun("mv pgplot.gif "+tempdir+ "/pgplot1.gif")
    
    videcon(tempdir+"/"+vidname, tempdir=tempdir, r=r)

    # Delete the intermediate gifs
    shrun("rm "+tempdir+"/pgplot*.gif")
    video = io.open(tempdir+"/"+vidname, "rb").read()
    video_encoded = b64encode(video)
    video_tag = '<video controls alt="test" src="data:video/x-m4v;base64,{0}">'.format(video_encoded)
    return HTML(data=video_tag)

def vembed(video=None):
	'''
	vembed(video=None) - Video Embedder for IPython Notebooks. Uses the HTML module to embed an
	mp4 encoded video. 
	'''
	if video!=None:
		video = io.open(video, "rb").read()
		video_encoded = b64encode(video)
		video_tag = '<video controls alt="test" src="data:video/x-mp4;base64,{0}">'.format(video_encoded)
		return HTML(data=video_tag)
	else: 
		print "Please provide video to embed"

def uvplt(vis=None, r=2., tempdir = "/home/frank/", **kwargs):
    '''
    IPython Video Embedder for UVPLT. 
    vis = Full path of vis to be plotted
        No Default
    tempdir = temporary directory to store the video and plot files. 
        Default is the ~/, but this is not recommended.
    r = plots per second [2]
        Please specify vis and any of the following:
                2pass,all,avall,average,axis,equal,flagged,hann,hours,inc,
                line,log,mrms,nanosec,nxy,options,rms,run,scalar,seconds,
                select,set,size,source,stokes,unwrap,vis,xrange,yrange
    '''
    # Check that vis exists
    vis = check_file(vis)
    
    # Check that the tempdir exists
    tempdir = check_tempdir(tempdir)
    
    # Switch to the path
    path = os.path.split(vis)
    os.chdir(path[0])
    
    # Use mirrun to run uvplt
    U, E = lib.mirrun(task = 'uvplt', vis = path[1], device='/gif', **kwargs)
    if len(E)>1:
        sys.exit("UVPLT Oops: "+E)
    # Get the output from vidshow
    HTML = vidshow(U=U, tempdir=tempdir, vidname="uvplt.m4v", r=r)
    
    # Return the HTML object to the IPython Notebook for Embedding
    return HTML
   
def uvspec(vis=None, r=2., tempdir = "/home/frank/", **kwargs):
    '''
    IPython Video Embedder for UVSPEC. 
    vis = Full path of vis to be plotted
    r = plots per second [2]
        Please specify vis and any of the following:
                2pass,all,avall,average,axis,equal,flagged,hann,hours,inc,
                line,log,mrms,nanosec,nxy,options,rms,run,scalar,seconds,
                select,set,size,source,stokes,unwrap,vis,xrange,yrange
    '''
    # Check that vis exists
    vis = check_file(vis)
    
    # Validate the tempdir
    tempdir = check_tempdir(tempdir)
    
    # Switch to the path
    path = os.path.split(vis)
    os.chdir(path[0])
    
    # Make the plots using uvspec
    U, E = lib.mirrun(task = 'uvspec', vis=path[1], device='/gif', **kwargs)
    if len(E)>1:
        sys.exit("UVSPEC Oops: "+E)
    
    # Embed the plots
    HTML = vidshow(U=U, tempdir=tempdir, vidname="uvspec.m4v", r=r)
    
    return HTML

def gpplt(vis=None, r=2, tempdir = "/home/frank/", **kwargs):
    '''
    IPython Video Embedder for GPPLT. 
    vis = Full path of vis to be plotted
    r = plots per second [2]
        Please specify vis and any of the following:
         log yaxis options nxy select yrange 
         yaxis: amp, phase, real, imag
         options: gains, xygains, xbyygains, polarization, 
            2polarization, delays, speccor, bandpass, dots, 
            dtime, wra
    
    '''
    # First, check that vis exists
    vis = check_file(vis)
    
    # Check that tempdir exists
    tempdir = check_tempdir(tempdir)
    
    # Switch to the path
    path = os.path.split(vis)
    os.chdir(path[0])
    
    # Use GPPLT to make the plots
    U, E = lib.mirrun(task = 'gpplt', device='/gif', vis = path[1], **kwargs)
   
    # Get the output from vidshow
    HTML = vidshow(U=U, tempdir=tempdir, vidname="gpplt.m4v", r=r)
    
    # Return the HTML object to IPython Notebook for Embedding
    return HTML
        
def imview(im=None, r=2, tempdir = None, typ='pixel', slev = "p,1", levs="2e-3", 
        rang="0,2e-3,lin", nxy="1,1", labtyp = "hms,dms", options="wedge,3pixel", **kwargs):
    '''
    IPython Video Embedder for CGDISP.
    im = Full path of image to be plotted
    r = plots per second [2]
        Please specify vis and any of the following:
         
        type slev levs rang (not range!) nxy labtyp options
    '''
    # Check that the image exists
    im = check_file(im)
    
    # Check that the tempdir exists
    tempdir = check_tempdir(tempdir)
    
    # If we've gotten this far, then it means that we've passed the test.
    
    # Switch to the path
    path = os.path.split(im)
    os.chdir(path[0])
    
    # Use CGDISP to make the plots
    # This uses the generic lib.mirrun() method, so you don't need anything special to run this.
    U, E = lib.mirrun(task='cgdisp', device='/gif', in_ = path[1], type=typ, slev=slev, levs=levs, range=rang,
                   nxy=nxy, labtyp=labtyp, **kwargs)

    # Get the output from vidshow!
    HTML = vidshow(tempdir=tempdir, vidname="imview.m4v", r=r)

    # Return the HTML object to IPython Notebook for Embedding!
    return HTML

def imhist(im=None, tempdir = '/home/frank/', device='/gif'):
	'''
	Pops up an histogram of the image.
	'''
	if im!=None:

		out, err = shrun("imhist in="+im+" device="+device)
		shrun("mv pgplot.gif "+tempdir+'imhist.gif')
		i = Image(filename = tempdir + 'imhist.gif')
		out, err = shrun("imhist in="+im)
		print out, err
		return i
	else:
		print "Error: im argument missing."
