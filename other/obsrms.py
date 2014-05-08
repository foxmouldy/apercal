#! /usr/bin/env python
#http://astro.berkeley.edu/~wright/obsrms.py
#  Help #
desc="""
    Calculate theoretical rms noise for radio telescopes.
INPUTS: Integration time on source in minutes, Number of antennas in array,
SSB system temperature (K), antdiam and aperture efficiency, or jyperk (Jy/K).
Freq (GHz) is used to compute wavelength. Angular resolution FWHM in arcsec.
Bandwidth (MHz).
Velocity resolution (km/s) for spectral line observations.
Correlator efficiency factor. 2-, 3-, 4-level coreff=0.64, 0.81, 0.88.
Phase noise reduces the signal, effectively increasing the observed RMS noise in the data by a factor exp(rmsphase(radians)**2/2.).
    History  mchw 28may96  original MIRIAD version. Python 03oct2012
    Version  14jan2014
"""
import math
from optparse import OptionParser
parser = OptionParser(description=desc)
parser.add_option("-t", "--telescope", help="known telescopes: aca, alma, ata, arecibo, baobab, bima, carma, gbt, iram-pdb, iram-30m, sma, sza, vla, wsrt, paper-64", default='carma')
parser.add_option("-f", "--freq", help="frequency(GHz)", dest='freq', action='store', type='float', default=0.)
parser.add_option("-b", "--bandwidth", help="bandwidth(MHz)", dest='bw', action='store', type='float', default=0.)
parser.add_option("-v", "--velocity", help="velocity resolution(km/s)", dest='deltav', action='store', type='float', default=0.)
parser.add_option("-n", "--nants", help="number of antennas)", dest='nants', action='store', type='float', default=0.)
parser.add_option("-i", "--inttime", help="integration time(minutes)", dest='inttime', action='store', type='float', default=1.)
parser.add_option("-j", "--jyperk", help="Jansky per Kelvin", dest='jyperk', action='store', type='float', default=0.)
parser.add_option("-a", "--theta", help="angular resolution(arcsec)", dest='theta', action='store', type='float', default=0.)
parser.add_option("-s", "--systemp", help="SSB system temperature(K)", dest='tsys', action='store', type='float', default=0.)
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()
print options
print args

print "Calculate theoretical rms noise for telescope:" 
print options.telescope

#  constants #
kB = 1.3806e-23     # boltzmann's constant, joule K-1
c = 2.9979e8        # c in m/sec
h = 6.626e-27       # plank's constant, erg s
au = 1.496e13       # 1 AU in cm
pc = 3.0856e18	    # 1 pc in cm
G = 6.6732e-8       # grav constant in dynes cm^2 g^-2
PI = math.pi

#  Get the telescope parameters for known telescopes.  #
if options.telescope == "aca" :
    nants = 12      # number of antennas
    tsys = 100      # K
    antdiam = 7     # m
    anteff = 0.6    # aperture efficiency
    freq = 230      # GHz
    bw = 4000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 5       # arcsec

elif options.telescope == "alma" :
    nants = 50      # number of antennas
    tsys = 100      # K
    antdiam = 12    # m
    anteff = 0.6    # aperture efficiency
    freq = 230 	    # GHz
    bw = 4000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 1       # arcsec

elif options.telescope == "arecibo" :
    nants = 1       # number of antennas
    tsys = 35       # K
    antdiam = 300   # m
    anteff = 0.6    # aperture efficiency
    freq = 1.4      # GHz
    bw = 4000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 200      # arcsec

elif options.telescope == "ata" :
    nants = 42      # number of antennas
    tsys = 40       # K
    antdiam = 6.1   # m
    anteff = 0.6    # aperture efficiency
    freq = 3        # GHz
    bw = 600.       # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 150    # Jy/K
    theta = 100     # arcsec

elif options.telescope == "baobab" :
    nants = 42      # number of antennas
    tsys = 50       # K
    antdiam = 1.3   # m (1 tile of 4 dipoles)
    anteff = 0.6    # aperture efficiency
    freq = 0.6 	    # GHz (400-800 MHz)
    bw = 400.       # MHz
    coreff = 1.0    # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 3600    # 1-degree

elif options.telescope == "bima" :
    nants = 9       # number of antennas
    tsys = 300      # K
    antdiam = 6.1   # m
    anteff = 0.6    # aperture efficiency
    freq = 100      # GHz
    bw = 800.       # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 150    # Jy/K
    theta = 1       # arcsec

