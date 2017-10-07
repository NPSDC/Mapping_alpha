import argparse as ag
import os
###Just tester function checking counts

def get_counts_file(file):
	with open(file) as f:
		return sum(1 for _ in f)

def get_study_acc_counts(study_acc):
	run_acc_file = os.path.join(study_acc, 'files.txt')
	align_file = os.path.join(study_acc, 'alignment.txt')
	file_count = 'not there'
	align_count = 'not there'
	if(os.path.exists(run_acc_file)):
		file_count = get_counts_file(run_acc_file)
	if(os.path.exists(align_file)):
		align_count = get_counts_file(align_file)
	print(study_acc+"\t"+str(file_count)+"\t"+str(align_count)+"\n")

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--dir', metavar = 'directory', required = True, dest = 'study_acc', help = 'study accession')
	args = parser.parse_args()
	
	if(not os.path.exists(args.study_acc)):
		raise FileNotFoundError('Invalid Directory')
	get_study_acc_counts(args.study_acc)

if __name__ == '__main__':
	main()
