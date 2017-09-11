#! /bin/bash
if [ -z $1 ]
	then	
		echo "Please enter the filename"
		exit
fi
if [ -a $1 ]
	then
		output_file=$(echo "$1" | cut -d"." -f1)
		counts=$(samtools view $1 | cut -f 3 | grep -v \* | wc -l)
		total_counts = 	$(samtools view $1 | wc -l)
		#echo $counts
		echo $counts $total_counts>$output_file"_count.txt"
else
	echo Enter Valid Filename
fi

