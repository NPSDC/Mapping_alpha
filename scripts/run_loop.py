import argparse as ag
import os
import subprocess
import time
from joblib import Parallel, delayed

def run_proc(line, args):
			study_acc = line.strip()
			study_path=os.path.join(args.acc_dir,study_acc)
			if(os.path.exists(study_path)):
				subprocess.call(['python',  args.align_py, '--study_acc', study_path, '--ind_files', args.ind_files,
				'--Pi', args.pi_dir, '--reader_path', args.read_path], stderr = open('er_cum', 'a'))
			else:
				print(study_path + " not found")

def set_loop(args):
    os.environ['PATH'] += ':/mnt/Data/Anders_group/Noor/sratoolkit.2.8.2-1-ubuntu64/bin'
    os.environ['PATH'] += ':/mnt/Data/Anders_group/Noor/bowtie2-2.3.2'
    start = time.time()
    with open(args.inp_file, 'r') as f:
                Parallel(n_jobs=16)(delayed(run_proc)(line=line, args=args) for line in f.readlines())
    print time.time() - start

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--inp_file', metavar = 'acc', required = True, dest = 'inp_file', help = 'inp_file')
	parser.add_argument('--align_py', metavar = 'al', required= True, dest = 'align_py', help = 'align_py')
	parser.add_argument('--acc_dir', metavar = 'acc', required = True, dest = 'acc_dir', help = 'acc_dir')
	parser.add_argument('--ind_files', metavar = 'ind_files', required = True, dest = 'ind_files', help = 'Index Files')
	parser.add_argument('--Pi', metavar = 'pi', required = True, dest = 'pi_dir', help = 'Directory containing pickled files')
	parser.add_argument('--reader_path', metavar = 'reader_path', required = True, dest = 'read_path', help = 'Reader.py path')
	args = parser.parse_args()
	
	if(not os.path.exists(args.inp_file)):
		raise FileNotFoundError('Invalid filename')
	if(not os.path.exists(args.align_py)):
		raise FileNotFoundError('Invalid align_py')	
	if(not os.path.exists(args.acc_dir)):
		raise FileNotFoundError('Invalid directory of study acc')
	if(not os.path.exists(args.ind_files)):
		raise FileNotFoundError('Invalid directory of index files')
	if(not os.path.exists(args.pi_dir)):
		raise FileNotFoundError('Invalid directory of pickled files')
	if(not os.path.exists(args.read_path)):
		raise FileNotFoundError('Invalid path for reader.py')
    
	set_loop(args)

if __name__ == '__main__':
	main()