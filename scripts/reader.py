import csv
import HTSeq as HT
import itertools
import os
import cPickle as pickle
import re
import argparse as ag
import time
import csv
import collections
import numpy as np
#sed -e 's/v/\./' -e 's/\(_random\|_alt\)//'  -e 's/chr//'  -e 's/^\([[:alnum:]]\+_\)//' a


def check_read(read_int, genomic_array, valid_chroms):
#	if read_int.chrom in valid_chroms:
#		import code; code.interact( local=locals() )
		try:
#		if read_int.chrom in genomic_array.chrom_vectors.keys():
			return any(val for gi, val in genomic_array[read_int].steps())
		except KeyError as key:
			pass
#	else:
#		print('Not Valid Chromosome '+read_int.chrom)
	

def get_counts(inp_file, ga_fam_dict, valid_chroms, break_count):
	ext = inp_file.split('.')[-1]
	reader_file = ''
	if(ext == 'bam'):
#		print('bam')
#		global reader_file
		reader_file = HT.BAM_Reader(inp_file)
	elif(ext == 'sam'):
#		global reader_file
		reader_file = HT.SAM_Reader(inp_file)
	else:
		print('wrong input')
	total_reads = 0
	count_fams = collections.Counter(ga_fam_dict.keys())
	break_flags = collections.Counter(ga_fam_dict.keys())
	for fam in count_fams.keys():
		count_fams[fam] = 0
	start_time = time.clock()
	for bundle in HT.bundle_multiple_alignments(reader_file):
		for fam in break_flags.keys():
			break_flags[fam] = 0
		for g in bundle: 
			if(g is not None and g.aligned):
				iv = g.iv
				for fam in count_fams.keys():
					if(break_flags[fam] == 1):
						continue
					if(check_read(iv, ga_fam_dict[fam], valid_chroms)):
						count_fams[fam] += 1
						break_flags[fam] = 1
			if(sum(np.array(break_flags.values()) == 1) == len(break_flags.keys())):
				print('yes')
				break
		total_reads += 1

		if(total_reads == break_count):
			break

	for key in count_fams.keys():
		count_fams[key]=count_fams[key]/float(total_reads)*100
#	print('\t\t##### '+ str(count_fams))
#	print('\t\t#####'+ str(total_reads))
	return [count_fams, total_reads]
		
def check_input(file, message):
	if(not os.path.exists(file)):
		raise FileNotFoundError(message)

def count_and_write(align_file, dest_file, ga_fam_dict, valid_chroms, break_count = 1e5):
	check_input(align_file, 'Invalid Filename or path for sam/bam file')
	check_input(dest_file, 'Invalid destination file')
	count_reads = get_counts(align_file, ga_fam_dict, valid_chroms, break_count)
	acc = align_file.split('.')[0].split('/')[-1]
	
	##Extract the fieldnames from the file making sure order of writing is same
	fieldnames = []
	with open(dest_file, 'r') as read_file:
		read_csv = csv.DictReader(read_file)
		fieldnames = read_csv.fieldnames
	
	count_reads[0]['Accession Id'] = acc
	count_reads[0]['Met Criteria'] = 'Yes'
	count_reads[0]['Total Counts'] = count_reads[1]
	with open(dest_file, 'a') as csvfile:
		print(fieldnames)
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		if(count_reads[1] < break_count):
			count_reads[0]['Met Criteria'] = 'No'
		print(count_reads[0])
		writer.writerow(count_reads[0])			

	print("\t\t##### Finished counting\n")

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--align_file', metavar = 'file', required = True, dest = 'align_file', help = 'input file to be aligned')
	parser.add_argument('--p_fam_align', metavar = 'file', required = True, dest = 'ga_fam_pickle', help = 'Alignment for families of regions')
	parser.add_argument('--p_valid_chrom', metavar = 'file', required = True, dest = 'chrom_pickle', help = 'All chromosomes extracted from repeat sequence file')
	parser.add_argument('--dest_file', metavar = 'file', required = True, dest = 'dest_file', help = 'File where output has to be saved')
	parser.add_argument('--break_count', metavar = 'count', dest = 'break_count', help = 'Maximum reads to be considered')
	args = parser.parse_args()

	check_input(args.ga_fam_pickle, 'Invalid Filename or path for genomic array family object')
	check_input(args.chrom_pickle, 'Invalid Filename or path for valid chromosomes object')

	ga_fam_dict = pickle.load(open(args.ga_fam_pickle, "rb"))
	valid_chroms = pickle.load(open(args.chrom_pickle, "rb"))

	count_and_write(args.align_file, args.dest_file, ga_fam_dict, valid_chroms)
	
	
if __name__ == '__main__':
	main()
