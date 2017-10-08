import argparse as ag
import os

def remove_files(dir):
	file = os.path.join(dir, 'files.txt')
	if(not os.path.exists(file)):
		raise FileNotFoundError(file)
	req = ''
	with open(file, 'r') as f:
		for line in f.readlines():
			url = line.split(' ')[1]
			if(url != '\n'):
				req += line
	with open(file, 'w') as f:
		f.write(req)

def loop_dir(output_dir):
	study_accs = os.listdir(output_dir)
	for study_acc in study_accs:
		remove_files(os.path.join(output_dir, study_acc))

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--dir', metavar = 'directory', required = True, dest = 'output_dir', help = 'output directory')
	args = parser.parse_args()
	
	if(not os.path.exists(args.output_dir)):
		raise FileNotFoundError('Invalid Directory')
	loop_dir(args.output_dir)	

if __name__ == '__main__':
	main()