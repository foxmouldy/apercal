#!/usr/bin/env bash
. ./acf_batchvals.sh
# Convert the MSs to UVFs
for msname in `ls -d *.MS`
	do
		export uvname=`echo $msname | sed s/.MS/.UVF/g`
		ms2uvfits ms=$msname fitsfile=$uvname writesyscal=T multisource=T combinespw=T
	done
. ./acf_batchvals.sh
echo "MSs -> UVF completed"
time python acf_inical.py -v $uvfs -f $flags 
echo "Completed Inical"
time python acf_pgflagger.py -v $uvs --flagpar $flagpar 
echo "Completed PGFLAG"
time python acf_calcals.py -c $cals --refant 2
echo "Completed Calcal"
time python acf_cal2srcs.py -c $cal1 -s $srcs
echo "Completed Cal Copy"
time python acf_mns.py -v "*.UV" -s $sourcenames
echo "Completed Merge and Split"
time python acf_wimage.py -v $sourcefilenames
echo "Completed Imaging"
time python acf_mosaicr.py -t $tag 
echo "Completed!"
