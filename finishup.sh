#!/usr/bin/bash
uvcat vis=src.uv out=src.uv_bg
gpcopy vis=src.uv_chan0 out=src.uv_bg
uvcat vis=src.uv_bg out=src.uv_bgs
uvcat vis=src.uv_chan0 out=src.uv_chan0_s
uvlin vis=src.uv_bgs chans=10,200,250,400,650,900 out=src.uv_bgs_line order=5
invert vis=src.uv_bgs_line map=src.uv_bgs_line.map beam=src.uv_bgs_line.beam imsize=1050 cell=4 fwhm=30 robust=0.0 options=double line=channel,100,300,4,4
