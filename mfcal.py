import sys
import miriad
import mirtask
import mirexec
import aplpy
import pylab as pl
import numpy
from apercal import calib
from apercal import acim
from apercal import acos
import os
from optparse import OptionParser 
from threading import Thread

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

# O1 for Option 
parser.add_option("--channels", '-c', dest = 'channels',default='0,10', 
	help = 'Channel range for the operation.');

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);



def exchan(vis, ch):
	uvaver = mirexec.TaskUVAver();
	uvaver.vis = vis;
	uvaver.line = 'channel,1,'+str(ch)+',1,1';
	uvaver.out = vis.replace('.uv','_ch'+str(ch)+'.uv');
	tout = uvaver.snarf()
	acos.taskout(uvaver, tout, 'uvaver.txt');
	return uvaver.out;

def invert(vis, i):
	invert = mirexec.TaskInvert();
	invert.vis = vis;
	invert.map = vis.replace('.uv','.map'+str(i));
	invert.beam = vis.replace('.uv','.beam'+str(i));
	invert.imsize = 2048;
	invert.cell = 2;
	invert.options = 'double';
	tout = invert.snarf();
	acos.taskout(invert, tout, 'invert.txt');

def clean(vis, cutoff, i):
	# Remove the old model
	#cmd = 'rm -r '+vis.replace('.uv', '.model'+str(i))
	#os.system(cmd)
	clean = mirexec.TaskClean();
	clean.vis = vis;
	clean.beam = vis.replace('.uv','.beam'+str(i));
	clean.map = vis.replace('.uv','.map'+str(i));
	clean.out = vis.replace('.uv','.model'+str(i));
	clean.cutoff = cutoff;
	tout = clean.snarf();
	acos.taskout(clean, tout, 'clean.txt');

def restor(vis, i):
	restor = mirexec.TaskRestore();
	restor.model = vis.replace('.uv','.model'+str(i))
	restor.beam = vis.replace('.uv','.beam'+str(i))
	restor.map = vis.replace('.uv','.map'+str(i))
	restor.out = vis.replace('.uv', '.image'+str(i))
	tout = restor.snarf();
	acos.taskout(restor, tout, 'restor.txt');
	restor.mode = 'residual';
	restor.out = vis.replace('.uv','.res'+str(i));
	tout = restor.snarf();
	acos.taskout(restor, tout, 'restor.txt');

def selfcal(vis, model):
	selfcal = mirexec.TaskSelfCal();
	selfcal.vis = vis; 
	selfcal.model = model;
	selfcal.options='amplitude'
	tout = selfcal.snarf();
	acos.taskout(selfcal, tout, 'selfcal.txt');

def worker(vis, cutoff, i):
		#print "Channel "+str(i);
		visout = exchan(vis, i)
		for j in range(0,4):
			print "j = "+str(j);
			invert(visout, j);
			clean(visout, cutoff[j], j);
			restor(visout, j);
			selfcal(visout, visout.replace('.uv','.model'+str(j)));
		vises.append(visout);
		print "Channel "+str(i)+" DONE :)";

vis = 'src.uv';
cutoff = [0.004, 0.002, 0.001, 0.0008];
global vises
vises = [];

C = options.channels.split(',');

for i in range(int(C[0]),int(C[1])+1):
	t = Thread(target=worker, args=(vis,cutoff,i));
	t.start();

