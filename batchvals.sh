# Setup the flagging parameters
export flagpar='5,1,1,1,5,3'

# Calibrators
export cals='11400543_S0_T0.UV,11400544_S0_T0.UV,11400546_S0_T0.UV,11400547_S0_T0.UV'
export cal1='11400543_S0_T0.UV' 

# Sources
export srctag=' 11400545_S0_*.UV'
export sourcefilenames='ACF4G2P1.UV,ACF4G2P2.UV,ACF4G2P3.UV,ACF4G2P4.UV'
export sourcenames=`echo $sourcefilenames | sed s/.UV//g`

# First put uvfs=*.UVF, 
export file=''
export uvfs=''
for file in `ls *.UVF`
	do 
		export uvfs=$uvfs,$file 
	done
export uvfs=`echo $uvfs | sed s/^,//g`
export uvs=`echo $uvfs | sed s/.UVF//g`

# Now do the  
export file=''
export srcs=''
for files in `ls $srctag`
	do 
		export srcs=$srcs,$files 
	done
export srcs=`echo $srcs | sed s/^,//g`

