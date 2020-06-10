#!/bin/bash -l

# Kathryn Atherton 2020
# Run this file with the command "sh 3_busco_table_copy.sh"

# Change the input directory to where the busco output directories are. 
# Change the "." to where you want to put the busco tables if it is not the current directory.

cp /projectnb/mullenl/kate/annotated_trinity_assemblies/run_*/full_table* .
