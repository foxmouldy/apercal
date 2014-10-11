import pylab as pl
import time
import os
import threading
import sys
import mirexec
from apercal import mirexecb
from optparse import OptionParser
import acf_selfcal

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--vis", '-v', type = 'string', dest = 'vis', default=None, 
	help = 'vis to be split')

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

class Bunch:
	def __init__(self, **kwds):
		self.__dict__.update(kwds)


def pgflag(vis, stokes, flagpar):
	pgflag = mirexecb.TaskPGFlag();
	pgflag.vis = vis;
	pgflag.stokes = stokes;
	pgflag.flagpar = flagpar;
	pgflag.options = 'nodisp';
	pgflag.command = '<';
	pgflag.snarf();


class uv_split_spws(threading.Thread):
	def __init__(self, vis, spw, res):
		threading.Thread.__init__(self)		
		self.vis = vis 
		self.spw = spw
		self.res = res
	
	def run(self):
		print "Thread for SPW"+str(self.spw)+" Started"	
		uvaver = mirexec.TaskUVCat()
		uvaver.vis = self.vis
		uvaver.select = 'window('+str(self.spw)+')'
		wvis = self.vis+'_spw'+str(self.spw)+'.uv'
		uvaver.out = wvis
		uvaver.line = 'channel,60,2,1,1'
		uvaver.snarf()


		print "UVCAT'd ", self.vis, " -> ", wvis
		
		pgflag(wvis, 'ii', '3,5,5,3,5,3') 
		
		print "Flagged "+str(self.spw)

		pparams = Bunch(vis=wvis, select='-uvrange(0,1)', mode='pselfcalr', tag='', defmcut='1e-2')

		print "Phase Selfcal for "+wvis
		acf_selfcal.pselfcalr(pparams)

		print "Amp Selfcal for "+wvis
		
		aparams = Bunch(vis=wvis, select='-uvrange(0,1)', mode='aselfcalr', tag='', defmcut='1e-2',
			ergs="interval=120")
		acf_selfcal.aselfcalr(aparams)

		print "Done for "+wvis

	def get_result(self):
		return self.res

print 'starting'

if __name__=="__main__":
	s = []
	print "Splitting "+options.vis
	i = 0
	for i in range(0,8):
		res = ''
		s.append(uv_split_spws(options.vis, i+1, res))
		s[i].start()

	for j in range(0,8):
		s[j].join()

	select = ''	
	mapname = options.vis+'.map'
	beamname =  options.vis+'.beam'
	modelname =  options.vis+'.model'
	imagename = options.vis+'.image'
	acf_selfcal.invertr(options.vis+'_spw*.uv', select, mapname, beamname, robust=0.0)
	acf_selfcal.clean(mapname, beamname, modelname)
	acf_selfcal.restor(mapname, beamname, modelname, imagename)
