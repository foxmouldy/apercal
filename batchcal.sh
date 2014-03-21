#!/usr/bin/env bash
source ./batchvals.sh

# Convert the MSs to UVFs
for msname in `ls -d *.MS`
	do
		export uvname=`echo $msname | sed /.MS/UVF/g`
		ms2uvfits ms=$msname fitsfile=$uvname writesyscal=T multisource=T combinespw=T
	done
echo "MSs -> UVF completed"
python acf_inical.py -v $uvfs -f $flags 
echo "Completed Inical"
python pgflagger.py -v $uvs --flagpar $flagpar 
echo "Completed PGFLAG"
python acf_calcals.py -c $cals
echo "Completed Calcal"
python acf_cal2srcs.py -c $cal1 -s $srcs
echo "Completed Cal Copy"
python acf_mns.py -v "*.UV" -s $sourcenames
echo "Completed Merge and Split"
python acf_wimage.py -v $sourcefilenames
echo "Completed!"
