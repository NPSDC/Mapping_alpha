import os
import argparse as ag
import subprocess

####pythonic implementation of align_study_accession.sh

def align_run(run_sra_id, ind_dir, paired):
        f=open('er_'+run_sra_id,'w')
        err = subprocess.call(['fastq-dump', '--skip-technical',  '--readids', '--read-filter', 'pass', '--dumpbase', '--split-3', '-N', '10000', '-X', '200000', '--clip', run_sra_id], stderr = f )
        f.close()
#        err_bow = 0
        if(err != 0):
                err = 1
                if(not paired):
                    if(os.path.exists(run_sra_id+'_pass.fastq')):
                       subprocess.call(['rm', run_sra_id+'_pass.fastq'])
                else:
                    if(os.path.exists(run_sra_id+'_pass_1.fastq')):
                        subprocess.call(['rm', run_sra_id+'_pass_1.fastq'])
                    if(os.path.exists(run_sra_id+'_pass_2.fastq')):
                        subprocess.call(['rm', run_sra_id+'_pass_2.fastq'])

        else:
                f=open('er_'+run_sra_id,'w')
                s=open(run_sra_id+'.sam', 'w')
                if(not paired):
                    if(not os.path.exists(run_sra_id+'_pass.fastq')):
                        err = 3
                        return(err)
                    err = subprocess.call(['bowtie2', '-p', '18', '-x', os.path.join(ind_dir, 'GRCh38'), '-U', run_sra_id+'_pass.fastq'], stderr = f,
                  stdout = s)

                else:
                    if not (os.path.exists(run_sra_id+'_pass_1.fastq') and os.path.exists(run_sra_id+'_pass_2.fastq')) :
                        err = 3
                        return(err)
                    err = subprocess.call(['bowtie2', '-p', '18', '-x', os.path.join(ind_dir, 'GRCh38'), '-1', run_sra_id+'_pass_1.fastq', '-2',
                 run_sra_id+'_pass_2.fastq'], stderr = f, stdout = s)
                f.close()
                s.close()
                if(err != 0):
                    err = 2
                    if(not paired):
                        subprocess.call(['rm', run_sra_id+'_pass.fastq'])
                    else:
                        subprocess.call(['rm', run_sra_id+'_pass_1.fastq', run_sra_id+'_pass_2.fastq'])
                
        return(err)        

def align_study(args):
        print('Started on study accession ' + args.study_acc)
        align_file = os.path.join(args.study_acc, 'alignment.csv')
        not_downloaded=[]
        with open(os.path.join(args.study_acc, 'files.txt'), 'r') as f_study:
                for l in f_study.readlines():
                    sra_id = l.strip()
                    print('\t\t##### ' + sra_id) 
                    err_flag = align_run(sra_id, args.ind_files, args.paired)
                    if(err_flag == 1):
                        with open(align_file, 'a') as f_write:
                            with open('er_'+sra_id, 'r') as er:
                                m=er.readlines()
                                if(len(m)==0):
                                    m=''
                                else:
                                    m=m[0]
                                f_write.write(sra_id + m + "fastq couldn't be downloaded properly\n")
                        print('\t\t' + sra_id + ' ##### Unsuccessful fastq\n')
                        not_downloaded.append(sra_id)                            
#                        subprocess.call(['rm','er_'+sra_id])
#                        continue
                    elif(err_flag == 2):
                        #subprocess.call(['cat', 'er'])
                        with open(align_file, 'a') as f_write:
                            with open('er_'+sra_id, 'r') as er:
                                f_write.write(sra_id + "\t" + er.readlines()[0] + "\n")
                        print('\t\t' + sra_id + ' ##### Unsuccessful in bowtie\n')
                    elif(err_flag == 3):
                        with open(align_file, 'a') as f_write:
                            f_write.write(sra_id + " fastq poor reads" + "\n")
                        print('\t\t' + sra_id + ' ##### Poor Reads\n')                            

#                    elif(err[1] == 1):
#                        with open(align_file, 'a') as f_write:
#                            with open('er', 'r') as err:
#                                f_write.write(sra_id + "\t" +  err.readlines()[0])
                    else:
                        f=open('er_'+sra_id,'w')
                        read_align = subprocess.call(['python', args.read_path, '--file', sra_id+'.sam', '--p_alr_align', args.pi_dir+"/gen_array.pickle", "--p_valid_chrom", args.pi_dir+"/valid_chroms.pickle", "--dest_file", align_file], stderr = f)
                        f.close()
                        if(read_align != 0):
                            with open(align_file, 'a') as f_write:
                                with open('er_'+sra_id, 'r') as er:
                                    f_write.write(sra_id + "\t" +  er.readlines()[0])
                            print('\t\t' + sra_id + ' ##### Unsuccessful in reader\n')
                        #subprocess.call(['rm', sra_id+'_pass.fastq', sra_id+'.sam'])
                        subprocess.call(['rm', sra_id+'_pass_1.fastq', sra_id+'_pass_2.fastq', sra_id+'.sam'])
                            
                    subprocess.call(['rm','er_'+sra_id])
        if(not_downloaded):
            not_down_file = os.path.join(args.study_acc, 'not_downloaded.txt')
            with open(not_down_file, 'w') as f_not_down:
                for sra in not_downloaded:
                    f_not_down.write("%s\n" % sra)
#        os.system('ls')

def main():
	parser = ag.ArgumentParser(description = "file parser")
	parser.add_argument('--study_acc', metavar = 'study_acc', required = True, dest = 'study_acc', help = 'Study Accession')
	parser.add_argument('--ind_files', metavar = 'ind_files', required = True, dest = 'ind_files', help = 'Index Files')
	parser.add_argument('--Pi', metavar = 'pi', required = True, dest = 'pi_dir', help = 'Directory containing pickled files')
	parser.add_argument('--reader_path', metavar = 'reader_path', required = True, dest = 'read_path', help = 'Reader.py path')
    parser.add_argument('--paired', metavar = 'paired', required = True, dest = 'paired', help = 'single-end or paired end reads')
	args = parser.parse_args()
	os.environ['PATH'] += ':/mnt/Data/Anders_group/Noor/sratoolkit.2.8.2-1-ubuntu64/bin'	    
	os.environ['PATH'] += ':/mnt/Data/Anders_group/Noor/bowtie2-2.3.2'
	
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
