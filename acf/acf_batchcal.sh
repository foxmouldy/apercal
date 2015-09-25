#!/usr/bin/env bash
. ./acf_batchvals.sh
# Convert the MSs to UVFs
#for msname in `ls -d *.MS`
#	do
#		export uvname=`echo $msname | sed s/.MS/.UVF/g`
#		ms2uvfits ms=$msname fitsfile=$uvname writesyscal=T multisource=T combinespw=T
#	done
. ./acf_batchvals.sh
echo "MSs -> UVF completed"
time python acf_inical.py -v $uvfs -f $flags 
echo "Completed Inical"
# PGFLAG the Calibrators only
time python acf_pgflagger.py -v $cals --flagpar $flagpar 
echo "Flagged the Calibrators"
time python acf_calcals.py -c $cals --refant 2
echo "Completed Calcal"
time python acf_cal2srcs.py -c $cal1 -s $srcs
echo "Completed Cal Copy"
time python acf_mns.py -v "*.UV" -s $sourcenames
echo "Completed Merge and Split"
time python acf_pgflagger.py -v $srcs --flagpar $flagpar 
echo "Flagged the sources"
time python acf_wimage.py -v $sourcefilenames
echo "Completed Imaging"
time python acf_mosaicr.py -t $tag 

for j in `seq 1 4`
	do
		export outdir=$tag'P'$j
		mkdir $outdir
		for i in `seq 1 8` 
			do 
				uvcat vis=ACF2G2P$j.UV select="window($i)" out=ACF2G2P$j'_window'$i'.uv'
				python selfcal.py -v ACF2G2P$j'_window'$i'.uv'
				echo $i DONE
			done
		mv ACF2G2P$j'_window*' $outdir'/'
		linmos in=$outdir/*image* out=$outdir/$tag'.LIM' options=taper
	done
linmos in=$tag*/*.LIM out=$tag'.LIM' options=taper
echo "Completed!"
