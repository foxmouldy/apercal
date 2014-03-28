import casac
import pylab as pl
import scipy.signal
from tasks import * 
from taskinit import * 
import cmath
import numpy
from optparse import OptionParser

global options
global args

usage = "usage: %prog options"
parser = OptionParser(usage=usage);

parser.add_option("--btin", type='string', dest='btin', default=None, 
	help = 'Input bandpass table [None]')
parser.add_option("--btout", type='string', dest='btout', default=None, 
	help = 'Output bandpass table [None]');
parser.add_option("--window", type='string', dest='window', default='hanning',
	help = 'Window for smoothing: flat/hanning/hamming/bartlett/blackman [hanning]');
parser.add_option("--wl", type=int, dest='wl', default=21,
	help = 'Window length [21]');

(options, args) = parser.parse_args();

if len(sys.argv)==1:
	parser.print_help();
	dummy = sys.exit(0);


def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    Used the method from http://wiki.scipy.org/Cookbook/SignalSmooth 
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y


def bsmooth(options):
	#btable = 'day22_time_ave_split_spw0.B0_s'
	btable = options.btin
	tb.open(btable)
	tb.copy(options.btout, deep=True, valuecopy=True);
	tb.close();
	tb.open(options.btin, nomodify=False);
	C = tb.getcol('CPARAM')
	Cx = C*1;
	N = pl.shape(C);
	wl = options.wl;
	for i in range(N[0]):
		for j in range(N[2]):
			Cx[i,:,j] = smooth(C[i,:,j], window_len=wl, window=options.window)[(wl-1)/2:N[1]+(wl-1)/2];
	
	
	pl.plot(C[0,:,14], 'ro', mec='red', alpha=0.5);
	pl.plot(Cx[0,:,14], 'k-', lw=2);
	tb.putcol(columnname='CPARAM', value=Cx);
	tb.close()
	pl.savefig(options.btout+'.png', dpi=300)
	pl.close();

if __name__=='__main__':
	bsmooth(options);
