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
export tag='ACF2G3'
export cals='11400713_S0_T0.UV,11400714_S0_T0.UV,11400716_S0_T0.UV,11400717_S0_T0.UV'
export cal1='11400713_S0_T0.UV'

# Sources
export srctag='11400715_S0_*.UVF'
export sourcefilenames='ACF2G3P1.UV,ACF2G3P2.UV,ACF2G3P3.UV,ACF2G3P4.UV'
export sourcenames=`echo $sourcefilenames | sed s/.UV//g`
export lm='ACFG3*.IM,ACFG3.IM'

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
