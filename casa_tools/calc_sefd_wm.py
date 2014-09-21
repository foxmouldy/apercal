# Bradley Frank, ASTRON
from tasks import *
from taskinit import *
import casac
import pylab as pl
import sys
import numpy 
import analysisUtils as au
from optparse import OptionParser

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

# O1 for Option 
parser.add_option("--ants", "-a", type = 'string', dest = 'ants', default='8,9,10', 
	help = "Antennas to be used for calculation [8,9,10]")

parser.add_option("--vis", "-v", type = 'string', dest = 'vis', default=None, 
	help = "MS to be used for calculation")

(options, args) = parser.parse_args();

if len(sys.argv)==1: 
	parser.print_help();
	dummy = sys.exit(0);

def flux_density(source='3C147', f=1.4):
	'''
	This returns the flux density for the calibrator sources listed below. 3C147 is a default. 
	source='3C147', f=frequency in GHz.
	The flux density of 3C147 and 3C286 is taken from the VLA calibrators manual 
	( http://www.vla.nrao.edu/astro/calib/manual/baars.html ):
		  Source       A 	B 	  C 	    D
        	  3C48         1.31752  -0.74090  -0.16708  +0.01525
        	  3C138        1.00761  -0.55629  -0.11134  -0.01460
	          3C147        1.44856  -0.67252  -0.21124  +0.04077
	          3C286        1.23734  -0.43276  -0.14223  +0.00345
        	  3C295        1.46744  -0.77350  -0.25912  +0.00752
	'''
	if source.upper()=='3C147':
		A =  1.44856
		B = -0.67252  
		C = -0.21124  
		D = +0.04077
	logs = A + B*pl.log10(f) + C*pl.log10(f)**2 + D*pl.log10(f)**3
	return 10**logs

def AT(s_ij=0, s_ik=0, s_jk=0, S=0):
	'''
	Calculates: SEFD = (2k/S) * (s_ij*s_ik)/(s_jk)
	'''
	kb = 1.38e3 # Boltzmann's Constant in Jy m^2 K^-1
	s_ij = pl.average(s_ij)
	s_ik = pl.average(s_ik)
	s_jk = pl.average(s_jk)
	return (2*kb/S)*(s_ij*s_ik)/(s_jk-s_ij*s_ik)	


