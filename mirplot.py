from apercal import mirexecb
import io
from IPython.display import HTML
from base64 import b64encode
import subprocess

def videcon(outname, tempdir = "/home/frank/", r=2.):
	'''
	Uses avconv to make the video!
	'''
	shrun("avconv -r "+str(r)+" -f image2 -i "+tempdir+"pgplot%d.png -y -vcodec libx264 "+outname)

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

def vidshow(U=None, tempdir="/home/frank/", vidname="some_vid", r=2):

		# 2. Get and rename the pngs:
		pngs = []

		shrun("rm "+tempdir+"*png*")
		for i in range(0,len(U[1])):
			p = U[1][i].replace("PGPLOT /png: writing new file as ","")
			pngs.append(U[1][i].replace("PGPLOT /png: writing new file as ",""))
			shrun("mv "+p+" "+tempdir+"/pgplot"+str(i+2)+".png")
		shrun("mv pgplot.png "+tempdir+ "/pgplot1.png")
		
		videcon(tempdir+"/"+vidname, tempdir=tempdir, r=r)
		shrun("rm "+tempdir+"*png*")	
		#3: Plot the data
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
	r = plots per second [2]
	    Please specify vis and any of the following:
	            2pass,all,avall,average,axis,equal,flagged,hann,hours,inc,
	            line,log,mrms,nanosec,nxy,options,rms,run,scalar,seconds,
	            select,set,size,source,stokes,unwrap,vis,xrange,yrange
	'''
	if vis!=None:
		# 1: Make the plots
	        uvplt = mirexecb.TaskUVPlot ()
	        uvplt.vis = vis
	        for k in kwargs.keys():
	                setattr(uvplt, k, kwargs[k])
	        uvplt.device="/png"
	        U = uvplt.snarf()

		# 2. Get and rename the pngs:
		pngs = []

		shrun("rm "+tempdir+"*png*")
		for i in range(0,len(U[1])):
			p = U[1][i].replace("PGPLOT /png: writing new file as ","")
			pngs.append(U[1][i].replace("PGPLOT /png: writing new file as ",""))
			shrun("mv "+p+" "+tempdir+"/pgplot"+str(i+2)+".png")
		shrun("mv pgplot.png "+tempdir+ "/pgplot1.png")
		
		videcon(tempdir+"/uvplt.m4v", tempdir=tempdir, r=r)
		shrun("rm "+tempdir+"*png*")	
		#3: Plot the data
		video = io.open(tempdir+"uvplt.m4v", "rb").read()
		video_encoded = b64encode(video)
		video_tag = '<video controls alt="test" src="data:video/x-m4v;base64,{0}">'.format(video_encoded)
		return HTML(data=video_tag)
	else:
		print "Error: vis argument has to be explicitly specified"

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
	if vis!=None:
		# 1: Make the plots
	        uvspec = mirexecb.TaskUVSpec ()
	        uvspec.vis = vis
	        for k in kwargs.keys():
	                setattr(uvspec, k, kwargs[k])
	        uvspec.device="/png"
	        U = uvspec.snarf()

		# 2. Get and rename the pngs:
		pngs = []

		shrun("rm "+tempdir+"*png*")
		for i in range(0,len(U[1])):
			p = U[1][i].replace("PGPLOT /png: writing new file as ","")
			pngs.append(U[1][i].replace("PGPLOT /png: writing new file as ",""))
			shrun("mv "+p+" "+tempdir+"/pgplot"+str(i+2)+".png")
		shrun("mv pgplot.png "+tempdir+ "/pgplot1.png")
		
		videcon(tempdir+"/uvspec.m4v", tempdir=tempdir, r=r)
		shrun("rm "+tempdir+"*png*")	
		#3: Plot the data
		video = io.open(tempdir+"uvspec.m4v", "rb").read()
		video_encoded = b64encode(video)
		video_tag = '<video controls alt="test" src="data:video/x-m4v;base64,{0}">'.format(video_encoded)
		return HTML(data=video_tag)
	else:
		print "Error: vis argument has to be explicitly specified"

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
	if vis!=None:
		# NOTE: Use GPPLT to make the plots
	        gpplt = mirexecb.TaskGPPlot ()
	        gpplt.vis = vis
	        for k in kwargs.keys():
	                setattr(gpplt, k, kwargs[k])
	        gpplt.device="/png"
	        U = gpplt.snarf()
		HTML = vidshow(U=U, tempdir=tempdir, vidname="gpplt.m4v", r=r)
		
		return HTML
	else:
		print "Error: vis argument has to be explicitly specified"

def imview(im=None, r=2, tempdir = "/home/frank/", typ='pixel', slev = "p,1", levs="2e-3", 
		rang="0,2e-3,lin", nxy="1,1", labtyp = "hms,dms", options="wedge,3pixel", **kwargs):
	'''
	IPython Video Embedder for GPPLT. 
	vis = Full path of vis to be plotted
	r = plots per second [2]
	    Please specify vis and any of the following:
	'''
	if im!=None:
		# NOTE: Use CGDISP to make the plots
		cgdisp = mirexecb.TaskCgDisp ()
		cgdisp.in_ = im
		cgdisp.type = typ
		cgdisp.slev = slev
		cgdisp.levs = levs
		cgdisp.range = rang 
		cgdisp.nxy = nxy
		cgdisp.labtyp = labtyp
		cgdisp.options = options

	        for k in kwargs.keys():
	                setattr(cgdisp, k, kwargs[k])
	        cgdisp.device="/png"
	        
		U = cgdisp.snarf()

		# NOTE: Get the output from vidshow!
		HTML = vidshow(U=U, tempdir=tempdir, vidname="imview.m4v", r=r)

		# NOTE: Return the HTML object to IPython Notebook for Embedding!
		return HTML
	else:
		print "Error: vis argument has to be explicitly specified"