elif options.telescope == "carma" :
    nants = 15      # number of antennas
    tsys = 300      # K
    antdiam = 8     # m
    anteff = 0.6    # aperture efficiency
    freq = 230 	    # GHz
    bw = 8000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 10      # arcsec

elif options.telescope == "gbt" :
    nants = 1       # number of antennas
    tsys = 35       # K
    antdiam = 100   # m
    anteff = 0.6    # aperture efficiency
    freq = 1.4 	    # GHz
    bw = 4000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 514      # arcsec

elif options.telescope == "iram-pdb" :
    nants = 6       # number of antennas
    tsys = 100      # K
    antdiam = 15    # m
    anteff = 0.6    # aperture efficiency
    freq = 230 	    # GHz
    bw = 4000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 1       # arcsec

elif options.telescope == "iram-30m" :
    nants = 1       # number of antennas
    tsys = 100      # K
    antdiam = 30    # m
    anteff = 0.6    # aperture efficiency
    freq = 230 	    # GHz
    bw = 4000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 10      # arcsec

elif options.telescope == "paper-64" :
    nants = 64      # number of antennas
    tsys = 380      # K
    antdiam = 3     # m
    anteff  = 0.89  # aperture efficiency. effective area is 8 m^2
    freq = 0.15     # GHz
    bw = 100.       # MHz
    coreff = 1.0    # correlator efficiency. 16 level.
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 3600    # 1-degree

elif options.telescope == "sma" :
    nants = 8       # number of antennas
    tsys = 300      # K
    antdiam = 6     # m
    anteff = 0.7    # aperture efficiency
    freq = 230 	    # GHz
    bw = 8000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 10      # arcsec

elif options.telescope == "sza" :
    nants = 8       # number of antennas
    tsys = 30       # K
    antdiam = 3.5   # m
    anteff = 0.7    # aperture efficiency
    freq = 30 	    # GHz
    bw = 8000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 10      # arcsec

elif options.telescope == "vla" :
    nants = 27      # number of antennas
    tsys = 35       # K
    antdiam = 25    # m
    anteff = 0.6    # aperture efficiency
    freq = 1.4 	    # GHz
    bw = 8000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 10      # arcsec

elif options.telescope == "wsrt" :
    nants = 14      # number of antennas
    tsys = 35       # K
    antdiam = 25    # m
    anteff = 0.6    # aperture efficiency
    freq = 1.4 	    # GHz
    bw = 8000.      # MHz
    coreff = 0.88   # correlator efficiency
    rmsphase = 0    # RMS phase noise (degrees)
    jyperk = 0      # Jy/K
    theta = 10      # arcsec

else:
    print "Unknown telescope"
    exit()

#  options override telescope parameters

if options.bw > 0:
    bw = options.bw
if options.freq > 0:
    freq = options.freq
if options.jyperk > 0:
    jyperk = options.jyperk
if options.nants > 0:
    nants = options.nants
if options.tsys > 0:
    tsys = options.tsys
if options.theta > 0:
    theta = options.theta

inttime = options.inttime
if jyperk == 0:
    jyperk = 2*kB*1e26/(PI/4 * antdiam*antdiam * anteff)

# lambda in mm  .Note lambda is a forbidden python variable name
lamm = 1e-6 * c / freq   
deltav = options.deltav
if deltav > 0:
    bw=deltav/lamm
else:
    deltav=bw*lamm

# echo inputs to user. #
print " nants=",nants," antdiam=",antdiam," anteff=",anteff," jyperk=",jyperk
print " tsys=",tsys," freq=",freq," lambda=",lamm," deltav=",deltav," bw=",bw
print " inttime=",inttime," theta=",theta," coreff=",coreff," rmsphase=",rmsphase

# Convert to MKS units.

lamm=lamm*1.e-3
bw=bw*1.e6
inttime=inttime*60
theta = theta *PI/180/3600

# Efficiency factors.

if coreff > 0:
    tsys=tsys/coreff
if rmsphase > 0:
    tsys=tsys*exp((PI/180.*rmsphase)**2/2.)

# Calculate rms_Jy #

if nants < 2:
    rms_Jy = tsys*jyperk/math.sqrt(2.*bw*inttime)
else:
    rms_Jy = tsys*jyperk/math.sqrt(2.*bw*inttime*nants*(nants-1)/2.)

# Calculate rms_Tb #

omega = PI * theta * theta /(4.*math.log(2))
rms_Tb = rms_Jy * 1.e-26 * lamm * lamm / (2.* kB * omega)
print 	' Rms Flux density:', rms_Jy*1000., ' mJy/beam;',' Rms Brightness:', rms_Tb, ' K'

