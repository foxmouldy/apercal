from tasks import *
from taskinit import *
import casac
import pylab as pl
import sys
from optparse import OptionParser

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

# O1 for Option

parser.add_option("--ra", type='string', dest='ra', default='10h00m00.0s', 
		help="Right Ascension of Centre of Field  [10h00m00.0s]")
parser.add_option("--dec", type='string', dest='dec', default='-30d00m00.0s', 
		help="Declination of Centre of Field [-30d00m00.0s]")
parser.add_option("-g", type='string', dest='g', default=None,
		help='Text file containing list of Gaussian Components [None]')
parser.add_option("-i", type='string', dest='i', default='1024,1024,1,1,1', 
		help="Dimensions of output image dra,ddec,dcell,dfreq,dstokes [1024,1024,1,1,1]")
parser.add_option("-f", type='string', dest='f', default="Gaussian", 
		help = "Name for output files [Gaussian]")


(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

def make_gausses(options):
	direction = "J2000 "+options.ra+" "+options.dec;
	cl.done()
	g = pl.recfromtxt(options.g);
	dra = int(options.i.split(',')[0]);
	ddec = int(options.i.split(',')[1]);
	dcell = options.i.split(',')[2];
	dfreq = int(options.i.split(',')[3]);
	dstokes = int(options.i.split(',')[4]);
	ia.fromshape(options.f+".im",[dra, ddec,dfreq,dstokes],overwrite=True)
	cs=ia.coordsys()
	cs.setunits(['rad','rad','','Hz'])
	cell_rad=qa.convert(qa.quantity(dcell+"arcsec"),"rad")['value']
	cs.setincrement([-cell_rad,cell_rad],'direction')
	cs.setreferencevalue([qa.convert(options.ra,'rad')['value'], qa.convert(options.dec,'rad')['value']],type="direction")
	cs.setreferencevalue("1.420GHz",'spectral')
	cs.setincrement('1GHz','spectral')
	ia.setcoordsys(cs.torecord())
	ia.setbrightnessunit("Jy/pixel")
	for i in range(len(g)):
		direction = "J2000 "+g[i][0]+" "+g[i][1];
		cl.addcomponent(dir=direction, flux=g[i][2], fluxunit='Jy', freq='1.420GHz',
			shape="Gaussian",  majoraxis=g[i][3], minoraxis=g[i][4], positionangle=g[i][5])
	
	ia.modify(cl.torecord(), subtract=False)
	exportfits(imagename=options.f+'.im',fitsimage=options.f+'.fits',overwrite=True)

if __name__=="__main__":
	make_gausses(options);
