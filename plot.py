import aipy
import pylab as pl
from astropy.time import Time
from matplotlib import dates
import datetime
import mirexecb
import cmath
'''
Convenience module to plot MIRIAD Data
'''

def amptime(uv, baseline="0_1", pol="xx", applycal=False):
	'''
	Plots Amp vs Time for a single baseline. 
	'''
	fig = pl.figure()
	ax = fig.add_subplot(111)
	aipy.scripting.uv_selector(uv, baseline, pol)
	for preamble, data, flags in uv.all(raw=True):
		uvw, t, (i, j) = preamble
		ax.plot(t, pl.average(pl.absolute(data)), 'ks', mec='None', alpha=0.2, ms=5)
	hfmt = dates.DateFormatter('%m/%d %H:%M')
	ax.xaxis.set_major_locator(dates.HourLocator())
	ax.xaxis.set_major_formatter(hfmt)
	ax.set_ylim(bottom = 0)
	pl.xticks(rotation='vertical')	
	# TODO: Apply the calibration and flag data.
	# TODO: Modes - all, baseline, antenna

def phasetime(uv, baseline="0_1", pol="xx", applycal=False):
	'''
	Plots Amp vs Time for a single baseline. 
	'''
	uv.rewind()
	fig = pl.figure()
	ax = fig.add_subplot(111)
	aipy.scripting.uv_selector(uv, baseline, pol)
	for preamble, data, flags in uv.all(raw=True):
		uvw, t, (i, j) = preamble
		ax.plot(t, pl.average(cmath.phase(data)), 'ks', mec='None', alpha=0.2, ms=5)
	hfmt = dates.DateFormatter('%m/%d %H:%M')
	ax.xaxis.set_major_locator(dates.HourLocator())
	ax.xaxis.set_major_formatter(hfmt)
	ax.set_ylim(bottom = 0)
	pl.xticks(rotation='vertical')	
	# TODO: Apply the calibration and flag data.
	# TODO: Modes - all, baseline, antenna
