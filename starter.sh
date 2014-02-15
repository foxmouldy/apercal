#!/usr/bin/bash
python kal.py -s src.uv -c calcals
python kal.py -s src.uv -c cal2srcs
uvlin vis=src.uv chans=10,200,250,400,650,900 out=src.uv_chan0 order=5 mode=chan0
python kal.py -s src.uv_chan0 -c clean,sc,clean
