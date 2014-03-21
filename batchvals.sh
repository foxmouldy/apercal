# Setup the flagging parameters
export flagpar='5,1,1,1,5,3'
export flags='an(6),an(3),an(5),shadow(25),auto'
# Measurement sets
export file=''
export msfiles=''
for file in `ls -d *.MS`
	do 
		export msfiles=$msfiles,$file 
	done
export msfiles=`echo $msfiles | sed s/^,//g`

# Calibrators
export tag='ACF2G8'
export cals='11401523_S0_T0.UV,11401524_S0_T0.UV,11401526_S0_T0.UV,11401527_S0_T0.UV'
export cal1='11401523_S0_T0.UV'

# Sources
export srctag='11401525_S0_*.UVF'
export sourcefilenames='ACF2G8P1.UV,ACF2G8P2.UV,ACF2G8P3.UV,ACF2G8P4.UV'
export sourcenames=`echo $sourcefilenames | sed s/.UV//g`
export lm='ACFG8*.IM,ACFG8.IM'

# First put uvfs=*.UVF, 
export file=''
export uvfs=''
for file in `ls *.UVF`
	do 
		export uvfs=$uvfs,$file 
	done
export uvfs=`echo $uvfs | sed s/^,//g`
export uvs=`echo $uvfs | sed s/.UVF/.UV/g`

# Now do the  
export file=''
export srcs=''
for files in `ls $srctag`
	do 
		export srcs=$srcs,$files 
	done
export srcs=`echo $srcs | sed s/^,//g`
export srcs=`echo $srcs | sed s/.UVF/.UV/g`
