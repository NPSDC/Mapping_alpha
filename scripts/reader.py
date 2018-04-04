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
#		if(total_reads%1e4 == 0):
#			print("Finished counting "+ str(int(total_reads/1e4)) )
#			print("So far " + str(float(counts)/total_reads * 100) + " Aligned")
		if(total_reads == break_count):
			break
	for key in count_fams.keys():
		count_fams[key]=count_fams[key]/float(total_reads)*100
	print('\t\t##### '+ str(count_fams))
	print('\t\t#####'+ str(total_reads))
	return [count_fams, total_reads]
		

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--file', metavar = 'file', required = True, dest = 'inp_file', help = 'input file')
	parser.add_argument('--p_alr_align', metavar = 'file', dest = 'pickle_alpha', help = 'Alignment for alpha satellites', required = True)
	parser.add_argument('--p_valid_chrom', metavar = 'file', dest = 'pickle_chrom', help = 'All chromosomes extracted from repeat sequence file', required = True)
	parser.add_argument('--dest_file', metavar = 'file', dest = 'dest_file', help = 'File where output has to be saved')
	args = parser.parse_args()
	
	if(not os.path.exists(args.inp_file)):
		raise FileNotFoundError('Invalid Filename or path for sam/bam file')
	if(not os.path.exists(args.pickle_alpha)):
		raise FileNotFoundError('Invalid Filename or path for aligned alpha satellite object')
	if(not os.path.exists(args.pickle_chrom)):
		raise FileNotFoundError('Invalid Filename or path for valid chromosomes object')

	file_work = os.path.join(os.getcwd(), args.inp_file)
	file_write = file_work.split('.')[0]+"_count.txt"
	if(args.dest_file):
		file_write = args.dest_file
#	print(file_write)
#	print(args.pickle_alpha)
	break_count = 1e5
	ga_fam_dict = pickle.load(open(args.pickle_alpha, "rb"))
	valid_chroms = pickle.load(open(args.pickle_chrom, "rb"))
	count_reads = get_counts(file_work, ga_fam_dict, valid_chroms, break_count)
	acc = args.inp_file.split('.')[0].split('/')[-1]
#        print(acc)
	# vals = [acc]
	fieldnames = []
	with open(args.dest_file, 'r') as read_file:
		read_csv = csv.DictReader(read_file)
		fieldnames = read_csv.fieldnames
	#vals += [count_reads[0][key] for key in fieldnames]
	# vals.append(break_count)
	# print(vals)
	count_reads[0]['Accession Id'] = acc
	count_reads[0]['Met Criteria'] = 'Yes'
	count_reads[0]['Total Counts'] = count_reads[1]

	with open(file_write, 'a') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		if(count_reads[1] < break_count):
			count_reads[0]['Met Criteria'] = 'No'
		writer.writerow(count_reads[0])			
    	        
	print("\t\t##### Finished counting\n")	
	
	
if __name__ == '__main__':
	main()
