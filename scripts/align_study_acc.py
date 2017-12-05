import os
import argparse as ag
import subprocess

####pythonic implementation of align_study_accession.sh

def align_run(run_sra_id, ind_dir):
        err_sra = subprocess.call(['fastq-dump', '--skip-technical',  '--readids', '--read-filter', 'pass', '--dumpbase', '--split-3', '-N', '10000', '-X', '200000', '--clip', run_sra_id], stderr = open('er', 'w') )
        err_bow = 0
        if(err_sra != 0):
                return([1,0])
        if(not os.path.exists(run_sra_id+'_pass.fastq')):
                return([-1,-1])
        if(err_sra == 0):
                err_bow = subprocess.call(['bowtie2', '-p', '18', '-x', os.path.join(ind_dir, 'GRCh38'), '-U', run_sra_id+'_pass.fastq'], stderr = open('er', 'w'),
                    stdout = open(run_sra_id+'.sam', 'w'))
                if(err_bow != 0):
                        err_bow = 1
                        subprocess.call(['rm', sra_id+'_pass.fastq'])
        return([err_sra, err_bow])        

def align_study(args):
        os.environ['PATH'] += ':/mnt/Data/Anders_group/Noor/sratoolkit.2.8.2-1-ubuntu64/bin'
        os.environ['PATH'] += ':/mnt/Data/Anders_group/Noor/bowtie2-2.3.2'
        print('Started on study accession ' + args.study_acc)
        with open(os.path.join(args.study_acc, 'files.txt'), 'r') as f_study:
                for l in f_study.readlines():
                    sra_id = l.strip()
                    print('\t\t##### ' + sra_id) 
                    err = align_run(sra_id, args.ind_files)
                    align_file = os.path.join(args.study_acc, 'alignment_new.txt')
                    if(err[0] == -1 and err[1] == -1):
                        with open(align_file, 'a') as f_write:
                               f_write.write(sra_id + "_pass.fastq doesn't exist")
                        print('\t\t##### Unsuccessful')
                        continue
                    if(err[0] == 1 or err[1] == 1):
                        #subprocess.call(['cat', 'er'])
                        with open(align_file, 'a') as f_write:
                            with open('er', 'r') as err:
                                f_write.write(sra_id + "\t" + err.readlines()[0])
                        print('\t\t##### Unsuccessful')
#                    elif(err[1] == 1):
#                        with open(align_file, 'a') as f_write:
#                            with open('er', 'r') as err:
#                                f_write.write(sra_id + "\t" +  err.readlines()[0])
                    else:
                        read_align = subprocess.call(['python', args.read_path, '--file', sra_id+'.sam', '--p_alr_align', args.pi_dir+"/gen_array.pickle", "--p_valid_chrom", args.pi_dir+"/valid_chroms.pickle", "--dest_file", align_file], stderr = open('er','w'))
                        if(read_align != 0):
                            with open('er', 'r') as err:
                                f_write.write(sra_id + "\t" +  err.readlines()[0])
                            print('\t\t##### Unsuccessful')
                        subprocess.call(['rm', sra_id+'_pass.fastq', sra_id+'.sam'])
                            
                    subprocess.call(['rm','er'])
#        os.system('ls')

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--study_acc', metavar = 'study_acc', required = True, dest = 'study_acc', help = 'Study Accession')
	parser.add_argument('--ind_files', metavar = 'ind_files', required = True, dest = 'ind_files', help = 'Index Files')
	parser.add_argument('--Pi', metavar = 'pi', required = True, dest = 'pi_dir', help = 'Directory containing pickled files')
	parser.add_argument('--reader_path', metavar = 'reader_path', required = True, dest = 'read_path', help = 'Reader.py path')
	args = parser.parse_args()
	
	if(not os.path.exists(args.study_acc)):
		raise FileNotFoundError('Invalid directory of study acc')
	if(not os.path.exists(args.ind_files)):
		raise FileNotFoundError('Invalid directory of index files')
	if(not os.path.exists(args.pi_dir)):
		raise FileNotFoundError('Invalid directory of pickled files')
	if(not os.path.exists(args.read_path)):
		raise FileNotFoundError('Invalid path for reader.py')
        align_study(args)

if __name__ == '__main__':
	main()
