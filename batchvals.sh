# Setup the flagging parameters
export flagpar='5,1,1,1,5,3'

# Calibrators
export cals='11400815_S0_T0.UV,11400816_S0_T0.UV,11400818_S0_T0.UV,11400819_S0_T0.UV'
export cal1='111400815_S0_T0.UV' 

# Sources
export srctag='11400817_S0_*.UVF'
export sourcefilenames='ACF2G4P1.UV,ACF2G4P2.UV,ACF2G4P3.UV,ACF2G4P4.UV'
export sourcenames=`echo $sourcefilenames | sed s/.UV//g`

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
