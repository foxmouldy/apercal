import threading
import pylab as pl
import psutil
import time
from textwrap import wrap
import sys
from optparse import OptionParser

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--proc", type = 'string', dest = 'proc', default=None, 
	help = 'Process to be inspected, pid or name [None]');
parser.add_option("--ptype", type='string', dest='ptype', default='name', 
	help = "How have you specified the process? [Name] or pid?")

(options, args) = parser.parse_args();

def get_proc_by_pid(pid):
	proc = [];
	procs = psutil.get_process_list()
	for p in procs:
		if pid == p.pid:
			proc.append(p);
	return proc

def get_proc_by_name(proc_name='firefox'):
	'''
	Returns the process object. 	
	'''
	proc = [];
	procs = psutil.get_process_list()
	for p in procs:
		if proc_name.upper() == p.name.upper():
			proc.append(p);
	return proc

def get_children(proc):
	p_c = proc.get_children() 	
	return p_c;


if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

if __name__=="__main__":
	if options.ptype.upper()=='PID':
		procs = get_proc_by_pid(int(options.proc));
	else:
		procs = get_proc_by_name(proc_name=options.proc);
	if procs==[]:
		print "No process found."
		sys.exit(1)

	for p in procs:
		print "-----"
		print "Main Process: {}".format(p)
		print "#Threads = {}".format(p.get_num_threads())
		print '%CPU = {}'.format(p.get_cpu_percent())
		print "%MEM = {}".format(p.get_memory_percent())
		if len(get_children(p))>0:
			for child in get_children(p):
				print "\tChild of {}".format(p.name)
				print "\t"+str(child);
				print "\t#Threads = {}".format(child.get_num_threads())
				print '\t%CPU = {}'.format(child.get_cpu_percent())
				print "\t%MEM = {}".format(child.get_memory_percent())
				print "\t-"
	
	print "\n"
