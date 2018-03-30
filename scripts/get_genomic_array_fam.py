import csv
import HTSeq as HT
import itertools
import os
import pickle
import re
import argparse as ag

def get_chrom(chrom):
	return re.sub('\w+_','',re.sub('(_alt|_random|\n?)', '', re.sub('^chr','',re.sub('v', '.', chrom)))) ##Extracting chrom name without chr and other info so that it maps with the SAM/BAM file output


def get_gen_array_bed(bed_file, ga_family):
	j=0
	with open(bed_file, 'r') as bed:
		for line in bed.readlines():
			chrom, start, end, name = line.split('\t')
			chrom = get_chrom(chrom)
			start = int(start)
			end = int(end)
			j = j + 1
			if(start > end):
				print(j)
			name = name[:-2]
			# gi = HT.GenomicInterval(chrom, start, end)
			# ga_family[name] = HT.GenomicArray('auto', typecode = 'b', stranded = False)
			# ga_family[name][gi] = True
	return(ga_family)

def get_gen_array(inp_file, rep_families):
	'''
	This function dumps two objects in the same directory namely gen_array.pickle and valid_chroms.pickle
	'''
	ga_families = dict() #Dictionary containing genomic array of patterns
	for rep_family in rep_families:
		ga_families[rep_family] = HT.GenomicArray('auto', typecode = 'b', stranded = False)
	valid_chroms = list()
	with open(inp_file, 'r') as csvfile:
		seq = csv.reader(csvfile, delimiter = '\t')
		for row in seq:
			rep_family = row[12]
			if(rep_family in ga_families.keys()):
				chrom = get_chrom(row[5])
				if chrom not in valid_chroms:
					valid_chroms.append(chrom)
				gi = HT.GenomicInterval(chrom, int(row[6]), int(row[7]), row[9])
				ga_families[rep_family][gi] = True

	pickle.dump(ga_families, open(os.path.join(os.getcwd(),'ga_fam_dict.pickle'), "wb"))
	pickle.dump(valid_chroms, open(os.path.join(os.getcwd(), 'valid_chroms.pickle'), "wb"))


def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--file', metavar = 'file', required = True, dest = 'inp_file', help = 'input file') #input file containing repeat regions and their coordinates
	args = parser.parse_args()
	rep_families = ['centr', 'telo', 'acro', 'tRNA', 'rRNA', 'scRNA', 'snRNA', 'srpRNA', 'Helitron', 'Gypsy', 'PiggyBac', 'LTR', 
		'Merlin', 'hAT', 'Low_complexity', 'L2', 'Simple_repeat', 'L1', 'Alu', 'MIR'] 
	if(not os.path.exists(args.inp_file)):
		raise FileNotFoundError('Invalid Filename or path for sam/bam file')
	get_gen_array(args.inp_file, rep_families)

if __name__ == '__main__':
	main()
