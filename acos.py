import re
import aplpy
import mirexec
from mirexec import *
import sys 
import pylab as pl
import os 

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
