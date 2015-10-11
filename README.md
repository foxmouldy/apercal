**CINEMA** stands for: Calibration and Imaging in ipython Notebooks using **MIRIAD** for APERTIF. 

This **APERCAL**  branch provides some generic tools and wrappers that allow you to do the full calibration of WSRT data within an IPython/Jupyter Notebook, using **MIRIAD** tasks. Documentation and use-cases are available in the ipython-notebooks/ directory. 


## Installation

Download the latest version of the **CINEMA** branch of **APERCAL** into a convenient location. 

Add the full path of the **APERCAL** directory to your $PYTHONPATH. You can do this by adding the following line to the end of your .bashrc file:

```
export PYTHONPATH=$PYTHONPATH:"path-to-apercal"
```

That's it!

You will need the package **avconv** to use the functions in `mplot.py`. This is available on Ubuntu distributions, but a fix hasn't been implemented for Mac OS X yet - not that you'll need `mplot.py` if you're using this on your laptop :)

## Usage

The intended usage of the **CINEMA** branch is within an IPython/Jupyter Notebook (https://jupyter.org/). However, you can easily use the libraries in any Python script. 

You will need to have **MIRIAD** installed on your system. The **MIRIAD** environment should be setup before you start the notebook, so that **APERCAL** knows where to find **MIRIAD** tasks.

The main calibration tools are contained in the `crosscal.py` script, while the `lib.py` script contains generic tools and functions that are used by most calibration functions. This includes the class `miriad` which hooks to **MIRIAD** tasks. 

### Within a Notebook

Assuming that you're using **APERCAL** within a Notebook, you will need a header cell to import and define the necessary libraries. Here's an example:

```python
from apercal import lib
lib.setup_logger('debug', logfile='/home/user/my-log-file.log')
%matplotlib inline
from apercal import calibrate
ccal = calibrate.crosscal()
scal = calibrate.wselfcal()
```

### Logging

**APERCAL** tasks and functions interact through the Python logger. All the output from **MIRIAD** tasks and the **APERCAL** functions get dumped into the log file. Its best to use a new different log file for each Notebook that you use.

You can use the logger at two levels. The *info* level provides high-level messages from tasks and functions, i.e., that tasks are started and completed. The *debug* level provides low-level messages from tasks and functions, i.e., the full output. 
Errors and warnings are always reported. Using `quiet=True` will suppress the messages completely, but the messages will still get logged to an output file, which can be viewed by *tailing* it:
```
tail -n +1 -f /home/user/my-log-file.log
```

### calibrate.py
This script contains three important classes - source, crosscal and wselfcal (WSRT selfcal). The source class helps with book-keeping of paths and filenames of input and output datasets. 
The crosscal and wselfcal classes wrap commonly used **MIRIAD** tasks and python functions for cross-calibration and self-calibration, respectively. 
With the crosscal class you can import data-sets, flag data, combine visibility sets and, of course, do cross-calibration. 
With the selfcal class you can do iterative masking, imaging and selfcal of a visibility set. 

## Examples

In the [ipython-notebooks/](ipython-notebooks/) directory you will find several examples of **APERCAL** usage. The rendered output of the Notebooks will appear on the **Github** website. I recommend that you start with the [**Using MIRIAD Tasks in the Notebook**](ipython-notebooks/Using%20MIRIAD%20Tasks%20in%20the%20Notebook.ipynb). This provides a use-case of how to image a visibility dataset within the Notebook. The [**PLOTTING**](ipython-notebooks/PLOTTING.ipynb) and [**PGFLAG**](ipython-notebooks/PGFLAG.ipynb) Notebooks provide short examples of how to plot UV data and do automated flagging, respectively. 

Finally, there are three use cases which provide comprehensive use-cases for the cross-calibration, self-calbration and imaging of WSRT data. You should start with the [**UGC9519 Tutorial**](ipython-notebooks/UGC9519.ipynb), and refer to the [**NGC3998**](ipython-notebooks/NGC3998.ipynb) and [**NGC4278**](ipython-notebooks/NGC4278.ipynb) Notebooks for more tips and ideas for different datasets. The [**NGC4278**](ipython-notebooks/NGC4278.ipynb) contains a block on importing Measurement Sets. 