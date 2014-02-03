import sys
import miriad
#import mirtask
import mirexec
import aplpy
import pylab as pl
import numpy
from apercal import calib
from apercal import acim
from apercal import acos
import os
from optparse import OptionParser 

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--mode", '-m', type='string', dest = 'mode', default="",
	help = 'Mode: Either mkpeel or mkfield. mkpeel uses uvmodel to subtract \
	the field fmod from the original uv-data-set, resulting in p.uv. \
	mkfield copies over the gain correction from p.uv to the uv-data-set, \
	and then undoes the correction. \n The underlying methodology is a-b=c.')

parser.add_option("-a", type='string', dest='a', default=None,
	help = 'uv file a: This is the parent uv-data-set from which we will subtract\
	the model using uvmodel');

parser.add_option("-b", type='string', dest='b', default=None,
	help = 'model b: This is the model which will be subtracted from uv-data-set a.');

parser.add_option('-c', type='string', dest='c', default=None, 
	help = 'uv file c: This is the output uv-data-set which we by using uvmodel to \
	subtract model b from uv-data-set c.');

parser.add_option('-g', type='string', dest='g', default=None, 
	help = 'for mkfield, this is the uv-data-set which contains the gains which \
	need to copied, applied, re-copied and then undone. ');


(options, args) = parser.parse_args();

if len(sys.argv)==1:
	print "peel.py - This helps peel off a set of sources from a region in the sky."
	parser.print_help();
	dummy = sys.exit(0);

p2w = os.getcwd();

def mkpeel(a,b,c):
	'''
	Here I use uvmodel to subtract the model b from the uv-data-set a. 
	'''
	print "UVMODEL: "+a+" - "+"uv("+b+") = "+c;
	# Step 1: First we use uvcat to apply the calibration, just to make sure. 
	uvcat = mirexec.TaskUVCat();
	uvcat.vis = a; 
	uvcat.out = 'temp.uv';
	tout = uvcat.snarf();
	acos.taskout(uvcat, tout, 'peel.txt');

	# Step 2: We use the temp.uv file to subtract the model. 
	uvmodel = mirexec.TaskUVModel();
	uvmodel.vis = 'temp.uv'; 
	uvmodel.model = b; 
	uvmodel.out = c; 
	uvmodel.options = 'subtract,mfs';
	tout = uvmodel.snarf();
	acos.taskout(uvmodel, tout, 'peel.txt');
	
	# Step 3: Finally, I'm going to make a settings file just for the peel.uv:
	S = acos.settings(name=c);
	S.save();
	
	# Step 4: Now to clean up the temp.uv files.
	os.system("rm -r temp*.uv");

def mkfield(a, b, c, g):
	'''
	Here I use uvmodel to subtract the model b from the uv-data-set a. 
	This also copies the gain over, subtracts the source and then undoes the gain. 
	'''
	# Step 0: We need to ensure that any previous selfcal calibration gets applied
	# to the uv-data-set a. 
	uvcat = mirexec.TaskUVCat();
	uvcat.vis = a; 
	uvcat.out = 'temp2.uv';
	tout = uvcat.snarf();
	acos.taskout(uvcat, tout, 'peel.txt');

	# Step 1: First we copy the calibration from g to the uv-data-set a:
	
	gpcopy = mirexec.TaskGPCopy();
	gpcopy.vis = g; 
	gpcopy.out = 'temp2.uv';
	tout = gpcopy.snarf();
	acos.taskout(gpcopy, tout, 'peel.txt');
	
	# Step 2: Use uvcat to apply the gains, creating a temporary uv-file. 
	uvcat = mirexec.TaskUVCat();
	uvcat.vis = 'temp2.uv';
	uvcat.out = 'temp3.uv';
	tout = uvcat.snarf();
	acos.taskout(uvcat, tout, 'peel.txt');

	# Step 3: Subtract the model pmod from the temporary uv-file. 
	uvmodel = mirexec.TaskUVModel();
	uvmodel.vis = 'temp3.uv';
	uvmodel.out = 'temp4.uv';
	uvmodel.model = b;
	uvmodel.options = 'subtract,mfs';
	tout = uvmodel.snarf();
	acos.taskout(uvmodel, tout, 'peel.txt');
	
 	# Step 4: This is a hack: We use atnf-gpedit (agpedit) to copy and invert the gains from g. 
	gpcopy.vis = g;
	gpcopy.out = 'temp4.uv';
	tout = gpcopy.snarf();
	acos.taskout(gpcopy, tout, 'peel.txt');

	cmd = './agpedit vis=temp4.uv options=invert';
	os.system(cmd);

	# Step 5: We use uvcat to make the desired uv-data-set. 
	uvcat.vis = 'temp4.uv';
	uvcat.out = c;
	tout = uvcat.snarf();
	acos.taskout(uvcat, tout, 'peel.txt');
	
	# Step 6: Finally, I make a settings file for c:
	S = acos.settings(name=c);
	S.save();
	print "DONE"

	# Step 7: Cleanup temp.uv and temp3.uv temp4.uv
	os.system("rm -r temp*.uv");

if options.mode!=None:
	print options.mode;
	if options.mode=='':
		print "Please specify mode=mkpeel/mkfield";
	if options.mode=='mkpeel':
		mkpeel(options.a, options.b, options.c);
	if options.mode=='mkfield':
		mkfield(options.a, options.b, options.c, options.g);


