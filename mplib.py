import re

def tkout(key, mirtout):
	'''
	Returns the value for a [key] and miriad task output [mirtout].
	If a miriad task is run from miriad-python as 
	$ mirtout = task.snarf() 
	we can extract a value corresponding to the [key] from the
	[mirtout] output.
	The output is a dictionary corresponding to the input [key], and
	should be handled appropriately.
	
	!!! This is costly in terms of performance, since it loops over
	every line of [mirtout] in order to grab the matching line. 
	'''
	for i in range(len(mirtout[0])):
		if re.search(key, mirtout[0][i]):
			l = mirtout[0][i];
			l = dict(u.split(":") for u in l.split(","));
	
	return l;

