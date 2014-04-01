# Setup the flagging parameters
export refant=2
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
export tag='ACF4G4'
export cals='11400797_S0_T0.UV,11400798_S0_T0.UV,11400800_S0_T0.UV,11400801_S0_T0.UV'
export cal1='11400797_S0_T0.UV'

# Sources
export srctag='11400799_S0_*.UVF'
export sourcefilenames='ACF4G4P1.UV,ACF4G4P2.UV,ACF4G4P3.UV,ACF4G4P4.UV'
export sourcenames=`echo $sourcefilenames | sed s/.UV//g`
export lm='ACF4G4*.IM,ACF4G4.IM'

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
