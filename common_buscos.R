setwd("/projectnb/mullenl/kate/annotated_trinity_assemblies/busco_lists")
files <- list.files(pattern = "*.tsv")
data <- data.frame(matrix(0, ncol = 6, nrow = 1))
colnames(data) <- c("busco_id", "status", "sequence", "score", "length", "SF_id")
for (i in 1:length(files)){
  temp <- read.delim(files[i], header = FALSE, comment.char = "#")
  colnames(temp) <- c("busco_id", "status", "sequence", "score", "length")
  temp$SF_id <- i
  data <- rbind(data, temp)
}
data <- data[-c(1),]

buscos <- matrix(list(), nrow = length(files), ncol = 1)
j <- 1

for (i in 1:length(files)){
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

busco_counts <- matrix(1, ncol = 1, nrow = length(buscos[[1,1]]))
for (i in 1:length(buscos[[1,1]])){
  for (j in 2:length(files)){
    if (buscos[[1,1]][i] %in% buscos[[j,1]]){
      busco_counts[i,1] <- busco_counts[i,1] + 1
    }
  }
}

all_buscos <- buscos[[1,1]][which(busco_counts == length(files))]
buscos_95 <- buscos[[1,1]][which(busco_counts >= 0.95*length(files))]

write.table(all_buscos, "all_common_buscos.txt", append = FALSE, sep = "\t", quote = F, row.names = F, col.names = F)
write.table(buscos_95, "95_common_buscos.txt", append = FALSE, sep = "\t", quote = F, row.names = F, col.names = F)

cat("Buscos Common to All Genomes: \n", all_buscos, "\n\n\n")
cat("Buscos Common to 95% of Genomes: \n", buscos_95)
