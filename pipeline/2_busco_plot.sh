#!/bin/bash -l
#
# Run this file using 'qsub plot.sh'
# Kathryn Atherton 2019

# All lines starting with "#$" are SGE qsub commands

# Specify a project to run under
#$ -P mullenl

# Give this job a name
#$ -N busco_plot

# Name the file where to redirect standard output and error 
#$ -o plot_log

# Send an email when the job begins and when it ends running
# -m eas

# Request a large memory node, this will affect your queue time, but it's better to overestimate
#$ -l mem_per_core=8G

# Request more cores, this will affect your queue time, make sure your program supports multithreading
#$ -pe omp 1

# Now we write the script that the compute node will work on.

# First, let's keep track of some information just in case anything goes wrong
echo "=========================================================="
echo "Starting on : $(date)"
echo "Running on node : $(hostname)"
echo "Current directory : $(pwd)"
echo "Current job ID : $JOB_ID"
echo "Current job name : $JOB_NAME"
echo "Task index number : $SGE_TASK_ID"
echo "=========================================================="

# load any modules you might use 
module load python3
module load R

# do some work
# copy all short summaries to the current directory
# make sure you are in the same directory as all the busco output folders (called run_<output>)
cp run_*/short_summary_* .

# run the busco plot script
# CHANGE THE WORKING DIRECTORY IF NECESSARY (directory after -wd)
python BUSCO_plot.py -wd /projectnb/mullenl/kate/annotated_trinity_assemblies

Rscript busco_figure.R

# removes the copied files from the current directory to save space
rm -rf short_summary_*
