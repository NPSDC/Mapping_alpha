import csv
import HTSeq as HT
import itertools
import os
import pickle
import re
import argparse as ag

def get_chrom(chrom):
	return re.sub('\w+_','',re.sub('(_alt|_random|\n?)', '', re.sub('^chr','',re.sub('v', '.', chrom)))) ##Extracting chrom name without chr and other info so that it maps with the SAM/BAM file output


# def get_gen_array_bed(bed_file, rep_families, writePath = None):
# 	ga_family = dict()
# 	for rep_family in rep_families:
# 		ga_family[rep_family] = HT.GenomicArray('auto', typecode = 'b', stranded = False)

# 	with open(bed_file, 'r') as bed:
# 		for line in bed.readlines():
# 			chrom, start, end, name = line.split('\t')

# 			chrom = get_chrom(chrom)
# 			start = int(start)
# 			end = int(end)
			
# 			if(start < end):
# 			    name = name[:-2]
# 			    gi = HT.GenomicInterval(chrom, start, end)
# 			    ga_family[name] = HT.GenomicArray('auto', typecode = 'b', stranded = False)
# 			    ga_family[name][gi] = True
# 	if(not writePath is None):
# 		pickle.dump(ga_family, open(writePath, "wb"))
# 	return(ga_family)

# def get_gen_array(inp_file, rep_families, pos, stranded = False, writePath = None):
# 	'''
# 	This function dumps two objects in the same directory namely gen_array.pickle and valid_chroms.pickle
# 	pos a list with 1st chromosome, 2-3 start and end position, 3 strand, 4 name of family
# 	'''
# 	ga_families = dict() #Dictionary containing genomic array of patterns
# 	for rep_family in rep_families:
# 		ga_families[rep_family] = HT.GenomicArray('auto', typecode = 'b', stranded = stranded)
# 	valid_chroms = list()
# 	with open(inp_file, 'r') as csvfile:
# 		seq = csv.reader(csvfile, delimiter = '\t')
# 		for row in seq:
# 			rep_family = row[pos[3]]
# 			if(rep_family in ga_families.keys()):
# 				chrom = get_chrom(row[pos[0]])
# 				if chrom not in valid_chroms:
# 					valid_chroms.append(chrom)
# 				gi = HT.GenomicInterval(chrom, int(row[pos[1]]), int(row[pos[2]]))
# 				if(stranded):
# 					gi = HT.GenomicInterval(chrom, int(row[pos[1]]), int(row[pos[2]]), int(row[pos[4]]))
# 				ga_families[rep_family][gi] = True

# 	pickle.dump(valid_chroms, open(os.path.join(os.getcwd(), 'valid_chroms.pickle'), "wb"))
# 	if(not writePath is None):
# 		pickle.dump(ga_families, open(writePath, "wb"))
# 	return(ga_families)

def get_gen_array(inp_file, pos_list, stranded = False, writePath = None, write = True):
	'''
	This function dumps two objects in the same directory namely gen_array.pickle and valid_chroms.pickle
	0 for chromosome name, 1,2 for start and end, 3 family, 4 for stranded
	'''
	if(not os.path.exists(inp_file)):
		raise FileNotFoundError
	if(stranded):
		if(len(pos_list) != 5):
			raise Exception("Length of position list for stranded should be 5")
	else:
		if(len(pos_list) != 4):
			raise Exception("Length of position list not stranded should be 4")

	ga_families = dict() #Dictionary containing genomic array of patterns
	valid_chroms = []
	with open(inp_file, 'r') as csvfile:
		seq = csv.reader(csvfile, delimiter = '\t')
		for row in seq:
			rep_family = row[pos_list[3]]
			if(rep_family not in ga_families.keys()):
				ga_families[rep_family] = HT.GenomicArray('auto', typecode = 'b', stranded = stranded)
			
			chrom = get_chrom(row[pos_list[0]])
			if chrom not in valid_chroms:
				valid_chroms.append(chrom)
			gi = HT.GenomicInterval(chrom, int(row[pos_list[1]]), int(row[pos_list[2]]))
			if(stranded):
				gi = HT.GenomicInterval(chrom, int(row[pos_list[1]]), int(row[pos_list[2]]), int(row[pos_list[4]]))
			ga_families[rep_family][gi] = True

	if(writePath is None):
		writePath = os.getcwd()
	if(write):
		pickle.dump(ga_families, open(os.path.join(writePath, "ga_families"), "wb"))
		pickle.dump(valid_chroms, open(os.path.join(writePath, "valid_chroms.pickle"), "wb"))
	return(ga_families)

## Code snippet taken with help of StackOverFlow question
## https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
## Question by https://stackoverflow.com/users/399397/superelectric
## Answer by https://stackoverflow.com/users/805502/maxim
def checkbool(value):
    if isinstance(value, bool):
       return value
    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ag.ArgumentTypeError('Boolean value expected.')

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('-f', type = str, required = True, dest = 'bed_file', help = 'bed file') #input file containing repeat regions and their coordinates
	parser.add_argument('-c', type = int, required = True, dest = 'chrom_pos', help = 'chromosome index')
	parser.add_argument('-b', type = int, required = True, dest = 'start_pos', help = 'start position index')
	parser.add_argument('-e', type = int, required = True, dest = 'end_pos', help = 'end position index')
	parser.add_argument('-r', type = int, required = True, dest = 'repeat', help = 'replication family index')
	parser.add_argument('-s', type = checkbool, required = True, dest = 'stranded', help = 'Stranded')
	parser.add_argument('-v', type = int, dest = 'strand_pos', help = 'type of strand', default = 4)
	args = parser.parse_args()
	pos = [args.chrom_pos - 1, args.start_pos - 1, args.end_pos - 1, args.repeat - 1]
	if(args.stranded):
		pos.append(args.strand_pos)
	ga_families = get_gen_array(args.bed_file, pos, args.stranded)
	#	parser.add_argument('--file', metavar = 'file', required = True, dest = 'inp_file', help = 'input file') #input file containing repeat regions and their coordinates
	# rep_families = ['centr', 'telo', 'acro', 'tRNA', 'rRNA', 'scRNA', 'snRNA', 'srpRNA', 'Helitron', 'Gypsy', 'PiggyBac', 'LTR', 
	# 	'Merlin', 'hAT', 'Low_complexity', 'L2', 'Simple_repeat', 'L1', 'Alu', 'MIR'] 
	# if(not os.path.exists(args.inp_file)):
	# 	raise FileNotFoundError('Invalid Filename or path for sam/bam file')
	# ga_families = get_gen_array(args.inp_file, rep_families)
	# ga_families = get_gen_array_bed(args.bed_file, ga_families)
	# pickle.dump(ga_families, open(os.path.join(os.getcwd(),'ga_fam_dict.pickle'), "wb"))
        

if __name__ == '__main__':
	main()
