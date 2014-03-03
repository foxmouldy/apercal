source batchvals.sh
python acf_inical.py -v $uvfs
python pgflagger.py -v $uvs --flagpar $flagpar 
python acf_calcals.py -c $cals
python acf_cal2srcs.py -c $cal1 -s $srcs
python acf_mns.py -v "*.UV" -s $sourcenames
python acf_wimage.py -v $sourcefilenames
