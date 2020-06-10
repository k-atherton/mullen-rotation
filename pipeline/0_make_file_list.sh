#!/bin/bash -l

# Kathryn Atherton 2020

# Run this file by using the command "sh 0_make_file_list.sh"


# This file will create a list of files for you within a text file so that you can loop through all files in a folder
# or with a pattern through the pipeline / a specific file

# You will likely use this for each step of the pipeline to easily loop through all output files from the previous step

# Put your file pattern here. Use the whole path if the files are not in the same folder as this file. 
# Example patterns are "/path/to/file/*.txt" (lists all text files in a folder); "/path/to/file/*" (lists all files in a folder) 
pattern=""

# Put your output text file name here. Use the whole path if you want the file to go to a different folder as the folder this file is in.
# Likely want to name the file something like  "<file category>_list.txt" MUST END IN .txt
output=".txt"

# Write list of files to a text file.

ls $pattern >> $output
