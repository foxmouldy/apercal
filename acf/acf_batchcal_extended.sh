#!/usr/bin/env bash
#. ./acf_batchvals.sh
# Convert the MSs to UVFs
#for msname in `ls -d *.MS`
#	do
#		export uvname=`echo $msname | sed s/.MS/.UVF/g`
#		ms2uvfits ms=$msname fitsfile=$uvname writesyscal=T multisource=T combinespw=T
#	done
. ./acf_batchvals.sh
#echo "MSs -> UVF completed"
time python acf_inical.py -v $uvfs -f $flags 
echo "Completed Inical"
# The following value should probably be moved to acf_batchvals.sh
# also not sure whether to time the python command or not...
windows=8
for vis_fits in `ls ${srctag}`
	do
		vis=`echo ${vis_fits} | sed s/.UVF/.UV/`
		for i in `seq 1 ${windows}`
			do
				echo $i
				python acf_spflag.py -v $vis -s "window($i)" -l 2,4
			done
	done
echo "Completed edge channels clipping"
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
echo "Completed Mosaic!"
echo
echo "Now doing some extra steps (previously done manually), such as selfcal..."
pointings='ACF*G*P*'
number_pointings=4
new_flagpars='4,3,3,10,6,3'
polynom_order=4
uvlin_mode=chan0
for i in `seq 1 ${number_pointings}`
	do
		pointing=ACF2G2P${i}
		vis=${pointing}.UV
		directory_name=`echo ${pointing} | tr '[:upper:]' '[:lower:]'`
		mkdir ${directory_name}
		working_directory=`pwd`
		#this is necessary to get a correct symbolic link
		ln -s ${working_directory}/${vis} ${directory_name}
		cd ${directory_name}
		for window in `seq 1 ${windows}`
			do
			cp ../acf_selfcal.py .
				uvlin vis=${vis} select="window(${window})" out="w${window}_${uvlin_mode}.uv" order=${polynom_order} mode=${uvlin_mode}
				python acf_selfcal.py -v w${window}_${uvlin_mode}.uv
			done
			rm -r w.*
			invert vis=w*_chan0.uv map=w.map beam=w.beam imsize=1250 cell=4 robust=-2 stokes=ii options=double,mfs slop=0.5
			clean map=w.map beam=w.beam out=w.model niters=1000
			restor model=w.model beam=w.beam map=w.map out=w.image
			maths exp=w.image mask=w.image.gt.1e-3 out=w.mask
			rm -r w.model
			rm -r w.image
			clean map=w.map beam=w.beam out=w.model niters=1000000 cutoff=3e-4 region="mask(w.mask)"
			restor model=w.model beam=w.beam map=w.map out=w.image
		cd ..
	done
