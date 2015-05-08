import mirexecb 
import acos
import acim
import plot
import mirplot
import crosscal2
from ConfigParser import SafeConfigParser
import subprocess
import mynormalize

#import mselfcal

def shrun(cmd):
	'''
	shrun: shell run - helper function to run commands on the shell.
	'''
	#print cmd
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        	stderr = subprocess.PIPE, shell=True)
	out, err = proc.communicate()
	# NOTE: Returns the STD output.
	return out, err

def get_source_names(vis=None):
	if vis!=None:
		uvindex = mirexecb.TaskUVIndex ()
		uvindex.vis = vis
		u = uvindex.snarf ()
		i = [i for i in range(0,len(u[0])) if "pointing" in u[0][i]]
		N = len(u[0])
		s_raw = u[0][int(i[0]+2):N-2]
		sources = []
		for s in s_raw:
			sources.append(s.replace('  ', ' ').split(' ')[0])
		return sources
	else:
		print "get_source_names needs a vis!"

class Bunch: 
	def __init__(self, **kwds): 
		self.__dict__.update(kwds)
	def __getitem__(self, key):
		return getattr(self, key)

	
class settings:
	def __init__(self, filename):
		self.filename = filename
		self.parser = SafeConfigParser ()
		self.parser.read(self.filename)
	def set(self, section, **kwds):
		'''
		settings.set(settings=None, keyword1=value1, keyword2=value2)
		Change settings using this method. 
		'''
		parser = self.parser
		for k in kwds:
			parser.set(section, k, kwds[k])
		self.inp(section=section)
	def inp(self, section=None):
		'''
		settings.inp(section=None)
		Output the settings, by section if necessary.
		'''
		parser = self.parser
		if section!=None:
			print "[", section , "]"
			for p in parser.items(section):
				print p[0], " : ", p[1]
			print "\n"
			print "### Don't forget to save\n"
		else:
			for s in parser.sections ():
				print "[", s, "]"
				for p in parser.items(s):
					print p[0], " : ", p[1]
				print "\n"	
			print "### Don't forget to save\n"
	def get(self, section, keyword):
		parser = self.parser
		if len(parser.get(section, keyword).split(','))>1:
			return parser.get(section, keyword).split(',')
		else:
			return parser.get(section, keyword)

	def save(self):
		'''
		settings.save()
		Saves the new settings.
		'''
		parser = self.parser
		parser.write(open(self.filename, 'w'))

def get_params(config_parser, section):
	params = Bunch()
	for p in config_parser.items(section):
		setattr(params, p[0], p[1])
	return params
