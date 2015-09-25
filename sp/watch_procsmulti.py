# Bradley Frank, ASTRON, 2014
# This script uses psutil to watch and profile the vital statistics of a
# program or a process. This also plots the output %CPU, %MEM and some io
# statistics to a png file. This will also write an output file which
# contains the aforementioned statistics. 
# TODO: Use hdf5 functionality to store the output. 
# TODO: Fix bug which causes only the last process to be plotted and saved. 
import pylab as pl
import time
import psutil
import os
from optparse import OptionParser 
import sys
from textwrap import wrap
import threading

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

# The text file which keeps the program calls to watch for
parser.add_option('--name', '-n', type='string', dest='name', default=None,
	help = 'Name of text file which contains the commands to be watched [None]')
# How long to keep watching? Default = 10mins
parser.add_option('--total', '-t', type='float', dest='total', default=600.00, 
	help = 'Total time to watch the program/process in seconds. [600]')
# Time increment to watch over
parser.add_option('--dt', type='float', dest='dt', default=0.01, 
	help = 'Time step to watch the program/process in seconds. [0.01]');
# Output text handle
parser.add_option('--outtag', '-o', type='string', dest='outtag', default=None, 
	help = 'Tag handle for the text and plot files. .txt and .png will be appended to this. [None]')

(options, args) = parser.parse_args();


if len(sys.argv)==1:
	# Run or Import
	if __name__=="__main__":
		print "watch_process.py: script to monitor, save and plot the vital-statistics of a program/process."
		parser.print_help();
		dummy = sys.exit(0);

def on_terminate(proc):
	print("process {} terminated".format(proc));

class watch_multiproc(threading.Thread):
	def __init__(self, params):
		threading.Thread.__init__(self);
		self.params = params;

	def run(self):
		'''
		watch_process(params): module based on psutil to watch a specific
		program/process. 
		Parameters required are:
		params.cmd = command in a Popen supported list, i.e. no spaces,
			each argument in its own cell.  
		params.outtag = tag handle for the text file and the plot file.
			.txt and .png will be appended to this. 
		params.dt = incremental time-step to watch the process. Default is
			10 milliseconds. 
		params.total = total time to watch the process. Default is 5
			minutes. 
		'''
		fout = open(params.outtag+'.txt', 'w');
		d0 = psutil.disk_usage('/');
		running=True;
		cpu_usage = [];
		mem_usage = [];
		duration = [];
		d = 0.0;
		p = psutil.Popen(params.cmd, stdout=fout);
		
		try:
			while d<params.total:
				d = d+params.dt;
				if p.status=='running':
					# If the program is running, this captures
					# the vital-statistics.
					cpu_usage.append(p.get_cpu_percent());
					mem_usage.append(p.get_memory_percent());
					#duration.append(d);
					duration.append(p.get_cpu_times().user)
				else:
					# This watches and ensures that the
					# process is indeed dead. This is the first
					# level of exception handling and
					# loop-breakage. 
					procs = psutil.get_process_list();
					gone, alive = psutil.wait_procs(procs, 3, callback=on_terminate)
					break
				time.sleep(params.dt)
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
			# This exception allows the user to Ctrl-C if you thing
			# that the program is hanging.
			p.kill()
			print "I have killed it, and it has become a..."+p.status
			procs = psutil.get_process_list();
			gone, alive = psutil.wait_procs(procs, 3, callback=on_terminate)
		cpu_usage = pl.array(cpu_usage);
		duration = pl.array(duration);
		mem_usage = pl.array(mem_usage);
		pl.step(duration, cpu_usage, label='%CPU');
		pl.step(duration, mem_usage, label='%MEM');
		pl.xlabel('User Time (seconds)');
		pl.ylabel('%');
		d1 = psutil.disk_usage('/')
		D = d1.used-d0.used; 
		MB = 1024.*1024. # 1MB in Bytes
		data_written = D/MB; 
		total_time = pl.amax(duration)-pl.amin(duration);
		dw = str(round(data_written, 2))+"MB"
		tt = str(round(total_time, 5))+"s";
		string_ann = "Writes: "+dw+' in '+tt;
		title='Process: '+str(params.cmd)+'\n / '+string_ann;
		pl.title('\n'.join(wrap(title,50)));
		pl.legend();
		pl.tight_layout();
		pl.savefig(params.outtag+'.png', dpi=300);
		pl.close();
		fout.write(string_ann+'\n')
		fout.close()
		print "Completed."

if __name__ == "__main__":
		print "\nwatch_process.py - Try not to do any other writes on this disk."
		options.cmds = open(options.name, 'r');
		i = 0;
		for cmd in options.cmds:
			print "watching... "+cmd;
			c = cmd.replace('\n', '').split(' ');
			options.cmd = c;
			options.outtag = options.outtag+'_'+str(i)
			watch_process(options);
			i = i+1;
