# Atherton Mullen Lab Rotation
The purpose of this rotation was to create a pipeline to identify genes common to most butterfly species and genes that produce sensory or pigmentation proteins and align these genes across butterfly species. The alignments will aid in determining the rate of evolution of the sensory and pigmentation genes in tropical vs. temperate butterfly species as compared to basal evolution (measured by the most common genes). 

Below lists all the files in the gene alignment pipeline and what they are used for. Numbered files are executed and non-numbered files are called by the executed files. They should all be kept in the same directory. 

## Files that can be used in multiple steps in the pipeline

### File Name: 0\_make\_file\_list.sh
* Required files: files to be listed
* Required modules: none


Use this file to create a list of the files you want to loop through for the following steps of the pipeline: 

1. **0\_oneline\_fasta.sh** -- use to list all fasta files to be changed to one line format
2. **1\_busco.qsub** -- use to list all annotated fasta files for BUSCO analysis
2. **6\_common_alignment.qsub** -- use to list all common busco fasta files to be aligned
3. **6\_sensory\_alignment.qsub** -- use to list all sensory or pigmentation busco fasta files to be aligned


Each time you use this file, be sure to change the file name pattern (e.g. if you want all the fasta files in a folder, the pattern would be **/path/to/files/\*.fasta**) and change the name of the file that the list will be written to. 

Run this file with the command **sh 0\_make\_file\_list.sh**

### File Name: 0\_oneline\_fasta.sh
* Required files: fasta file list (create with **0\_oneline\_fasta.sh**), files in the list
* Required modules: none

Use this file to write the annotated fasta files to one line per gene, rather than ~60 characters per line. This makes step 6 of the pipeline much simpler. 

Before running this file, change the output naming pattern, if desired. Currently, the naming pattern is **oneline_[samplename].fasta**. 

Run this file with the command **sh 0\_oneline\_fasta.sh**

