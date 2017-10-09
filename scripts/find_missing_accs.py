import argparse as ag
import os

def get_file_ids(run_acc_file):
	file_ids = list()
	with open(run_acc_file, 'r') as f:
		for line in f.readlines():
			run_acc_ids.append(line.split(' ')[0].strip())
	return(file_ids)

def get_al_ids(run_acc_file):
	al_ids = list()
	with open(run_acc_file, 'r') as f:
		for line in f.readlines():
			al_ids.append(line.split('\t')[0].split(':')[1].strip())
	return(al_ids)


def add_req_files(acc_track, acc_missing_files, output_dir):
	acc_ids = acc_missing_files.keys()
	for i in xrange(len(acc_ids)):
		file_path = os.path.join(output_dir, acc_track[i][0], 'files.txt')
		
		if(not os.path.exists(file_path)):
			raise FileNotFoundError(file_path)
		file_ids = get_file_ids(file_path)
		
		if(len(file_ids) != int(acc_track[i][0])):
			raise LengthNotEqualError(file_path)
		
		if(acc_track[i][2] != 'not there'):
			al_path = os.path.join(output_dir, acc_track[i][0], 'alignment.txt')
			
			if(not os.path.exists(al_path)):
				raise FileNotFoundError(al_path)
			al_ids = get_al_ids(al_path)

			if(len(al_ids) != int(acc_track[i][2])):
				raise LengthNotEqualError(al_path)
			
			missing_ids = list(set(file_ids) - set(al_ids))
			missing_ids = '\n'	.join(missing_ids)
			with open(os.path.join(output_dir, acc_track[i][0], 'rem_files.txt'), 'w') as f :
				f.write(missing_ids)


def find_accs(res_file, output_dir = None):
	def get_content(p):
		return (p.split(':')[-1].strip())
	acc_track = []
	with open(res_file) as f:
		for line in f.readlines():
			split_content = line.split('\t')
			req = map(get_content, split_content)
			if(req[1] != req[3]):
				acc_track.append([req[0], req[1], req[2]])
	return acc_track

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--file', metavar = 'res_file', required = True, dest = 'res_file', help = 'file containing the results')
	args = parser.parse_args()
	
	if(not os.path.exists(args.res_file)):
		raise FileNotFoundError(args.res_file)

	print(len(find_accs(args.res_file)))
if __name__ == '__main__':
	main()