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
	uvaver.stokes='ii'
	uvaver.vis = vis
	uvaver.select = 'window('+str(spw)+')'
	wvis = vis+'_spw'+str(spw)+'.uv'

	if os.path.isdir(wvis)==False:
		uvaver.out = wvis
		uvaver.line = 'channel,58,2,1,1'
		uvaver.snarf()
		pgflag(wvis, 'ii', '3,1,1,3,5,3') 
		pgflag(wvis, 'ii', '3,1,1,3,5,3') 
	else:
		pass
	return wvis

	print "SPLIT'd ", vis, " -> ", wvis


class selfcal_threaded_masked(threading.Thread):
	def __init__(self, vis, spw, res, mask):
		threading.Thread.__init__(self)		
		self.vis = vis 
		self.spw = spw
		self.res = res
		self.mask = mask
	
	def run(self):
		
		wvis = self.vis+'_spw'+str(self.spw)+'.uv'

		print "Thread for SPW"+str(self.spw)+" Started"	

		pparams = Bunch(vis=wvis, maskname=self.mask, select='-uvrange(0,1)', mode='pselfcalr', tag='', defmcut='1e-2')

		print "Phase Selfcal for "+wvis
		acf_selfcal.pselfcalr(pparams)

		print "Thread for SPW"+str(self.spw)+" Started"	

		#pparams = Bunch(vis=wvis, select='-uvrange(0,1)', mode='aselfcalr', tag='', defmcut='1e-2')

		#print "Amp Selfcal for "+wvis
		#acf_selfcal.aselfcalr(pparams)

		print "Done Selfcal-LSM for "+wvis
		time.sleep(0.1)
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
		
		wvis = splitspw(self.vis, self.spw)
		os.system("rm -r "+wvis+".*")	
		#pgflag(wvis, 'ii', '3,1,1,3,5,3') 
		#pgflag(wvis, 'ii', '3,1,1,3,5,3') 
		#print "Flagged "+str(self.spw)

		pparams = Bunch(vis=wvis, select='-uvrange(0,1)', mode='pselfcalr', tag='', defmcut='1e-2')

		print "Phase Selfcal for "+wvis
		acf_selfcal.pselfcalr(pparams)

		pparams = Bunch(vis=wvis, select='-uvrange(0,1)', mode='pselfcalr', tag='', defmcut='5e-3')

		print "Phase Selfcal for "+wvis
		acf_selfcal.pselfcalr(pparams)


		#pparams = Bunch(vis=wvis, select='-uvrange(0,1)', mode='aselfcalr', tag='', defmcut='5e-3', ergs="interval=10")

		#print "Amp Selfcal for "+wvis
		#acf_selfcal.pselfcalr(pparams)

		print "Done Selfcal for "+wvis
		time.sleep(0.1)

	def get_result(self):
		return self.res

def full_imager(vis, defmcut='1e-2', select=''):
	mapname = vis+'.map'
	beamname =  vis+'.beam'
	modelname =  vis+'.model'
	imagename = vis+'.image'
	maskname = vis+'.mask'
	acf_selfcal.imager(vis+'_spw*.uv', select, mapname, beamname, imagename, modelname, maskname=maskname, cutoff=1e-3)
	immax, imunits = acf_selfcal.getimmax(imagename);
	if str(immax)=='nan':
		immax = float(defmcut);
	acf_selfcal.maths(imagename, immax/10, maskname);
	acf_selfcal.imager(vis+'_spw*.uv', select, mapname, beamname, imagename, modelname, maskname=maskname, cutoff=immax/30.)
	acf_selfcal.maths(imagename, immax/20, maskname);
	acf_selfcal.imager(vis+'_spw*.uv', select, mapname, beamname, imagename, modelname, maskname=maskname, cutoff=immax/40.)


if __name__=="__main__":
	s = []
	print "Splitting "+options.vis
	i = 0
	for i in range(0,8):
		time.sleep(0.1)
		res = ''
		s.append(selfcal_threaded(options.vis, i+1, res))
		s[i].start()
	for j in range(0,8):
		s[j].join()
	
	select = ''
	full_imager(options.vis)

	s = []
	for i in range(0,8):
		time.sleep(0.1)
		res = ''
		s.append(selfcal_threaded_masked(options.vis,  i+1, res, options.vis+'.mask',))
		s[i].start()
	for j in range(0,8):
		s[j].join()
	full_imager(options.vis)
