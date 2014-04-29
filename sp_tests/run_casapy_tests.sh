sleep 5
echo CASAPY Tests >> report.txt
echo >> report.txt
echo casapy_clean_n0 >> report.txt
( time python swatch_family.py --ptype start --cfile casapy_clean_n0.sh --totaltime 10000 --tag casapy_clean.n0 ) 2>> report.txt
sleep 5
echo casapy_clean_n10 >> report.txt
( time python swatch_family.py --ptype start --cfile casapy_clean_n10.sh --totaltime 10000 --tag casapy_clean.n10 ) 2>> report.txt
sleep 5
echo casapy_clean_n100 >> report.txt
( time python swatch_family.py --ptype start --cfile casapy_clean_n100.sh --totaltime 10000 --tag casapy_clean.n100 ) 2>> report.txt
sleep 5
echo casapy_clean_n1000 >> report.txt
( time python swatch_family.py --ptype start --cfile casapy_clean_n1000.sh --totaltime 10000 --tag casapy_clean.n1000 ) 2>> report.txt
sleep 5
echo casapy_clean_n10000 >> report.txt
( time python swatch_family.py --ptype start --cfile casapy_clean_n10000.sh --totaltime 10000 --tag casapy_clean.n10000 ) 2>> report.xt