## Files that must be run in order
### File Name: 1\_busco.qsub
* Required files: genome assembly files list (create with **0\_oneline\_fasta.sh**), files in the list, insecta\_odb9 lineage reference dataset (download using the command **wget http://busco.ezlab.org/v2/datasets/insecta_odb9.tar.gz**)
* Required modules: python3, blast+/2.7.1, hmmer/3.2.1, augustus/3.3.2, busco/3.0.2

Use this file to run BUSCO on your annotated fast afiles. 

Be sure to change the path to the input annotated fasta files. Currently, it points to **/projectnb/mullenl/kate/annotated\_trinity\_assemblies/annotated\_fastas/[files]**. Additionally, because of the way that the fasta files in our dataset were named, (e.g. SF.01), the output file pattern is set up such that it finds the **SF.##** pattern within the input file name. If your file names do not have this naming pattern, change the output naming pattern. 

Run this file with the command **qsub 1\_busco.qsub [filelist].txt**, where **[filelist].txt** is what you named the output file created with the **0\_make\_file\_list.sh** script. 

### File Name: 2\_busco\_plot.sh
* Required files: "short_summary" files output from **1\_busco.qsub**; **BUSCO\_plot.py**
* Required modules: python3, R

Use this file to create the visualization of the assembly quality. 

Make sure that you are in the same directory as all the BUSCO output folders (named **run_[samplename]**), or change the path in the line staring with **cp** to point to the directory where these folders are. Also, change the working directory within the line calling the python script, if necessary. Currently, it points to **/projectnb/mullenl/kate/annotated\_trinity\_assemblies**

Run this file iwth the command **qsub 2\_busco\_plot.sh**

### File Name: 3\_busco\_table\_copy.sh
* Required files: "full_table" files output from **1\_busco.qsub**
* Required modules: none

Use this file to copy all of the BUSCO tables output from the BUSCO R script run in **1\_busco.qsub**. This sets up the ability to find the most common BUSCO IDs in the dataset. 

Change the input directory to where the BUSCO output directories (folders called **run\_[samplename]**) are. Currently, it points to **/projectnb/mullenl/kate/annotated\_trinity\_assemblies/run\_\*/full\_table\*** Additionally, change the **"."** to the directory where you want to copy these tables,if it is not the directory where this file is.

Run this file with the command **sh 3\_busco\_table\_copy.sh**

### File Name: 4\_common\_buscos.qsub
* Required files: "full_table" files output from **3\_busco\_table\_copy.sh**; **common\_buscos.R**
* Required modules: R

Use this file to run an R script that downloads all the tables copied in the above script and determines which BUSCO IDs are in 95% or more of the genomes. The R script will write a list of the BUSCO IDs to a text file to be used in the next script. 

Run this file with the command **qsub 4\_common\_buscos.qsub**

## Files that can be run in parallel
Beyond this point, you should have a .txt file that contains a list of the sensory/pigmentation/etc. gene BUSCO IDs. 

Additionally, for the rest of the pipeline, the common and sensory/pigmentation BUSCOs are treated separately, but in parallel. As such, the files are named with the same step number because they can be run at the same time. The files do the same thing, but to different sets of files. As such, I will describe the files together. 

### File Name: 5\_common\_alignment\_prep.qsub & 5\_sensory\_alignment\_prep.qsub
* Required files: list of common BUSCO IDs (created by **4\_common\_buscos.qsub**)
* Required modules: none

Use these files to take your lists of BUSCOs (common and sensory/pigmentation/etc.) and write one fasta file that contains all the genes that match the BUSCOs to be aligned. 

In each file, there are places that point to the file that contain the list of BUSCOs, the path where BUSCO tables are (the same tables used in **3\_busco\_table\_copy.sh**), the path where you want the fasta files to be written to, and the path to the annotated fasta files. Be sure to double check all of these paths and change them when necessary. Additionally, for this file, it is much easier if the annotated fasta files are written such that each sequence is one line, rather than 60 characters per line. Be sure to run file **0\_oneline\_fasta.sh** if your files are not like that. 

Run these files with the command **qsub 5\_common\_alignment\_prep.qsub** and **qsub 5\_sensory\_alignment\_prep.qsub**

### File Name 6\_common\_alignment.qsub & 6\_sensory\_alignment.qsub
* Required files: **clustalomega.qsub**; fasta files to be aligned
* Required modules: clustalomega

Use these files to loop through your list of fasta files to be aligned and align them. 

You may need to change the pattern of input and output file path names as well as the name of the text file that contains the list of fasta files to be aligned. Currently, the input file pattern is **[BUSCOID].fasta** (assumes the fasta files to be aligned are in the same directory as this file) and the output file pattern is **/projectnb/mullenl/kate/annotated\_trinity\_assemblies/aligned\_fastas/[BUSCOID]\_aligned.fasta**. Be sure that these two files are in the same directory as **clustalomega.qsub**.

Run these files with the command **qsub 6\_common\_alignment.qsub** and **qsub 6\_sensory\_alignment.qsub**

## Files that are not directly called by the user, but are called by scripts
### File Name: BUSCO.py
This file was created by Felipe A. Simao (felipe.simao@unige.ch), Robert M. Waterhouse (robert.waterhouse@unige.ch), and Mathieu Seppey (mathieu.seppey@unige.ch) and comes from the BUSCO software pipeline. In this pipeline, it is called by the script **1\_busco.qsub**

### File Name: BUSCO\_plot.py
This file was created by Mathieu Seppey (mathieu.seppey@unige.ch) comes from the BUSCO pipeline and produces a graphic summary for BUSCO runs based on short summary files.  In this pipeline, it is called by the file **2\_busco\_plot.sh**

### File Name: common\_buscos.R
This file identifies the BUSCO IDs that are found in at least 95% of the genomes and writes them to a list. The file is called by the script **4\_common\_buscos.qsub**

### File Name: clustalomega.qsub
This file runs the Clustal Omega alignment software and is called by the files **6\_common\_alignment.qsub** and **6\_sensory\_alignment.qsub**