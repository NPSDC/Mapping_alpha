import argparse as ag
import os
import subprocess
import time
from joblib import Parallel, delayed
import csv
import pickle
from align_study_acc import *
from reader import *

def run_proc(line, inp_file, acc_dir, ind_files, ga_fam_dict, valid_chroms, paired, break_count, req_fields):
	study_acc = line.strip()
	study_path=os.path.join(acc_dir,study_acc)
	if(os.path.exists(study_path)):
		with open(os.path.join(study_path, 'alignment.csv'), 'w') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=req_fields)
			writer.writeheader()
		try:
			align_study(study_path, ind_files, ga_fam_dict, valid_chroms, paired, break_count)
		except:
			with open('er_cum', 'a') as f:
				f.write("Error in processing " + study_acc + "\n")
	else:
		print(study_path + " not found")

def set_loop(inp_file, acc_dir, ind_files, ga_fam_dict, valid_chroms, paired, break_count = 1e5):
    families = ga_fam_dict.keys()
    req_fields = ['Accession Id', 'Met Criteria'] + families + ['Total Counts']
    start = time.time()
    with open(inp_file, 'r') as f:
                Parallel(n_jobs=10)(delayed(run_proc)(line=line, inp_file = inp_file, acc_dir = acc_dir, ind_files = ind_files, ga_fam_dict = ga_fam_dict, valid_chroms = valid_chroms, paired = paired, break_count = break_count, req_fields=req_fields) for line in f.readlines())
    print time.time() - start

def main():
    parser = ag.ArgumentParser(description = "file parser")
    parser.add_argument('--inp_file', metavar = 'acc', required = True, dest = 'inp_file', help = 'inp_file')
    parser.add_argument('--acc_dir', metavar = 'acc', required = True, dest = 'acc_dir', help = 'acc_dir')
    parser.add_argument('--ind_files', metavar = 'ind_files', required = True, dest = 'ind_files', help = 'Index Files')
    parser.add_argument('--p_fam_align', metavar = 'file', required = True, dest = 'ga_fam_pickle', help = 'Alignment for families of regions')
    parser.add_argument('--p_valid_chrom', metavar = 'file', required = True, dest = 'chrom_pickle', help = 'All chromosomes extracted from repeat sequence file')
    parser.add_argument('--paired', metavar = 'paired', required = True, dest = 'paired', help = 'single or paired end')
    parser.add_argument('--break_count', metavar = 'count', dest = 'break_count', default = 1e5, type = float, help = 'Maximum reads to be considered')
    args = parser.parse_args()

    os.environ['PATH'] += ':/mnt/Data/Anders_group/Noor/sratoolkit.2.8.2-1-ubuntu64/bin'        
    os.environ['PATH'] += ':/mnt/Data/Anders_group/Noor/bowtie2-2.3.2'
	
    check_input(args.inp_file, 'Invalid filename')	
    check_input(args.acc_dir, 'Invalid directory of study acc')
    check_input(args.ind_files, 'Invalid directory of index files')
    check_input(args.ga_fam_pickle, 'Invalid Filename or path for genomic array family object')
    check_input(args.chrom_pickle, 'Invalid Filename or path for valid chromosomes object')

    ga_fam_dict = pickle.load(open(args.ga_fam_pickle, "rb"))
    valid_chroms = pickle.load(open(args.chrom_pickle, "rb"))
    
    args.paired = ast.literal_eval(args.paired)

    set_loop(args.inp_file, args.acc_dir, args.ind_files, ga_fam_dict, valid_chroms, args.paired, args.break_count)

if __name__ == '__main__':
	main()
