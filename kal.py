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

parser.add_option("--calls", '-c', type='string', dest = 'calls', default=None,
	help = 'Custom pipeline (input each block in sequence)')
parser.add_option("--settings", '-s', type='string', dest='settings',
	default='mircal', help='Settings file [mircal.txt]')
parser.add_option("--args", '-a', type='string', dest='args',
	default='', help='Extra arguments for sub-calls ['']')

(options, args) = parser.parse_args();

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);



#p2w = '/home/frank/ngc3998/02-May-11/working/'
p2w = os.getcwd();

def cleanup():
	'''
	
	'''
	os.system('rm -r '+S.name+'/gains');
	os.system('rm -r '+S.name+'.model*')
	os.system('rm -r '+S.name+'.image*')
	os.system('rm -r '+S.name+'.res*')
	os.system('rm -r '+S.name+'.map*')
	os.system('rm -r '+S.name+'.beam*')
	os.system('rm -r '+S.name+'.mask*')
	os.system('rm -r '+S.name+'.m4s*')
	

def clean():
	#S.niters=10000;
	calib.invert(S, 'invert.txt');
	calib.clean(S, 'clean.txt');
	calib.restorim(S, 'restor.txt');
	calib.restores(S, 'restor.txt');

def rimres():
	calib.restorim(S, 'restor.txt');
	calib.restores(S, 'restor.txt');

def clean_deeper():
	ni = S.niters;
	S.niters=1000000;
	if os.path.exists(S.mask)!=True:
		calib.maths(S, 'maths.txt');
	calib.clean_deeper(S, 'clean.txt')#, df=2.);
	S.image = S.image.replace('image','image4s')
	S.res = S.res.replace('res','res4s')
	S.niters=ni;
	rimres();

def sc():
	#if S.N/(S.i+1)==2:
	#	S.selfcal_options='mfs'
	calib.selfcal(S, 'selfcal.txt');
	update();

global S; 

def makesettings():
	global S;
	S = acos.settings(name=options.settings)
	S.save();

def gets():
	global S;
	S = acos.settings(name=options.settings);
	S.save();

def iof():
	'''
	Reads in the comma-separated list of uvfiles. 
	wsrtfits -> attsys -> uvflag
	'''
	
	uvfiles = S.uvfiles;
	for u in uvfiles.split(','):
		calib.iofits(u, u.replace(S.tag, S.retag));

def ionly():
	uvfiles = S.uvfiles;
	fits = mirexec.TaskFits();
	for u in uvfiles.split(','):
		infile = u;
		fits.in_ = infile;
		outfile = u.replace(S.tag, S.retag);
		fits.out = outfile; 
		fits.op = 'uvin'; 
		tout = fits.snarf();
		acos.taskout(fits, tout, 'fits.txt');

def exf():
	fits = mirexec.TaskFits();
	uvfiles = S.uvfiles;
	for u in uvfiles.split(','):
		infile = u.replace(S.tag, S.retag);
		outfile = u.replace(S.tag, 'muvfits');
		calib.exfits(infile, outfile);	


def calcals():
	'''
	Performs mfcal on two calibrators.
	'''
	print '-> CALCALS'
	calib.calcals([S.cal1,S.cal2]);

def cal2srcs():
	'''
	Applies the calibration to the source files. 
	'''
	calib.cal2srcs(cals=[S.cal1,S.cal2], srcs=[S.src1,S.src2, S.name]);

def specr(u):
	'''
	Pulls a spectral-range from the file u.
	'''
	calib.specr(u, S)

def inical():
	print "-> INICAL"	
	#uvfiles = 'c1.UVF,c2.UVF,t1.UVF,t2.UVF'
	uvfiles = S.uvfiles;
	#1 Read in the files and do an initial calibration with calib.infits
	if S.i==0:
		if S.line.upper()!='NONE': 
			for u in uvfiles.split(','):
				print "SPECR"
				calib.specr(u.replace(S.tag,S.retag), S)
	
	#2 Run calib.calcals on the calibrator files. 
		print "CALCALS"
		calib.calcals([S.cal1,S.cal2]);
	
	#3 Run cal.cal2srcs to copy solutions over to the solutions to the files.
	print "CAL2SRCS"
	calib.cal2srcs(cals=[S.cal1,S.cal2], srcs=[S.src1,S.src2, S.name]);
	
	#4 selfcal
	
	# Initialize stuff
	
	# First Dirty Map
	print "0th Loop.\n"
	clean(S)
	S.m4s = S.model;
	sc(S);
	S.update(selfcal_options='mfs,amplitude')
	S.save();

