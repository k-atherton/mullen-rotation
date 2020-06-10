# Set working directory to where the .tsv files are (output directory from file 3) 
setwd("/projectnb/mullenl/kate/annotated_trinity_assemblies/busco_lists")
files <- list.files(pattern = "*.tsv") # all tables that reference the busco ID, busco rating, and trinity ID
#files <- files[-c(1)] # move the limenitis table to the bottom for numbering purposes
#files <- c(files, "full_table_Limenitis.tsv")
data <- data.frame(matrix(0, ncol = 6, nrow = 1)) # initiate a data frame
colnames(data) <- c("busco_id", "status", "sequence", "score", "length", "Sample_id")
for (i in 1:length(files)){
  temp <- read.delim(files[i], header = FALSE, comment.char = "#")
  colnames(temp) <- c("busco_id", "status", "sequence", "score", "length") # save desired data to the dataframe
  temp$Sample_id <- files[i]
  data <- rbind(data, temp)
}
data <- data[-c(1),] # remove the initial blank row

buscos <- matrix(list(), nrow = length(files), ncol = 1) 
j <- 1

for (i in 1:length(files)){ # make a list of all complete buscos
  while(data$SF_id[j] == i){
    if (data$status[j] == "Duplicated"){
      buscos[[i,1]] <- c(buscos[[i,1]], data$busco_id[j])
    } else if (data$status[j] == "Complete"){
      buscos[[i,1]] <- c(buscos[[i,1]], data$busco_id[j])
    }
    j <- j + 1
    if (j > length(data$busco_id)){
      break
    }
  }
}

# remove the duplicates from the lists for quicker comparisons
for (i in 1:length(buscos)){
  buscos[[i,1]] <- unique(buscos[[i,1]])
}

busco_counts <- matrix(1, ncol = 1, nrow = length(buscos[[1,1]])) # count how many genomes each busco ID is listed in
for (i in 1:length(buscos[[1,1]])){
  for (j in 2:length(files)){
    if (buscos[[1,1]][i] %in% buscos[[j,1]]){
      busco_counts[i,1] <- busco_counts[i,1] + 1
    }
  }
}

all_buscos <- buscos[[1,1]][which(busco_counts == length(files))] # save buscos that are in all genomes
buscos_95 <- buscos[[1,1]][which(busco_counts >= 0.95*length(files))] # save buscos that are in 95% or more of genomes

# save to txt files
write.table(all_buscos, "all_common_buscos.txt", append = FALSE, sep = "\t", quote = F, row.names = F, col.names = F)
write.table(buscos_95, "95_common_buscos.txt", append = FALSE, sep = "\t", quote = F, row.names = F, col.names = F)

#cat("Buscos Common to All Genomes: \n", all_buscos, "\n\n\n")
#cat("Buscos Common to 95% of Genomes: \n", buscos_95)

# save true IDs to the data frame
# specific to SF.## pattern
#for(i in 1:length(data$SF_id)){
#  if(as.numeric(data$SF_id[i]) <= 9){
#    data$SF_id[i] <- paste0("SF0",data$SF_id[i])
#  } else if(as.numeric(data$SF_id[i]) <= 46){
#    data$SF_id[i] <- paste0("SF",data$SF_id[i])
#  } else if(as.numeric(data$SF_id[i]) <= 52){
#    data$SF_id[i] <- paste0("SF",as.numeric(data$SF_id[i]) + 1)
#  } else if(as.numeric(data$SF_id[i]) <= 71){
#    data$SF_id[i] <- paste0("SF",as.numeric(data$SF_id[i]) + 2)
#  } else{
#    data$SF_id[i] <- "Limenitis"
#  }
#}

# make a table of all Trinity IDs that match a Busco ID
for(i in 1:length(buscos_95)){
  alignments <- data[which(data$busco_id == buscos_95[i]),]
  write_alignments <- alignments[,c("sequence", "Sample_id")]
  write.table(write_alignments, paste0(buscos_95[i],".csv"), append = FALSE, sep = ",", quote = F, row.names = F, col.names = T)
}
