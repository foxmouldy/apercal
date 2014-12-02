#!/usr/bin/env python
'''
mk-nvss-lsm.py
This file uses astropy and miriad to construct an NVSS local sky model based on the coordinates
extracted from a template file. This uses the astroquery tool to query Vizier for all the sources
within the 1-degree field of view. 
'''

__author__ = "Bradley Frank"
__copyright__ = "ASTRON"
__credits__ = ["Kijeong Yim"]
__email__ = "frank@astron.nl"

import os
import pylab as pl
import mirexec
from astroquery.vizier import Vizier
from astropy.coordinates import Angle, ICRS, Distance, SkyCoord
import astropy.coordinates as coord
from astropy import units as u
import sys
from optparse import OptionParser
from astropy.io import ascii
deg2rad = pl.pi/180.

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--infile", "-i", type = 'string', dest = 'infile', default=None, 
	help = 'Template File to Extract Coordinates and RA/Dec [None]')
parser.add_option("--outfile", "-o", type = 'string', dest = 'outfile', default=None, 
	help = 'Output file with NVSS point source model <infile>-nvss-lsm')

(options, args) = parser.parse_args() 
if len(sys.argv)==1 or options.infile==None: 
	parser.print_help()
	dummy = sys.exit(0)

infile = options.infile
if options.outfile!=None:
	outfile = options.outfile
else:
	outfile = options.infile+'-nvss-lsm'

def ann_writer(options, x):
	annfile = options.outfile+'.ann'
	ann = open(annfile, 'w')
	ann.writelines("COORD W\n")
	ann.writelines("PA STANDARD\n")
	ann.writelines("COLOR ORANGE\n")
	ann.writelines("FONT hershey14\n")
	for i in range(0,len(x)):
		line = "CROSS "+str(x[i]["_RAJ2000"])+" "+str(x[i]["_DEJ2000"])+" 0.05 0.05 45.\n"
		ann.writelines(line)
	ann.close()

def fixra(ra0):
	R = ''
	s = 0
	for i in ra0:
		if i==':':
			if s==0:
				R+='h'
				s+=1
			else:
				R+='m'
		else:
			R+=i
	return R

def getradec(infile):
	'''
	getradec: module to extract the pointing centre ra and dec from a miriad image file. Uses
	the PRTHD task in miriad
	inputs: infile (name of file)
	returns: c, an instance of the astropy.coordinates SkyCoord class which has a few convenient
	attributes.
	'''
	prthd = mirexec.TaskPrintHead()
	prthd.in_ = infile
	p = prthd.snarf()
	ra0 = p[0][12][15:32].replace(' ','')
	ra0 = list(ra0)
	ra0 = fixra(ra0)
	dec0 = p[0][13][15:32].replace(' ','')
	coords = [ra0, dec0]
	c = SkyCoord(ICRS, ra=ra0, dec=dec0, unit=(u.deg,u.deg))
	return c

def query_nvss(options, ra0, dec0, s=">20"):
	'''
	query_nvss: module which queries the NVSS using the Vizier protocol. 
	inputs: ra0, dec0, s="<20"
	ra0 = the central ra in degrees
	dec0 = the central dec in degrees
	s = the flux cutoff
	returns L, M (relative coordinates in degrees), N (number of sources), S (1.4GHz Flux
	Density in mJy)
	'''
	v = Vizier(column_filters={"S1.4":s})
	result = v.query_region(coord.SkyCoord(ra=ra0, dec=dec0, unit=(u.deg, u.deg), frame='icrs'), 
	    radius=Angle(1, "deg"), catalog='NVSS')
	ra = result[0]['_RAJ2000']
	dec = result[0]['_DEJ2000']
	N = len(result[0])
	L = (ra-ra0)*pl.cos(dec*deg2rad)
	M = dec-dec0
	S = result[0]['S1.4']
	ascii.write(result[0], options.outfile+'.dat', format='tab') 
	ann_writer(options, result[0])
	return L, M, N, S

def mk_lsm(options):
	'''
	mk_lsm: The module that makes the NVSS LSM using the miriad task IMGEN.
	Needs options.infile (template) and options.outfile (name of output point source model)
	'''

	# NOTE: Classic cos^6 model of the WSRT PB used to calculate apparent fluxes. Here we use c=68.
	PB = lambda c, v, r: (pl.cos(c*v*r))**6

	# NOTE: Grab the central coordinates from the template file. 
	c = getradec(infile)
	ra0 = c.ra.deg
	dec0 = 	c.dec.deg

	# NOTE: Query the NVSS around the central pointing
	L, M, N, S = query_nvss(options, ra0, dec0, s='>10')
	L_asec = L*3600.
	M_asec = M*3600.

	# NOTE: Make the LSM!
	imgen = mirexec.TaskImGen()
	imgen.in_ = infile
	imgen.out = outfile
	os.system('rm -r '+str(imgen.out))
	objs = ''
	spars = ''
	for i in range(0,N):
	    objs+= 'point,'
	    d2point = L[i]**2+M[i]**2
	    S_app = S[i]*PB(c=68, v=1.420, r=d2point)
	    spars+= str(S_app/1e3)+','+str(L_asec[i])+','+str(M_asec[i])+','
	
	imgen.factor=0
	imgen.object = objs[:-1]
	imgen.spar = spars[:-1]
	imgen.snarf()

if __name__=='__main__':
	mk_lsm(options)
	print "Done!"
