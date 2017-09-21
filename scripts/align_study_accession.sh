#! /bin/bash

###Download the respective files under files.txt for each study accession
#1st input contains the directory of the study accession
#2nd contains the directory of human ref genome
#3rd directory containing Pickle
study_directory=$1

if [ !-d $study_directory ]
	then
		echo "Enter Valid directory"
		exit
fi

if [ !-d $2 ]
	then
		echo "Enter valid index location"
		exit
fi

file_ids="$study_directory/files.txt"

while read -r line
do
    file_acc=$(echo "$line" | cut -f 1)
    echo "File accession $file_acc"
    url=$(echo "$line" | cut -f 2)
    echo "URL $url"
    bam_file="study_directory/$file_acc.bam"
    echo "Bam File $bam_file"
    wget -O "$study_directory/$file_acc.fastq.gz" $url 
    bowtie2  -p 16 -x "$2/GRCh38" -U  "$study_directory/$file_acc.fastq.gz" | samtools view -bS - > $bam_file
#    python reader.py --file $bam_file --p_alr_align "$3/gen_array.pickle" --p_valid_chrom "$3/valid_chroms.pickle" --dest_file "$study_directory/$file_acc/alignment.txt"
done < $file_ids