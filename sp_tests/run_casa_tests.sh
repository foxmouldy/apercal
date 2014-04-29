sleep 5
python swatch_family.py --ptype start --cfile casapy_clean_n0.sh --totaltime 10000 --tag casapy_clean.n0
sleep 5
python swatch_family.py --ptype start --cfile casapy_clean_n10.sh --totaltime 10000 --tag casapy_clean.n10
sleep 5
python swatch_family.py --ptype start --cfile casapy_clean_n100.sh --totaltime 10000 --tag casapy_clean.n100
sleep 5
python swatch_family.py --ptype start --cfile casapy_clean_n1000.sh --totaltime 10000 --tag casapy_clean.n1000
sleep 5
python swatch_family.py --ptype start --cfile casapy_clean_n10000.sh --totaltime 10000 --tag casapy_clean.n10000
