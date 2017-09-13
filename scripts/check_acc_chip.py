def check_study_acc(file_name):
	'''Checks whether all the accession ids are in consecutive order and not spread randomly'''
	with open(file_name, 'r') as f:
		lines = f.readlines()
	i = 0
	acc_num = dict() 
	for line in lines:
		req_ids = line.split('\t')
		if req_ids[0] not in acc_num.keys():
			acc_num[req_ids[0]] = i
		else:
			if(acc_num[req_ids[0]] != i-1):
				print(req_ids[0])
				return -1
			acc_num[req_ids[0]] = i
		i += 1
	return 1

		
def main():
	file_name = '../single.txt'
	if(check_study_acc(file_name) == 1):
		print('correct')
	else:
		print('not correct')
	

if __name__ == '__main__':
	main()