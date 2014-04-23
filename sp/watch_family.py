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
	help = 'Process to be Monitored, pid or name [None]');
parser.add_option("--ptype", type='string', dest='ptype', default='name', 
	help = "How have you specified the process? [Name] or pid?")
parser.add_option("--saveas", type='string', dest='saveas', default='txt',
	help = "How should the report be saved? [txt] file or fig?");
parser.add_option("--totaltime", type=float, dest='totaltime', default=5.0, 
	help = "Total Time to Sample the Process [5.0]s");

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

class watch_procs(threading.Thread):
	def __init__(self, proc, totaltime=5.0):
		threading.Thread.__init__(self);
		self.totaltime = totaltime;
		self.proc = proc;
		self.cpu = [];
		self.ram = [];
		self.x = [];
		self.z = []

	def run(self):
		running=True;
		cpu = [];
		mem = [];
		x = [];
		z = []
		d = 0.0;
		p = self.proc;
		try:
			while d<self.totaltime:
				d += 1;
				if p.status=='running':
					# If the program is running, this captures
					# the vital-statistics.
					cpu.append(p.get_cpu_percent());
					mem.append(p.get_memory_percent());
					z.append(p.get_cpu_times().system)
					x.append(d)
				else:
					# This watches and ensures that the
					# process is indeed dead. This is the first
					# level of exception handling and
					# loop-breakage. 
					procs = psutil.get_process_list();
					gone, alive = psutil.wait_procs(procs, 3, callback=on_terminate)
					break
				time.sleep(1)
		except psutil._error.AccessDenied:
			# This exception watches for the natural death of the
			# process. This is the second level of redundancy handling
			# the death of the task, the first one is in the else
			# statement above. 
			p.kill()
			print "It has died and has become a... "+p.status;
			procs = psutil.get_process_list();
			gone, alive = psutil.wait_procs(procs, 3, callback=on_terminate)
		except KeyboardInterrupt:
			# This exception allows the user to exit the watch. You
			# have to terminate the process elsewhere. 
			print "Exiting..."+p.status
			procs = psutil.get_process_list();
			gone, alive = psutil.wait_procs(procs, 3, callback=on_terminate)
		self.cpu = pl.array(cpu);
		self.x = pl.array(x);
		self.ram = pl.array(mem);
		self.z = pl.array(z);

	def get_result(self):
		return self.x, self.cpu, self.ram, self.z

def on_terminate(proc):
	print("process {} terminated".format(proc));


def get_proc_by_pid(pid):
	procs = psutil.get_process_list()
	for p in procs:
		if pid == p.pid:
			proc = p;
	return proc


def get_proc_by_name(proc_name='firefox'):
	'''
	Returns the process object. 	
	'''
	proc = None;
	procs = psutil.get_process_list()
	for p in procs:
		if proc_name.upper() == p.name.upper():
			proc = p;
	return proc

def get_children(proc):
	p_c = proc.get_children()	
	return p_c;


if __name__=='__main__':
	
	if options.ptype.upper()=='PID':
		proc = get_proc_by_pid(int(options.proc));
	else:
		proc = get_proc_by_name(proc_name=options.proc);

	if proc==None:
		print "No process found."
		sys.exit(1)
	F = [];
	F.append(watch_procs(proc, totaltime=options.totaltime));
	
	for child in get_children(proc):
		F.append(watch_procs(child, totaltime=options.totaltime));
	
	for f in F:
		f.start()
	
	for f in F:
		f.join()
		time.sleep(1)
	
	if options.saveas.upper()=='TXT':
		header = "time cputimes cpu ram"
		print f.name
		for f in F:
			x, cpu, ram, z = f.get_result()
			pl.savetxt(proc.name+'.'+f.proc.name+'.'+str(f.proc.pid)+'.txt', zip(x, z, cpu, ram), header=header, fmt='%10.10f');
	else:
		for f in F:
			x, cpu, ram, z = f.get_result()
			pl.step(x-pl.amin(x), cpu, label=f.proc.name)
			pl.step(x-pl.amin(x), ram);
		
		pl.legend(loc=2)
		pl.xlabel('Wall Clock (s)');
		pl.ylabel('% Usage')
		pl.savefig(options.proc+'.eps');
