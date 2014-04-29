sleep 5
echo MIRIAD Tests>> report.txt
echo >> report.txt
echo invert >> report.txt
( time python swatch_family.py --ptype start --cfile invert.sh --totaltime 10000 --tag restor ) 2>> report.txt 
sleep 5
echo clean_n10 >> report.txt
( time python swatch_family.py --ptype start --cfile clean_n10.sh --totaltime 10000 --tag miriad_clean.n10 ) 2>> report.txt
sleep 5
echo restor_n10 >> report.txt
( time python swatch_family.py --ptype start --cfile restor_n10.sh --totaltime 10000 --tag miriad_restor.n10 ) 2>> report.txt
sleep 5
echo clean_n100 >> report.txt
( time python swatch_family.py --ptype start --cfile clean_n100.sh --totaltime 10000 --tag miriad_clean.n100 ) 2>> report.txt
sleep 5
echo restor_n100 >> report.txt
( time python swatch_family.py --ptype start --cfile restor_n100.sh --totaltime 10000 --tag miriad_restor.n100 ) 2>> report.txt
sleep 5
echo clean_n1000 >> report.txt
( time python swatch_family.py --ptype start --cfile clean_n1000.sh --totaltime 10000 --tag miriad_clean.n1000 ) 2>> report.txt
sleep 5
echo restor_n1000 >> report.txt
( time python swatch_family.py --ptype start --cfile restor_n1000.sh --totaltime 10000 --tag miriad_restor.n1000 ) 2>> report.txt
sleep 5
echo clean_n10000 >> report.txt
( time python swatch_family.py --ptype start --cfile clean_n10000.sh --totaltime 10000 --tag miriad_clean.n10000 ) 2>> report.txt
sleep 5
echo restor_n10000 >> report.txt
( time python swatch_family.py --ptype start --cfile restor_n10000.sh --totaltime 10000 --tag miriad_restor.n10000 ) 2>> report.txt
