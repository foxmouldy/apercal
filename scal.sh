export pointing='ACF2G2P2'

for i in `seq 1 8`
	do 
		echo Flagging $pointing'_window'$i'.uv'
		python acf_pgflagger.py -v $pointing'_window'$i'.uv' --flagpar 4,5,10,3,1,3
	done

for i in `seq 1 8` 
	do 
		echo Selfcal on $pointing'_window'$i'.uv'
		python selfcal.py -v $pointing'_window'$i'.uv'
	done
