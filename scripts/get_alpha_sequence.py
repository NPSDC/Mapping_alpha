import csv
import HTSeq as HT
import itertools
import os
import pickle
import re
import argparse as ag

def get_alpha_align(inp_file):
	'''
	This function dumps two objects in the same directory namely gen_array.pickle and valid_chroms.pickle
	'''
	ga = HT.GenomicArray('auto', typecode = 'b', stranded = False)
	valid_chroms = list()
	with open(inp_file, 'r') as csvfile:
		seq = csv.reader(csvfile, delimiter = '\t')
		for row in seq:
			chrom = re.sub('\w+_','',re.sub('(_alt|_random|\n?)', '', re.sub('^chr','',re.sub('v', '.', row[5]))))
			if chrom not in valid_chroms:
				valid_chroms.append(chrom)
			if(row[10] == 'ALR/Alpha'):
				gi = HT.GenomicInterval(chrom, int(row[6]), int(row[7]), row[9])
				ga[gi] = True
	pickle.dump(ga, open(os.path.join(os.getcwd(),'gen_array.pickle'), "wb"))
	pickle.dump(valid_chroms, open(os.path.join(os.getcwd(), 'valid_chromes.pickle'), "wb"))

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--file', metavar = 'file', required = True, dest = 'inp_file', help = 'input file')
	args = parser.parse_args()
	
	if(not os.path.exists(args.inp_file)):
		raise FileNotFoundError('Invalid Filename or path for sam/bam file')
	get_alpha_align(args.inp_file)

if __name__ == '__main__':
	main()
