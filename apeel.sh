#!/bin/bash
echo GPCOPY
gpcopy vis=p.uv out=src.uv_bgsc
echo UVCAT
uvcat vis=src.uv_bgsc out=s.uv
echo UVMODEL
uvmodel vis=s.uv options=mfs,subtract model=pmod
echo GPCOPY
gpcopy vis=p.uv out=s.uv
echo GPEDIT
./agpedit vis=s.uv options=invert
echo UVCAT
uvcat vis=s.uv out=s2.uv
echo STUFF
rm -r s.uv
mv s2.uv s.uv
echo UVLIN
uvlin vis=s.uv chans=10,200,250,400,650,900 order=5 out=sl.uv
echo INVERT
invert vis=sl.uv map=sl.uv.map beam=sl.uv.beam imsize=1250 cell=4 robust=0.4 line=channel,50,400,1,1 stokes=ii options=double slop=0.2
