#!/bin/bash -l

# Kathryn Atherton 2020
# Run this file using "sh 0_oneline_fasta.sh"

while read i; do
	input=$i
	# CHANGE THIS IF YOU WANT A DIFFERENT OUTPUT NAMING PATTERN
	output="oneline_$i"
	cat $input | sed -E 's/(>\w+)/\1!!!/' | tr -d '\n' | sed -E 's/>/\n&/g' | sed -E 's/!!!/\n/g' >> $output
done < list.txt
