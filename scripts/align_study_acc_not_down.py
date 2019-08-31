import os
import argparse as ag
import subprocess
import ast
from reader import *
####pythonic implementation of align_study_accession.sh

def align_run(run_sra_id, ind_dir, paired, break_count):
    f=open('er_'+run_sra_id,'w')
    err = subprocess.call(['fastq-dump', '--skip-technical',  '--readids', '--read-filter', 'pass', '--dumpbase', '--split-3', '-N', '10000', '-X', str(int(break_count*2)), '--clip', run_sra_id], stderr = f )
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
        if(not paired):
            if(not os.path.exists(run_sra_id+'_pass.fastq')):
                err = 3
                return(err)
            s=open(run_sra_id+'.sam', 'w')
            err = subprocess.call(['bowtie2', '-p', '13', '-x', os.path.join(ind_dir, 'GRCh38'), '-U', run_sra_id+'_pass.fastq'], stderr = f,
          stdout = s)

        else:
            if not (os.path.exists(run_sra_id+'_pass_1.fastq') and os.path.exists(run_sra_id+'_pass_2.fastq')) :
                err = 3
                return(err)
            s=open(run_sra_id+'.sam', 'w')
            err = subprocess.call(['bowtie2', '-p', '13', '-x', os.path.join(ind_dir, 'GRCh38'), '-1', run_sra_id+'_pass_1.fastq', '-2',
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

def align_study(study_acc, ind_files, ga_fam_dict, valid_chroms, paired, break_count = 1e5):
    print('Started on study accession ' + study_acc)
    dest_file = os.path.join(study_acc, 'alignment_not_down_init.csv')
    not_downloaded=[]
    if(os.path.exists(os.path.join(study_acc, 'not_downloaded.txt'))):
        with open(os.path.join(study_acc, 'not_downloaded.txt'), 'r') as f_study:
            for l in f_study.readlines():
                sra_id = l.strip()
                print('\t\t##### ' + sra_id) 
                err_flag = align_run(sra_id, ind_files, paired, break_count)
                if(err_flag == 1):
                    with open(dest_file, 'a') as f_write:
                        with open('er_'+sra_id, 'r') as er:
                            m=er.readlines()
                            if(len(m)==0):
                                m=''
                            else:
                                m=m[0]
                            write_csv = csv.writer(f_write)
                            write_csv.writerow([sra_id, 'No', m + "fastq couldn't be downloaded properly"])
                    print('\t\t' + sra_id + ' ##### Unsuccessful fastq\n')
                    not_downloaded.append(sra_id)                            

                elif(err_flag == 2):
                    with open(dest_file, 'a') as f_write:
                        with open('er_'+sra_id, 'r') as er:
                            write_csv = csv.writer(f_write)
                            write_csv.writerow([sra_id, 'No', er.readlines()[0]])
                    print('\t\t' + sra_id + ' ##### Unsuccessful in bowtie\n')
                elif(err_flag == 3):
                    with open(dest_file, 'a') as f_write:
                        write_csv = csv.writer(f_write)
                        write_csv.writerow([sra_id, 'No', 'Poor fastq reads or alternate of given paired argument'])
                    print('\t\t' + sra_id + ' ##### Poor Reads or alternate of given paired argument\n')

                else:
                    try:
                        count_and_write(sra_id+'.sam', dest_file, ga_fam_dict, valid_chroms, break_count)
                    except:
                        with open(dest_file, 'a') as f_write:
                            write_csv = csv.writer(f_write)
                            write_csv.writerow([sra_id, 'No', 'Problem with reader.py'])
                        print('\t\t' + sra_id + ' ##### Unsuccessful in reader\n')
                    if(not paired):
                        subprocess.call(['rm', sra_id+'_pass.fastq', sra_id+'.sam'])
                    else:
                        subprocess.call(['rm', sra_id+'_pass_1.fastq', sra_id+'_pass_2.fastq', sra_id+'.sam'])
                        
                subprocess.call(['rm','er_'+sra_id])
        if(not_downloaded):
            not_down_file = os.path.join(study_acc, 'not_downloaded.txt')
            with open(not_down_file, 'w') as f_not_down:
                for sra in not_downloaded:
                    f_not_down.write("%s\n" % sra)
#        os.system('ls')

def main():
    parser = ag.ArgumentParser(description = "file parser")
    parser.add_argument('--study_acc', metavar = 'study_acc', required = True, dest = 'study_acc', help = 'Study Accession')
    parser.add_argument('--ind_files', metavar = 'ind_files', required = True, dest = 'ind_files', help = 'Index Files')
    parser.add_argument('--p_fam_align', metavar = 'file', required = True, dest = 'ga_fam_pickle', help = 'Alignment for families of regions')
    parser.add_argument('--p_valid_chrom', metavar = 'file', required = True, dest = 'chrom_pickle', help = 'All chromosomes extracted from repeat sequence file')
    parser.add_argument('--paired', metavar = 'paired', required = True, dest = 'paired', help = 'single-end or paired end reads')
    parser.add_argument('--break_count', metavar = 'count', dest = 'break_count', default = 1e5, type = float, help = 'Maximum reads to be considered')
    args = parser.parse_args()
    #os.environ['PATH'] += ':/mnt/Data/Anders_group/Noor/sratoolkit.2.8.2-1-ubuntu64/bin'	    
    #os.environ['PATH'] += ':/mnt/Data/Anders_group/Noor/bowtie2-2.3.2'
	
    check_input(args.study_acc, 'Invalid directory of study acc')
    check_input(args.ind_files, 'Invalid directory of index files')
    check_input(args.ga_fam_pickle, 'Invalid Filename or path for genomic array family object')
    check_input(args.chrom_pickle, 'Invalid Filename or path for valid chromosomes object')

    ga_fam_dict = pickle.load(open(args.ga_fam_pickle, "rb"))
    valid_chroms = pickle.load(open(args.chrom_pickle, "rb"))

    args.paired = ast.literal_eval(args.paired)
    align_study(args.study_acc, args.ind_files, ga_fam_dict, valid_chroms, args.paired, args.break_count)

if __name__ == '__main__':
	main()
