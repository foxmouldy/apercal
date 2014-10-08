#!/bin/bash
# Bradley Frank, ASTRON, NL 2014
export vis='ACF2G1P1.UV'

#Splitting up the UV file into SPWs
cp apercal/acf_selfcal.py .
cp apercal/acf_pgflagger.py . 

for i in `seq 1 8`
	do 
		echo $i uvcat
		uvcat vis=$vis select=window\($i\) stokes=ii options=unflagged out=w$i.uv
	done

for file in `ls -d *.uv`
	do 
		echo $file Flagging 
		python acf_pgflagger.py --stokes ii --flagpar 3,5,5,3,5,3 --vis $file 
	done

for i in `seq 1 8`
	do 
		echo $i
		python acf_selfcal.py -v w$i.uv --select "-uvrange(0,1.0)" -m pselfcalr
		python acf_selfcal.py -v w$i.uv --select "-uvrange(0,1.0)" -m aselfcalr
		python acf_selfcal.py -v w$i.uv --select "-uvrange(0,1.0)" -m pselfcalr
	done
