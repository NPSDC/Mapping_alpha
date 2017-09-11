#! /bin/bash

while read -r line
do
	chr=$( echo $line |  cut -d ' ' -f 6 ) 
	chr=$(echo $chr | sed -e 's/v/\./' -e 's/\(_random\|_alt\)//'  -e 's/chr//'  -e 's/^\([[:alnum:]]\+_\)//')
	range_start=$( echo $line |  cut -d ' ' -f 7 ) 	
	range_end=$( echo $line |  cut -d ' ' -f 8 )
#	echo samtools faidx $2 $chr:$range_start-$range_end
#	echo $line
#	echo $(samtools faidx $2 $chr:$range_start-$range_end)
	samtools faidx $2 $chr:$range_start-$range_end >> "alpha.fasta"

done <$1
