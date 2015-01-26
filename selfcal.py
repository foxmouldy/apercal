import mirexec
from optparse import OptionParser
import sys
import os
from ConfigParser import SafeConfigParser

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--vis", "-v", type = 'string', dest = 'vis', default=None, 
	help = "Vis to be selfcal'd [None]");
parser.add_option("--settings", "-s", type = 'string', dest='settings', default=None, 
	help = 'Settings file to be used [None]')

(options, args) = parser.parse_args();

if __name__=="__main__":
	if len(sys.argv)==1: 
		parser.print_help();
		dummy = sys.exit(0);

class Bunch: 
	def __init__(self, **kwds): 
		self.__dict__.update(kwds)

def getimmax(imname):
	imstat = mirexec.TaskImStat()
	imstat.in_ = imname;
	imstats = imstat.snarf();
	immax = float(imstats[0][10][51:61]);
	imunits = imstats[0][4];
	return immax, imunits

def invertr(vis, select, mapname, beamname, robust=-2.0, line=''):
	invert = mirexec.TaskInvert()
	invert.vis = vis;
	invert.select = select;
	invert.line = line;
	os.system('rm -r '+mapname)
	os.system('rm -r '+beamname)
	invert.map = mapname
	invert.beam = beamname
	invert.options = 'double,mfs';
	invert.slop = 0.5
	invert.stokes = 'ii'
	invert.imsize = 1500
	invert.cell = 4
	invert.robust= robust 
	tout = invert.snarf();

def clean(mapname, beamname, modelname, maskname=None, cutoff=0.0):
	clean = mirexec.TaskClean()
	clean.map = mapname;
	clean.beam = beamname;
	clean.cutoff = cutoff;
	if maskname!=None:
		clean.region='mask('+maskname+')';
		clean.niters = 10000000
	else:
		clean.niters = 1000
	os.system('rm -r '+modelname);
	clean.out = modelname; 
	tout = clean.snarf()

def restor(mapname, beamname, modelname, imname):
	os.system('rm -r '+imname)
	restor = mirexec.TaskRestore()
	restor.beam = beamname;
	restor.map = mapname
	restor.model = modelname
	restor.out = imname
	tout = restor.snarf()

# Step 0, make an LSM and use this as the first step in Selfcal

# Step 1, Make a dirty image
# invert_bunch should be replaced by a settings file. 


invert_bunch = Bunch(vis=options.vis, select='-uvrange(0,1)', 
	mapname='map_temp', beamname='beam_temp', maskname = 'mask_temp', modelname='model_temp', imname = 'image_temp', 
	robust='-2.0', line='')

invertr(invert_bunch.vis, invert_bunch.select, invert_bunch.mapname, invert_bunch.beamname)
immax, imunits = getimmax(invert_bunch.mapname)
maths(imname, immax/3, maskname)
clean(invert_bunch.mapname, invert_bunch.beamname, invert_bunch.model, invert_bunch.mask,
	cutoff=immax/30)
restor(invert_bunch.mapname, invert_bunch.beamname, invert_bunch.modelname, invert_bunch.imname)

immax, imunits = getimmax(invert_bunch.imname)
maths(imname, immax/9, maskname)
clean(invert_bunch.mapname, invert_bunch.beamname, invert_bunch.model, invert_bunch.mask,
	cutoff=immax/90)
restor(invert_bunch.mapname, invert_bunch.beamname, invert_bunch.modelname, invert_bunch.imname)

immax, imunits = getimmax(invert_bunch.imname)
maths(imname, immax/27, maskname)
clean(invert_bunch.mapname, invert_bunch.beamname, invert_bunch.model, invert_bunch.mask,
	cutoff=immax/270)
restor(invert_bunch.mapname, invert_bunch.beamname, invert_bunch.modelname, invert_bunch.imname)

immax, imunits = getimmax(invert_bunch.imname)
maths(imname, immax/81, maskname)
clean(invert_bunch.mapname, invert_bunch.beamname, invert_bunch.model, invert_bunch.mask,
	cutoff=immax/810)
restor(invert_bunch.mapname, invert_bunch.beamname, invert_bunch.modelname, invert_bunch.imname)
