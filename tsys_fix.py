import pyrap.tables as pt
# Get nr of channels
t = pt.table (msname + '/SPECTRAL_WINDOW')
nf = t.getcell('NUM_CHAN', 0)
t.close()
# Get nr of receptors and value (for the datatype)
t = pt.table (msname + '/SYSCAL', readonly=False)
val = t.getcell('TCAL', 0)
shp = [nf, len(val)]
shpstr = str(shp)
# Add a freq-dep column for each freq-indep column
t.addcols (pt.maketabdesc(pt.makecoldesc('TCAL_SPECTRUM', val[0], 2, shp),
                                      pt.makecoldesc('TSYS_SPECTRUM', val[0], 2, shp)))   #etc for other columns
t.close()
# Copy the freq-indep values to the freq-dep (TaQL's array function extends the values)
pt.taql ('update %s/SYSCAL set TCAL_SPECTRUM=array(TCAL,%s), TSYS_SPECTRUM=array(TSYS,%s)' % (msname,shpstr,shpstr))
