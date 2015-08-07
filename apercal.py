import imp
try:
    imp.find_module('mirexecb')
    found = True
    import mirexecb
except ImportError:
    found = False
try:
    imp.find_module('mirexec')
    found = True
    import mirexec
except ImportError:
    found = False
import acos
import acim
import plot
import mirplot2
import crosscal2
import selfcal
from ConfigParser import SafeConfigParser
import subprocess
import mynormalize
import pylab as pl
import lib
import os
import tools