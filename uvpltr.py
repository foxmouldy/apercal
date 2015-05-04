from apercal import mirexecb
import io
from IPython.display import HTML
from base64 import b64encode
import subprocess

#vis = 'acf2g4p1.1370'
#tempdir = "/home/frank/mirtemp/"
def videcon(outname):
	'''
	Uses avconv to make the video!
	'''
	shrun("avconv -r 2 -f image2 -i pgplot%d.png -vcodec libx264 "+outname)

def shrun(cmd):
	'''
	shrun: shell run - helper function to run commands on the shell.
	'''
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=True)
	out, err = proc.communicate()
	# NOTE: Returns the STD output.
	return out, err

def uvpltr(vis=None, tempdir = "/home/frank/", **kwargs):
	'''
	IPython Video Embedder for UVPLT. 
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
		for i in range(0,len(U[1])):
			p = U[1][i].replace("PGPLOT /png: writing new file as ","")
			pngs.append(U[1][i].replace("PGPLOT /png: writing new file as ",""))
			shrun("mv "+p+" "+tempdir+"/pgplot"+str(i+2)+".png")
		shrun("mv pgplot.png "+tempdir+ "/pgplot1.png")
		
		videcon(tempdir+"/uvplt.mp4")
		
	        return uvplt
		# 2: Rename them
	else:
		print "Error: vis argument has to be explicitly specified"

def vembed(video=None):
	if video!=None:
		video = io.open(video, "rb").read()
		video_encoded = b64encode(video)
		video_tag = '<video controls alt="test" src="data:video/x-mp4;base64,{0}">'.format(video_encoded)
		HTML(data=video_tag)
	else: 
		print "Please provide video to embed"
	
#uvpltr(vis='acf2g4p1.1370', tempdir = tempdir, nxy='2,2', stokes='xx,yy')
#vembed(video=tempdir+"/uvplt.mp4")
