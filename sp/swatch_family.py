import threading
import pylab as pl
import psutil
import time
from textwrap import wrap
import sys
from optparse import OptionParser
import os 

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--proc", type = 'string', dest = 'proc', default=None, 
	help = 'Process to be Monitored, pid or name [None]');
parser.add_option("--ptype", type='string', dest='ptype', default='name', 
	help = "How have you specified the process? [Name] or pid or start?")
parser.add_option("--cfile", type='string', dest='cfile', default=None, 
	help = "File which contains the commands to be started. [None]")
parser.add_option("--saveas", type='string', dest='saveas', default='txt',
	help = "How should the report be saved? [txt] file or fig?");
parser.add_option("--totaltime", type=float, dest='totaltime', default=5.0, 
	help = "Total Time to Sample the Process [5.0]s");
parser.add_option("--tag", type='string', dest='tag', default=None, 
	help = "Output tag [None]");

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
		self.i0 = [];
		self.i1 = [];
		self.i2 = [];
		self.i3 = [];

	def run(self):
		running=True;
		cpu = [];
		mem = [];
		x = [];
		z = []
		d = 0.0;
		p = self.proc;
		i0 = []; 
		i1 = [];
		i2 = [];
		i3 = [];
		try:
			while d<self.totaltime:
				d += 1;
				if p.status!='zombie':
					# If the program is running, this captures
					# the vital-statistics.
					cpu.append(p.get_cpu_percent());
					mem.append(p.get_memory_percent());
					z.append(p.get_cpu_times().system)
					x.append(d)
					i0.append([p.get_io_counters()[0]])
					i1.append([p.get_io_counters()[1]])
					i2.append([p.get_io_counters()[2]])
					i3.append([p.get_io_counters()[3]])
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
		self.i0 = pl.array(i0);
		self.i1 = pl.array(i1);
		self.i2 = pl.array(i2);
		self.i3 = pl.array(i3);

	def get_result(self):
		return self.x, self.cpu, self.ram, self.z, self.i0, self.i1, self.i2, self.i3

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

def start_proc(cmd):
	'''
	Utility to start the process. Hopefully this happens instantaneously.
	'''
	fout = open('temp.txt', 'w');
	p = psutil.Popen(cmd, stdout = fout);
	return p, fout;

if __name__=='__main__':
	fout = None;	
	if options.ptype.upper()=='PID':
		proc = get_proc_by_pid(int(options.proc));
	elif options.ptype.upper()=='NAME':
		proc = get_proc_by_name(proc_name=options.proc);
	elif options.ptype.upper()=='START':
		if options.cfile!=None:
			cfile = open(options.cfile, 'r');
			cmd = cfile.read()
			cmd = cmd.replace('\n', '').split(' ');
			proc, fout = start_proc(cmd);
		else:
			print "Missing --cfile for command file."
			sys.exit(0);
	if proc==None:
		print "No process found."
		sys.exit(0)
	F = [];
	F.append(watch_procs(proc, totaltime=options.totaltime));
	if len(proc.get_children())!=None:
		for child in get_children(proc):
			F.append(watch_procs(child, totaltime=options.totaltime));
	
	for f in F:
		f.start()
	
	for f in F:
		f.join()
		time.sleep(1)
	N = 0;	
	if options.saveas.upper()=='TXT':
		header = "time cputimes cpu ram"
		for f in F:
			N += 1;
			if f.proc.is_running()==False:
				pname = str(proc.pid);
				fname = str(proc.pid);
				fid = proc.pid;
			else:
				pname = proc.name;
				fname = f.proc.name;
				fid = f.proc.pid;

			x, cpu, ram, z, i0, i1, i2, i3 = f.get_result()
			if options.tag!=None:
				outname = options.tag+'.'+pname+'.'+fname+'.'+str(fid)+str(N)+'.dat';
			else:
				outname = pname+'.'+fname+'.'+str(fid)+str(N)+'.dat';
			pl.savetxt(outname, zip(x, z, cpu, ram, i0, i1, i2, i3), fmt='%10.10f');
	else:
		for f in F:
			x, cpu, ram, z = f.get_result()
			pl.step(x-pl.amin(x), cpu, label=f.proc.name)
			pl.step(x-pl.amin(x), ram);
		
		pl.legend(loc=2)
		pl.xlabel('Wall Clock (s)');
		pl.ylabel('% Usage')
		pl.savefig(proc+'.eps');
		
	if fout!=None:
		fout.close()
		os.system('mv temp.txt '+pname+'.stdout.txt')
