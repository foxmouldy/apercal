sleep 5
python swatch_family.py --ptype start --cfile invert.sh --totaltime 10000 --tag restor 
sleep 5
python swatch_family.py --ptype start --cfile clean_n10.sh --totaltime 10000 --tag miriad_clean.n10
sleep 5
python swatch_family.py --ptype start --cfile restor_n10.sh --totaltime 10000 --tag miriad_restor.n10
sleep 5
python swatch_family.py --ptype start --cfile clean_n100.sh --totaltime 10000 --tag miriad_clean.n100
sleep 5
python swatch_family.py --ptype start --cfile restor_n100.sh --totaltime 10000 --tag miriad_restor.n100
sleep 5
python swatch_family.py --ptype start --cfile clean_n1000.sh --totaltime 10000 --tag miriad_clean.n1000
sleep 5
python swatch_family.py --ptype start --cfile restor_n1000.sh --totaltime 10000 --tag miriad_restor.n1000
sleep 5
python swatch_family.py --ptype start --cfile clean_n10000.sh --totaltime 10000 --tag miriad_clean.n10000
sleep 5
python swatch_family.py --ptype start --cfile restor_n10000.sh --totaltime 10000 --tag miriad_restor.n10000
