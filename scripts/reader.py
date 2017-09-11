import csv
import HTSeq as HT
import itertools
import os
import pickle
import re
import argparse as ag
import time

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
	

def get_counts(inp_file, genomic_array, valid_chroms):
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
	counts = 0
	start_time = time.clock()
	for bundle in HT.bundle_multiple_alignments(reader_file):
		for g in bundle: 
			if(g is not None and g.aligned):
				iv = g.iv
				if(check_read(iv, genomic_array, valid_chroms)):
					counts += 1
					break
		total_reads += 1
		if(total_reads%1e4 == 0):
			print("Finished counting "+ str(int(total_reads/1e4)) )
			print("So far " + str(float(counts)/total_reads * 100) + " Aligned")
	print(time.clock() - start_time)
	print(counts)
	print(total_reads)
	return [counts, total_reads]
		

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
	print(file_write)
	
	genomic_array = pickle.load(open(args.pickle_alpha, "rb"))
	valid_chroms = pickle.load(open(args.pickle_chrom, "rb"))
	count_reads = get_counts(file_work, genomic_array, valid_chroms)
	
		
	with open(file_write, 'w') as writ:
		writ.write("Reads aligned to bam file : " + str(count_reads[0])+"\n"
			   "Total Reads : " + str(count_reads[1]) + "\n")

	print("Finished counting")	
	
	
if __name__ == '__main__':
	main()
