import argparse as ag
import os
###Just tester function checking counts

def get_counts_file(file):
	with open(file, 'r') as f:
		return sum(1 for _ in f)

def map_ids(align_file, run_acc_file):
	align_ids = list()
	run_acc_ids = list()
	with open(align_file, 'r') as f:
		for line in f.readlines():
			align_ids.append(line.split('\t')[0].split(':')[1].strip())

	with open(run_acc_file, 'r') as f:
		for line in f.readlines():
			run_acc_ids.append(line.split(' ')[0].strip())
        return(len(list(set(align_ids) & set(run_acc_ids))))

def get_study_acc_counts(study_acc):
	run_acc_file = os.path.join(study_acc, 'files.txt')
	align_file = os.path.join(study_acc, 'alignment.txt')
	file_count = 'not there'
	align_count = 'not there'
        mapped = 'not there'
        req_acc = study_acc.split('/')[-1].strip()
	if(os.path.exists(run_acc_file)):
		file_count = get_counts_file(run_acc_file)
        	if(os.path.exists(align_file)):
                    align_count = get_counts_file(align_file)
                    mapped = map_ids(align_file, run_acc_file)
	print('Study Ids : ' + req_acc + "\t" + 'File Ids : ' + str(file_count)+ "\t" + 'Align Ids : ' + str(align_count) + "\t" + 'Mapped : ' + str(mapped))

def loop_files(file_path, acc_path):
        with open(file_path) as f:
                for filename in f.readlines():
                        get_study_acc_counts(os.path.join(acc_path, filename.split()[0]))

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--dir', metavar = 'directory', required = True, dest = 'study_acc', help = 'path accession')
	parser.add_argument('--file', metavar = 'acc_files', required = True, dest = 'file_acc', help = 'Text file with accessions')
	args = parser.parse_args()
	
	if(not os.path.exists(args.study_acc)):
		raise FileNotFoundError('Invalid Directory')
	if(not os.path.exists(args.file_acc)):
		raise FileNotFoundError('Invalid file path')
        loop_files(args.file_acc, args.study_acc)

if __name__ == '__main__':
	main()