if __name__=="__main__":	
	pl.figure(figsize=(10,15))
	chans = pl.arange(0,64) 
	spws = pl.arange(0,8)
	#vis = '11404314_S0_T0.MS'
	vis = options.vis;
	tb.open(vis+'/SOURCE')
	source = tb.getcol('NAME')
	tb.close()
	
	tb.open(vis+'/SPECTRAL_WINDOW')
	chan_freq = tb.getcol('CHAN_FREQ')
	tb.close()
	
	ants = options.ants
	i = int(ants.split(',')[0]);
	j = int(ants.split(',')[1]);
	k = int(ants.split(',')[2]);
	
	
	tb.open(vis)
	for spw in spws:
		AT_i_xx = []
		AT_i_yy = []
		AT_j_xx = []
		AT_j_yy = []
		AT_k_xx = []
		AT_k_yy = []
		print spw
		for chan in chans:
			#i = 8
			#j = 9
			#k = 10
			
			kb = 1.38e3;
	
			# Grab the Auto Correlations
			query = "ANTENNA1=="+str(i)+" && ANTENNA2=="+str(i)+" && DATA_DESC_ID=="+str(spw)
			vistab_ii = tb.query(query)
			data_ii = vistab_ii.getcol("DATA")
			data_ii_xx = data_ii[0,chan,:]
			data_ii_yy = data_ii[3,chan,:]
	
			query = "ANTENNA1=="+str(j)+" && ANTENNA2=="+str(j)+" && DATA_DESC_ID=="+str(spw)
			vistab_jj = tb.query(query)
			data_jj = vistab_jj.getcol("DATA")
			data_jj_xx = data_jj[0,chan,:]
			data_jj_yy = data_jj[3,chan,:]
	
			query = "ANTENNA1=="+str(k)+" && ANTENNA2=="+str(k)+" && DATA_DESC_ID=="+str(spw)
			vistab_kk = tb.query(query)
			data_kk = vistab_kk.getcol("DATA")
			data_kk_xx = data_kk[0,chan,:]
			data_kk_yy = data_kk[3,chan,:]
	
			
			# For sigma_ij==sigma_ji
			query = "ANTENNA1=="+str(i)+" && ANTENNA2=="+str(j)+" && DATA_DESC_ID=="+str(spw)
			vistab_ij = tb.query(query)
			data_ij = vistab_ij.getcol("DATA")
			data_ij_xx = data_ij[0,chan,:]
			data_ij_yy = data_ij[3,chan,:]
			c_ij_xx = pl.absolute(data_ij_xx)/pl.sqrt(pl.absolute(data_ii_xx)*pl.absolute(data_jj_xx))
			c_ij_yy = pl.absolute(data_ij_yy)/pl.sqrt(pl.absolute(data_ii_yy)*pl.absolute(data_jj_yy))
	
	
			# For sigma_ki==sigma_ik
			query = "ANTENNA1=="+str(i)+" && ANTENNA2=="+str(k)+" && DATA_DESC_ID=="+str(spw)
			vistab_ik = tb.query(query)
			data_ik = vistab_ik.getcol("DATA")
			data_ik_xx = data_ik[0,chan,:]
			data_ik_yy = data_ik[3,chan,:]
			c_ik_xx = pl.absolute(data_ik_xx)/pl.sqrt(pl.absolute(data_ii_xx)*pl.absolute(data_kk_xx))
			c_ik_yy = pl.absolute(data_ik_yy)/pl.sqrt(pl.absolute(data_ii_yy)*pl.absolute(data_kk_yy))
	
			
			# For sigma_ji
	
			query = "ANTENNA1=="+str(j)+" && ANTENNA2=="+str(k)+" && DATA_DESC_ID=="+str(spw)
			vistab_jk = tb.query(query)
			data_jk = vistab_jk.getcol("DATA")
			data_jk_xx = data_jk[0,chan,:]
			data_jk_yy = data_jk[3,chan,:]
			c_jk_xx = pl.absolute(data_jk_xx)/pl.sqrt(pl.absolute(data_jj_xx)*pl.absolute(data_kk_xx))
			c_jk_yy = pl.absolute(data_jk_yy)/pl.sqrt(pl.absolute(data_jj_yy)*pl.absolute(data_kk_yy))
			
			
			S = flux_density(source='3c147', f=chan_freq[chan,spw]/1e9)
			AT_i_xx.append(AT(s_ij=c_ij_xx, s_ik=c_ik_xx, s_jk=c_jk_xx, S=S))
			AT_i_yy.append(AT(s_ij=c_ij_yy, s_ik=c_ik_yy, s_jk=c_jk_yy, S=S))	
	
			AT_j_xx.append(AT(s_ij=c_jk_xx, s_ik=c_ij_xx, s_jk=c_ik_xx, S=S))
			AT_j_yy.append(AT(s_ij=c_jk_yy, s_ik=c_ij_yy, s_jk=c_ik_yy, S=S))	
	
			AT_k_xx.append(AT(s_ij=c_ik_xx, s_ik=c_jk_xx, s_jk=c_ij_xx, S=S))
			AT_k_yy.append(AT(s_ij=c_ik_yy, s_ik=c_jk_yy, s_jk=c_ij_yy, S=S))	
	
		AT_i_xx = pl.array(AT_i_xx)
		AT_i_yy = pl.array(AT_i_yy)
		sefd_i_xx = 2*kb/(AT_i_xx)
		sefd_i_yy = 2*kb/(AT_i_xx)
	
		AT_j_xx = pl.array(AT_j_xx)
		AT_j_yy = pl.array(AT_j_yy)
		sefd_j_xx = 2*kb/(AT_j_xx)
		sefd_j_yy = 2*kb/(AT_j_xx)
	
		AT_k_xx = pl.array(AT_k_xx)
		AT_k_yy = pl.array(AT_k_yy)
		sefd_k_xx = 2*kb/(AT_k_xx)
		sefd_k_yy = 2*kb/(AT_k_xx)
	
		pl.subplot(311)
		pl.plot(chan_freq[:,spw], sefd_i_xx, linestyle='-', color='blue', lw=1, alpha=0.6, label="SPW"+str(spw));
		pl.plot(chan_freq[:,spw], sefd_i_yy, linestyle='--', color='red', lw=1, alpha=0.6, label="SPW"+str(spw));
	
		pl.subplot(312)
		pl.plot(chan_freq[:,spw], sefd_j_xx, linestyle='-', color='blue', lw=1, alpha=0.6, label="SPW"+str(spw));
		pl.plot(chan_freq[:,spw], sefd_j_yy, linestyle='--', color='red', lw=1, alpha=0.6, label="SPW"+str(spw));
		
		pl.subplot(313)
		pl.plot(chan_freq[:,spw], sefd_k_xx, linestyle='-', color='blue', lw=1, alpha=0.6, label="SPW"+str(spw));
		pl.plot(chan_freq[:,spw], sefd_k_yy, linestyle='--', color='red', lw=1, alpha=0.6, label="SPW"+str(spw));
	tb.close()
	pl.subplot(311)
	pl.title("ANTENNA "+str(i))
	pl.ylim(0,1000)
	pl.subplot(312)
	pl.title("ANTENNA "+str(j))
	pl.ylim(0,1000)
	pl.subplot(313)
	pl.title("ANTENNA "+str(k))
	pl.ylim(0,1000)
	pl.xlabel('Frequency (Hz)', fontsize=20)
	pl.ylabel("SEFD", fontsize=20)
	pl.savefig("SEFD"+str(i)+str(j)+str(k)+".pdf", dpi=300)
	pl.close()
