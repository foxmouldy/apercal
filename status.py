import re
import aplpy
#import mirexec
import imp
try:
	imp.find_module('mirexec');
	found = True;
except ImportError:
	found = False;
if found:
	from mirexec import *
	import mirexec

import sys 
import pylab as pl
import os 

class status:
	def __init__(self, name, i):
		self.name = name;
		self.i = i;

	def iter(self):
		self.i +=1; 
