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
	def __init__(self, name=None, cal1='cal1', cal2='cal2',
	src1='src1', spw='channel,1000,1,1,1', src2='src2', i=1, selfcal_options='mfs,phase', 
	selfcal_select='uvrange(0.5,10000)', gt=0.001, cutoff=None,
	overwrite=False):

		fname = name+'.txt';
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
				self.name = FA['name'];
				self.cal1 = FA['cal1'];
				self.cal2 = FA['cal2'];
				self.src1 = FA['src1'];
				self.src2 = FA['src2'];
				self.spw = FA['spw'];
				self.i = int(FA['i']);
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
				if cutoff!=None:
					self.cutoff = round(cutoff, 6);
				else:
					self.cutoff = round(float(FA['cutoff']), 6);
				self.niters = float(FA['niters']);
				if gt!=None:
					self.gt=gt;
				else:
					self.gt = round(float(FA['gt']),6);
				self.invert_options = FA['invert_options'];
				if selfcal_options!=None:
					self.selfcal_options=selfcal_options;
				else:
					self.selfcal_options = FA['selfcal_options']
				F.close();
		except IOError:
			# Object Handling
			self.name = name;
			self.cal1 = cal1;
			self.cal2 = cal2;
			self.src1 = src1;
			self.src2 = src2;
			self.spw = spw;
			self.i = i;
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
			self.gt = round(gt,6);
			self.invert_options = 'mfs,double'
			self.selfcal_options = selfcal_options;
			self.selfcal_select = selfcal_select;

	def update(self, selfcal_options=None):
		self.i +=1;
		df = 2.+1./(self.i+1);
		self.mask = self.name+'.mask'+str(self.i);
		self.model = self.name+'.model'+str(self.i);
		self.map = self.name+'.map'+str(self.i);
		self.beam = self.name+'.beam'+str(self.i);
		self.image = self.name+'.image'+str(self.i);
		self.res = self.name+'.res'+str(self.i);
		self.m4s = self.name+'.m4s'+str(self.i);
		self.cutoff = round(self.cutoff/df, 6);
		self.gt = round(self.gt/df, 6)
		if selfcal_options!=None:
			self.selfcal_options = selfcal_options;

	def save(self):
		fname = self.name+'.txt';
		F = open(fname, 'w');
		# Object Handling
		F.write('name='+self.name+'\n');
		F.write('cal1='+self.cal1+'\n')
		F.write('cal2='+self.cal2+'\n')
		F.write('src1='+self.src1+'\n')
		F.write('src2='+self.src2+'\n')
		F.write('spw='+self.spw+'\n')
		F.write('i='+str(self.i)+'\n');
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
		F.write('cutoff='+str(round(self.cutoff,6))+'\n')
		F.write('niters='+str(self.niters)+'\n')
		F.write('gt='+str(round(self.gt,6))+'\n')
		F.write('invert_options='+self.invert_options+'\n')
		F.write('selfcal_options='+self.selfcal_options+'\n')
		F.close();
