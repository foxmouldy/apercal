import re
import aplpy
import sys 
import pylab as pl
import os 
import imp
try:
	imp.find_module('mirexec');
	found = True;
except ImportError:
	found = False;
if found:
	from mirexec import *
	import mirexec

def pout(task=None, tout=None):
	'''
	Inserts the output tout into the tasks's record file. 
	'''
	f = open(task+'.txt', 'a');
	for t in tout[0]:
		f.writelines(t+'\n');
	f.writelines('\n');
	f.close();

def taskout(task, tout, tfilename):
	f = open(tfilename, 'a');
	D = task.__dict__;
	for d in D:
		if D[str(d)]!=False:
			outstring = str(d)+'='+str(D[str(d)])+'\n';
			f.writelines(outstring);
	f.writelines('\n')
	for t in tout[0]:
            f.writelines(t+'\n');
	f.writelines('\n---- \n')
	f.close();

def rm(tag=None):
	'''
	Cleans up using a wildcard.
	'''
	os.system('rm -r '+tag)

class settings:
	def __init__(self, uvfiles='c1,c2,t1,t2', name=None, tag='.UVF', retag='uv', cal1='cal1', cal2='cal2',
	src1='src1', line='channel,1000,1,1,1', src2='src2', i=1, N=0, selfcal_options='mfs,phase', 
	selfcal_select='uvrange(0.5,10000)', gt=0.001, cutoff=None,
	overwrite=False):

		fname = name+'.dat';
		if overwrite==True:
			os.system('rm '+fname)

		try:
			with open(fname):
			 	F = open(fname);
				Fr = F.readlines();
				FA = {};
				for i in range(len(Fr)):
					f = Fr[i].replace('\n','').replace(' ','').split('=');
					FA[f[0]] = f[1];
				# Object Handling
				self.uvfiles = FA['uvfiles'];
				self.tag = FA['tag'];
				self.retag = FA['retag'];
				self.name = FA['name'];
				self.cal1 = FA['cal1'];
				self.cal2 = FA['cal2'];
				self.src1 = FA['src1'];
				self.src2 = FA['src2'];
				self.line = FA['line'];
				self.i = int(FA['i']);
				self.N = int(FA['N']);
				self.vis = FA['vis']
				self.mask = FA['mask'];
				self.model = FA['model'];
				self.map = FA['map'];
				self.beam = FA['beam'];
				self.image = FA['image'];
				self.res = FA['res']
				self.m4s = FA['m4s']
				self.imsize = int(FA['imsize']);
				self.cell = int(FA['cell']);
				self.selfcal_select = FA['selfcal_select'];
				self.cutoff = round(float(FA['cutoff']), 10);
				self.niters = float(FA['niters']);
				self.gt = round(float(FA['gt']),10);
				self.invert_options = FA['invert_options'];
				self.selfcal_options = FA['selfcal_options']
				F.close();
		except IOError:
			# Object Handling
			self.uvfiles = uvfiles;
			self.tag = tag;
			self.retag = retag;
			self.name = name;
			self.cal1 = cal1;
			self.cal2 = cal2;
			self.src1 = src1;
			self.src2 = src2;
			self.line = line;
			self.i = i;
			self.N = N;
			self.vis = name;
			self.mask = name+'.mask'+str(i);
			self.model = name+'.model'+str(i);
			self.map = name+'.map'+str(i);
			self.beam = name+'.beam'+str(i);
			self.image = name+'.image'+str(i);
			self.res = name+'.res'+str(i);
			self.m4s = name+'.m4s'+str(i);
			self.imsize = 2000;
			self.cell = 2; 
			self.cutoff = 0.02; # Just a random default.
			self.niters = 10000; 
			self.gt = round(gt,10);
			self.invert_options = 'mfs,double'
			self.selfcal_options = selfcal_options;
			self.selfcal_select = selfcal_select;

	def update(self, selfcal_options=None):
		self.i +=1;
		if self.N>0:
			self.N -=1;
		df = 2.+1./(self.i+1);
		self.mask = self.name+'.mask'+str(self.i);
		self.model = self.name+'.model'+str(self.i);
		self.map = self.name+'.map'+str(self.i);
		self.beam = self.name+'.beam'+str(self.i);
		self.image = self.name+'.image'+str(self.i);
		self.res = self.name+'.res'+str(self.i);
		self.m4s = self.name+'.m4s'+str(self.i);
		self.cutoff = round(self.cutoff/df, 10);
		self.gt = round(self.gt/df, 10)
		if selfcal_options!=None:
			self.selfcal_options = selfcal_options;

	def save(self):
		fname = self.name+'.dat';
		F = open(fname, 'w');
		# Object Handling
		F.write('uvfiles='+self.uvfiles+'\n');
		F.write('tag='+self.tag+'\n')
		F.write('retag='+self.retag+'\n');
		F.write('name='+self.name+'\n');
		F.write('cal1='+self.cal1+'\n')
		F.write('cal2='+self.cal2+'\n')
		F.write('src1='+self.src1+'\n')
		F.write('src2='+self.src2+'\n')
		F.write('line='+self.line+'\n')
		F.write('i='+str(self.i)+'\n');
		F.write('N='+str(self.N)+'\n');
		F.write('vis='+self.name+'\n');
		F.write('mask='+self.mask+'\n');
		F.write('model='+self.model+'\n');
		F.write('map='+self.map+'\n');
		F.write('beam='+self.beam+'\n');
		F.write('image='+self.image+'\n');
		F.write('res='+self.res+'\n');
		F.write('m4s='+self.m4s+'\n')
		F.write('imsize='+str(self.imsize)+'\n');
		F.write('cell='+str(self.cell)+'\n')
		F.write('cutoff='+str(round(self.cutoff,10))+'\n')
		F.write('niters='+str(self.niters)+'\n')
		F.write('gt='+str(round(self.gt,10))+'\n')
		F.write('invert_options='+self.invert_options+'\n')
		F.write('selfcal_options='+self.selfcal_options+'\n')
		F.write('selfcal_select='+self.selfcal_select+'\n')
		F.close();
		
