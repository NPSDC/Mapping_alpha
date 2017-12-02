import argparse as ag
import os

def get_file_ids(run_acc_file):
	file_ids = list()
        file_urls = list()
	with open(run_acc_file, 'r') as f:
		for line in f.readlines():
			file_ids.append(line.split(' ')[0].strip())
	with open(run_acc_file, 'r') as f:
		for line in f.readlines():
			file_urls.append(line.split(' ')[1].strip())
	return([file_ids, file_urls])

def get_al_ids(run_acc_file):
	al_ids = list()
	with open(run_acc_file, 'r') as f:
		for line in f.readlines():
			al_ids.append(line.split('\t')[0].split(':')[1].strip())
	return(al_ids)


def add_req_files(acc_track, output_dir):
	for i in xrange(len(acc_track)):
		file_path = os.path.join(output_dir, acc_track[i][0], 'files.txt')
		
		if(not os.path.exists(file_path)):
			raise FileNotFoundError(file_path)
		file_ids = get_file_ids(file_path)[0]
                file_urls = get_file_ids(file_path)[1]

		if(str(len(file_ids)) != acc_track[i][1]):
			raise Exception(file_path + " length not equal")

		if(acc_track[i][2] != 'not there'):
                        al_path = os.path.join(output_dir, acc_track[i][0], 'alignment.txt') 
			if(not os.path.exists(al_path)):
				raise FileNotFoundError(al_path)
			al_ids = get_al_ids(al_path)
			
                        if(str(len(al_ids)) != acc_track[i][2]):
			        raise Exception(al_path + " length not equal")
                        if(len(al_ids) == 0):
                                continue                
			
			missing_ids = list(set(file_ids) - set(al_ids))
                        missing_urls = []
                        for j in missing_ids:
                            missing_urls.append(file_urls[file_ids.index(j)])
                        missing_req = [m_id + " " + m_url for m_id, m_url in zip(missing_ids, missing_urls)]
                        missing_req = '\n'.join(missing_req)
			with open(os.path.join(output_dir, acc_track[i][0], 'rem_files.txt'), 'w') as f :
				f.write(missing_req)


def find_accs(res_file):
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
	parser.add_argument('--output_dir', metavar = 'output_dir', required = True, dest = 'output_dir', help = 'path containing the output directory')
	parser.add_argument('--save_dir', metavar = 'save_dir', required = True, dest = 'save_dir', help = 'path of the directory where missing accs to be saved')
	args = parser.parse_args()
	
	if(not os.path.exists(args.res_file)):
		raise FileNotFoundError(args.res_file)
        if(not os.path.exists(args.output_dir)):
		raise FileNotFoundError(args.output_dir)
        if(not os.path.exists(args.save_dir)):
		raise FileNotFoundError(args.save_dir)

	accs = find_accs(args.res_file)
        missing_accs = [p[0] for p in accs]
        missing_accs = '\n'.join(missing_accs)
        with open(os.path.join(args.save_dir,'missing_files.txt'), 'w') as f:
            f.write(missing_accs)
        add_req_files(accs, args.output_dir)
if __name__ == '__main__':
	main()
