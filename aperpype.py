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

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--calls", '-c', type='string', dest = 'calls', default=None,
	help = 'Custom pipeline (input each block in sequence)')
parser.add_option("--settings", '-s', type='string', dest='settings',
	default='mircal', help='Settings file [mircal.txt]')

(options, args) = parser.parse_args();

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);



#p2w = '/home/frank/ngc3998/02-May-11/working/'
p2w = os.getcwd();

def cleanup():
	os.system('rm -r '+S.name+'/gains');
	os.system('rm -r '+S.name+'.model*')
	os.system('rm -r '+S.name+'.image*')
	os.system('rm -r '+S.name+'.res*')
	os.system('rm -r '+S.name+'.map*')
	os.system('rm -r '+S.name+'.beam*')
	os.system('rm -r '+S.name+'.mask*')
	os.system('rm -r '+S.name+'.m4s*')
	

def gocal(S):
	calib.invert(S, 'invert.txt');
	calib.clean(S, 'clean.txt');
	calib.restorim(S, 'restor.txt');
	calib.restores(S, 'restor.txt');

def decal(S):
	calib.maths(S, 'maths.txt');
	calib.clean_deeper(S, 'clean.txt')#, df=2.);

def sc(S):
	if S.N/S.i==2:
		S.selfcal_options='mfs'
	calib.selfcal(S, 'selfcal.txt');

global S; 

def mkset():
	global S;
	S = acos.settings(name=options.settings)
	S.save();

def gets():
	global S;
	#immax = 5.668E-02/3.;
	S = acos.settings(name=options.settings);
	S.save();

def iof():
	#if S.i==0:
	uvfiles = S.uvfiles;
	for u in uvfiles.split(','):
		calib.iofits2(u, u.replace('.UVfl', '.uv'));

def inical():
	
	#uvfiles = 'c1.UVF,c2.UVF,t1.UVF,t2.UVF'
	uvfiles = S.uvfiles;
	print uvfiles
	sys.exit(0);
	#1 Read in the files and do an initial calibration with calib.infits
	if S.i==0:
		for u in uvfiles.split(','):
			calib.specr(u.replace('.UVfl','.uv'), S)
	
	#2 Run calib.calcals on the calibrator files. 
		calib.calcals([S.cal1,S.cal2]);
	
	#3 Run cal.cal2srcs to copy solutions over to the solutions to the files.
	calib.cal2srcs(cals=[S.cal1,S.cal2], srcs=[S.src1,S.src2, S.name]);
	
	#4 selfcal
	
	# Initialize stuff
	
	# First Dirty Map
	print "0th Loop....... \n -------"
	gocal(S)
	S.m4s = S.model;
	sc(S);
	S.update(selfcal_options='mfs,amplitude')
	S.save();

def scloop():
	for i in range(S.i,S.i+S.N+1):
		print "Selfcal Loop "+str(i);
		S.update(selfcal_options='mfs,amplitude');
		S.save();
		gocal(S);
		decal(S);
		sc(S);
		
	S.model = S.m4s;
	S.image = S.m4s.replace('.m', '.image');
	S.res = S.m4s.replace('.m', '.res');
	calib.restorim(S, 'restor.txt');
	calib.restores(S, 'restor.txt');
	cmd = "grep Ratio selfcal.txt > sc_summary.txt";
	os.system(cmd);
	X = pl.recfromtxt('sc_summary.txt', delimiter=':');
	pl.figure(figsize=(5,5));
	pl.plot(pl.log10(X['f1']))
	pl.savefig('sc_summary.png', dpi=300)
	pl.close();

if options.calls!=None:
	for c in options.calls.split(','):
		gets();
		print c+'\n';
		exec(c+'()');