def scloop():
	#for i in range(S.i,S.N+1):
	#print "Selfcal Loop "+str(i);
	#S.update(selfcal_options='mfs,amplitude');
	#S.save();
	clean(S);
	clean_deeper(S);
	sc(S);
		
	S.model = S.m4s;
	S.image = S.m4s.replace('.m4s', '.image4s');
	S.res = S.m4s.replace('.m4s', '.res4s');
	calib.restorim(S, 'restor.txt');
	calib.restores(S, 'restor.txt');
	#cmd = "grep Ratio selfcal.txt > sc_summary.txt";
	#os.system(cmd);
	#X = pl.recfromtxt('sc_summary.txt', delimiter=':');
	#pl.figure(figsize=(5,5));
	#pl.plot(pl.log10(X['f1']))
	#pl.savefig('sc_summary.png', dpi=300)
	#pl.close();

def specr():
	'''
	Removes the specified spectral window from the uv file. 
	'''

def fp_models(ppoly,fpoly,model):
	'''
	Uses the vertices defined in pgon to  
	'''
	maths = mirexec.TaskMaths();
	maths.exp = model;
	maths.mask = model;
	maths.region=ppoly;
	maths.out=model.replace("src","src_p");
	tout = restor.snarf();
	acos.taskout(maths,tout,'maths.txt');
	
	maths = mirexec.TaskMaths();
	maths.exp = model;
	maths.mask = model;
	maths.region=fpoly;
	maths.out=model.replace("src","src_f");
	tout = restor.snarf();
	acos.taskout(maths,tout,'maths.txt');

def mkfmod():
	'''
	Uses image properties to cutout a single rectangular 
	region from a mask. 
	S.fipe = X,Y,xp,yp,l
	X,Y: Size of the model image (pixels)
	xp,yp: Pixel coords of the source to be peeled
	l: Pixel length of displacement from source
	'''
	# First, the size of the image
	S.fipe=S.fipe.split(',');
	X = int(S.fipe[0]);
	Y = int(S.fipe[1]);
	xp = int(S.fipe[2]);
	yp = int(S.fipe[3]);
	l = int(S.fipe[4]);
	model = S.fipe[5];
	polygon = 'polygon(1,1,'+str(xp-l)+',1,'+str(xp-l)+','+str(yp+l);
	polygon = polygon+','+str(xp+l)+','+str(yp+l)+','+str(xp+l)+',1,';
	polygon = polygon+str(X)+',1,'+str(X)+','+str(Y)+',1,'+str(Y)+')';
	maths = mirexec.TaskMaths();
	maths.exp = model;
	maths.region = polygon;
	maths.out = 'fmod';
	tout = maths.snarf();
	acos.taskout(maths,tout,'maths.txt');

def mkpuv():
	'''
	For a chan0, applies the gains and then subtracts all the sources
	to provide a uv file with the source to be peeled. 	
	'''
	# First, apply the current gains. 
	uvcat = mirexec.TaskUVCat();
	uvcat.vis=S.vis;
	uvcat.out = S.vis+'_sc';
	tout = uvcat.snarf();
	acos.taskout(uvcat, tout, 'uvcat.txt');
	
	# Second, subtract the model from the new uv-file
	uvmodel = mirexec.TaskUVModel();
	uvmodel.vis = S.vis+'_sc';
	#TODO: Need to include pmod in the settings file. 
	uvmodel.model = 'fmod'; 
	uvmodel.options='subtract';
	uvmodel.out = 'puv';
	tout = uvmodel.snarf();
	acos.taskout(uvmodel, tout, 'uvmodel.txt');

def flag():
	uvflag = mirexec.TaskUVFlag();
	uvflag.vis = S.vis;
	uvflag.flagval = 'flag';
	for f in S.flags.split(','):
		uvflag.select = f;
		tout = uvflag.snarf();
		acos.taskout(uvflag, tout, 'uvflag.txt');

def update():
	S.update();
	S.save();
	#print "Updated!"

def uvlin():
	cmd = 'uvlin vis='+S.vis+' chans='+chans0+' out='+S.chan0+' order=2 mode='+S.mode;
	os.system(cmd);
	gets(S.chan0)

def selfcalcopy():
	gpcopy = mirexec.TaskGPCopy();
	gpcopy.vis = S.chan0;
	gpcopy.out = S.vis;
	tout = gpcopy.snarf();
	acos.taskout(gpcopy, tout, 'gpcopy');

def getuvspw():
	uvaver = mirexec.TaskUVAver();
	for f in S.uvfiles.split(','):
		print "Extracting "+str(S.line)+" from "+f;
		# Now to extract the spectral range using uvaver
		uvaver.vis = f;
		uvaver.line = S.line;
		uvaver.out = f.replace(S.tag,S.retag);
		tout = uvaver.snarf();
		acos.taskout(uvaver, tout, 'uvaver');
		# Delete the old file
		cmd = 'rm -r '+f;
		os.system(cmd);
			
def bsc():
	# This is the batch selfcal. It will loop over each vis. 
	vises = S.vis;
	for v in vises.split(','):
		S.vis=v;
		calib.selfcal(S, 'selfcal.txt');
	S.vis = vises


if options.calls!=None:
	gets();
	print S.name
	for c in options.calls.split(','):
		#print c+'\n';
		cmd = c+'('+str(options.args)+')';
		print cmd;
		exec(cmd);
