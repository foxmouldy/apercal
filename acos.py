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

def rm(tag=None):
	'''
	Cleans up using a wildcard.
	'''
	os.system('rm -r '+tag)

class status:
	def __init__(self, name=None, i=1, selfcal_options=None):
		fname = name+'.txt';
		try:
			with open(fname):
			 	F = open(fname);
				Fr = F.readlines();
				FA = {};
				for i in range(len(Fr)):
					f = Fr[i].replace('\n','').replace(' ','').split('=');
					FA[f[0]] = f[1];
				# Object Handling
				self.name = FA['name'];
				self.i = int(FA['i']);
				self.vis = FA['vis']
				self.mask = FA['mask'];
				self.model = FA['model'];
				self.map = FA['map'];
				self.beam = FA['beam'];
				self.image = FA['image'];
				self.model4selfcal = FA['model4selfcal']
				self.imsize = int(FA['imsize']);
				self.cell = int(FA['cell']);
				self.cutoff = float(FA['cutoff']);
				self.niters = float(FA['niters']);
				self.gt = float(FA['gt']);
				self.invert_options = FA['invert_options'];
				self.selfcal_options = FA['selfcal_options']
				F.close();
		except IOError:
			# Object Handling
			self.name = name;
			self.i = i;
			self.vis = name;
			self.mask = name+'.mask'+str(i);
			self.model = name+'.model'+str(i);
			self.map = name+'.map'+str(i);
			self.beam = name+'.beam'+str(i);
			self.image = name+'.image'+str(i);
			self.model4selfcal = name+'.model4selfcal'+str(i);
			self.imsize = 2000;
			self.cell = 2; 
			self.cutoff = 0.02; # Just a random default.
			self.niters = 10000; 
			self.gt = 0.01;
			self.invert_options = 'mfs,double'
			self.selfcal_options = 'mfs,amplitude'
	
	def update(self):
		self.i +=1; 
		self.mask = self.name+'.mask'+str(self.i);
		self.model = self.name+'.model'+str(self.i);
		self.map = self.name+'.map'+str(self.i);
		self.beam = self.name+'.beam'+str(self.i);
		self.image = self.name+'.image'+str(self.i);
		self.model4selfcal = self.name+'.model4selfcal'+str(self.i);
		self.cutoff = self.cutoff/3.;
		self.gt = self.gt/3.
		self.selfcal_options = self.selfcal_options;

	def save(self):
		fname = self.name+'.txt';
		F = open(fname, 'w');
		# Object Handling
		F.write('name='+self.name+'\n');
		F.write('i='+str(self.i)+'\n');
		F.write('vis='+self.name+'\n');
		F.write('mask='+self.mask+'\n');
		F.write('model='+self.model+'\n');
		F.write('map='+self.map+'\n');
		F.write('beam='+self.beam+'\n');
		F.write('image='+self.image+'\n');
		F.write('model4selfcal='+self.model4selfcal+'\n')
		F.write('imsize='+str(self.imsize)+'\n');
		F.write('cell='+str(self.cell)+'\n')
		F.write('cutoff='+str(self.cutoff)+'\n')
		F.write('niters='+str(self.niters)+'\n')
		F.write('gt='+str(self.gt)+'\n')
		F.write('invert_options='+self.invert_options+'\n')
		F.write('selfcal_options='+self.selfcal_options+'\n')
		F.close();
