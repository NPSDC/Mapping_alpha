#!/bin/bash
if [ -z $1 ]
	then
		echo "Please enter input file name"
		exit
fi

if [ -z $2 ]
	then
		echo "Please enter output directory"
		exit
fi

if [ ! -f $1 ]
	then
		echo "Enter valid filename"
		exit
fi

if [ ! -d $2 ]
	then
		mkdir $2
fi

while read -r line
do
    study_acc=$(echo "$line" | cut -f 1)
    file_acc=$(echo "$line" | cut -f 2)
    ftp_down=$(echo "$line" | cut -f 3)
    dir1="$2/$study_acc"
    if [ ! -d $dir1 ]
    	then
    		mkdir $dir1
    fi
    echo "$file_acc $ftp_down" >> "$dir1/files.txt"
done < "$1"