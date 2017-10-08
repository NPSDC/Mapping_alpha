#! /bin/bash

###Download the respective files under files.txt for each study accession
#1st input contains the directory of the study accession
#2nd contains the directory of human ref genome
#3rd directory containing Pickle
#4th reader.py path
study_directory=$1

if [ ! -d $study_directory ]
	then
		echo "Enter Valid directory"
		exit
fi

if [ ! -d $2 ]
	then
		echo "Enter valid index location"
		exit
fi

file_ids="$study_directory/files.txt"
count=0
#echo "$study_directory"
export PATH=$PATH:/mnt/Data/Anders_group/Noor/bowtie2-2.3.2
while read -r line
do
    file_acc=$(echo "$line" | cut -d ' ' -f 1)
#    echo "File accession $file_acc"
    url=$(echo "$line" | cut -d ' '  -f 2)
#    echo "URL $url"
    bam_file="$study_directory/$file_acc.bam"
#    echo "$study_directory/$file_acc.fastq.gz"
#    echo "Bam File $bam_file"
    wget -q --spider $url
    if [ $? -eq 0 ]
	then
	    wget -O "$study_directory/$file_acc.fastq.gz" $url & $PIDWGET=$!
	    sleep 15
	    bowtie2  -p 18 -x "$2/GRCh38" -U  "$study_directory/$file_acc.fastq.gz" | samtools view -bS - > $bam_file & $PIDBOW=$!
	    wait $PIDWGET
	    wait $PIDBOW
    	    python $4 --file $bam_file --p_alr_align "$3/gen_array.pickle" --p_valid_chrom "$3/valid_chroms.pickle" --dest_file "$study_directory/alignment.txt"
	    rm -r $bam_file "$study_directory/$file_acc.fastq.gz"
    else
    echo "$study_directory/alignment.txt" >> $file_acc "fastq file cant be downloaded with url $url" 
    fi
#    count=$(($count+1))
done < $file_ids
