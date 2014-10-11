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

def splitspw(vis, spw):
	uvaver = mirexec.TaskUVAver()
	uvaver.vis = vis
	uvaver.select = 'window('+str(spw)+')'
	wvis = vis+'_spw'+str(spw)+'.uv'
	uvaver.out = wvis
	uvaver.line = 'channel,60,2,1,1'
	uvaver.snarf()

	print "SPLIT'd ", self.vis, " -> ", wvis


class selfcal_threaded_masked(threading.Thread):
	def __init__(self, vis, spw, res, mask):
		threading.Thread.__init__(self)		
		self.vis = vis 
		self.spw = spw
		self.res = res
		self.mask = mask
	
	def run(self):
		print "Thread for SPW"+str(self.spw)+" Started"	
		pparams = Bunch(vis=wvis, maskname=mask, select='-uvrange(0,1)', mode='pselfcalr', tag='', defmcut='1e-2')

		print "Phase Selfcal for "+wvis
		acf_selfcal.pselfcalr(pparams)

		print "Done Selfcal-LSM for "+wvis

	def get_result(self):
		return self.res



class selfcal_threaded(threading.Thread):
	def __init__(self, vis, spw, res):
		threading.Thread.__init__(self)		
		self.vis = vis 
		self.spw = spw
		self.res = res
	
	def run(self):
		print "Thread for SPW"+str(self.spw)+" Started"	
		splitspw(self.vis, self.spw)
		
		pgflag(wvis, 'ii', '3,5,5,3,5,3') 
		
		print "Flagged "+str(self.spw)

		pparams = Bunch(vis=wvis, select='-uvrange(0,1)', mode='pselfcalr', tag='', defmcut='1e-2')

		print "Phase Selfcal for "+wvis
		acf_selfcal.pselfcalr(pparams)

		print "Amp Selfcal for "+wvis
		
		aparams = Bunch(vis=wvis, select='-uvrange(0,1)', mode='aselfcalr', tag='', defmcut='1e-2',
			ergs="interval=1200")
		acf_selfcal.aselfcalr(aparams)

		print "Done Selfcal for "+wvis

	def get_result(self):
		return self.res

def full_imager(vis, defmcut='1e-2', select=''):
	mapname = vis+'.map'
	beamname =  vis+'.beam'
	modelname =  vis+'.model'
	imagename = vis+'.image'
	maskname = vis+'.mask'
	acf_selfcal.invertr(vis+'_spw*.uv', select, mapname, beamname, robust=0.0)
	acf_selfcal.clean(mapname, beamname, modelname)
	acf_selfcal.restor(mapname, beamname, modelname, imagename)
	immax, imunits = acf_selfcal.getimmax(imname);
	if str(immax)=='nan':
		immax = float(defmcut);
	acf_selfcal.maths(imname, immax/10, maskname);
	acf_selfcal.imager(vis, select, mapname, beamname, imname, modelname, maskname=maskname, cutoff=immax/30.)

#print 'starting'

if __name__=="__main__":
	s = []
	print "Splitting "+options.vis
	i = 0
	for i in range(0,8):
		res = ''
		s.append(selfcal_threaded(options.vis, i+1, res))
		s[i].start()

	for j in range(0,8):
		s[j].join()
	

	select = ''
	full_imager(options.vis)

	s = []
	for i in range(0,8):
		res = ''
		s.append(selfcal_threaded_masked(options.vis,  i+1, res, options.vis+'.mask',))
		s[i].start()

	for j in range(0,8):
		s[j].join()
	
	full_imager(options.vis)
	#mapname = options.vis+'.map'
	#beamname =  options.vis+'.beam'
	#modelname =  options.vis+'.model'
	#imagename = options.vis+'.image'
	#acf_selfcal.invertr(options.vis+'_spw*.uv', select, mapname, beamname, robust=0.0)
	#acf_selfcal.clean(mapname, beamname, modelname)
	#acf_selfcal.restor(mapname, beamname, modelname, imagename)
