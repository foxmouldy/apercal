import mirexecb 
import acos
import acim
import plot
import mirplot
import crosscal
#import mselfcal

def get_source_names(vis=None):
	if vis!=None:
		uvindex = mirexecb.TaskUVIndex ()
		uvindex.vis = vis
		u = uvindex.snarf ()
		i = [i for i in range(0,len(u[0])) if "pointing" in u[0][i]]
		N = len(u[0])
		s_raw = u[0][int(i[0]+2):N-2]
		sources = []
		for s in s_raw:
			sources.append(s.replace('  ', ' ').split(' ')[0])
		return sources
	else:
		print "get_source_names needs a vis!"
		
