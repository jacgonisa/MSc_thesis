#!/bin/bash
#SBATCH -N 1
#SBATCH --mem=100GB

#SBATCH -t 07-00:00

#SBATCH -p long

KO_CODE=$1

mkdir -p "$KO_CODE/threshold_analysis"

#Step 4: Alignment
mafft --auto $KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_filtered.faa > $KO_CODE/03-MSA/"$KO_CODE".faa.alg

#Step 5: Trim alignment
python /home/jacobg/01-GTDB/pipeline_MetEOr/bin/trim_alignment.py -i $KO_CODE/03-MSA/"$KO_CODE".faa.alg -o $KO_CODE/03-MSA/"$KO_CODE"_trimmed.faa.alg --min_res_percent 0.1  --min_res_abs 3

#Step 6: Tree
FastTree $KO_CODE/03-MSA/"$KO_CODE"_trimmed.faa.alg > $KO_CODE/04-trees/"$KO_CODE".faa.alg.nw

#Step 7: Root the tree
python /home/jacobg/01-GTDB/pipeline_MetEOr/bin/midpoint_tree.py $KO_CODE/04-trees/"$KO_CODE".faa.alg.nw > $KO_CODE/04-trees/"$KO_CODE"_rooted.faa.alg.nw

#Step 8: Create output files
python /home/jacobg/01-GTDB/pipeline_MetEOr/bin/threshold_algorithm.py --threshold 80,97 --by 1 $KO_CODE/03-MSA/"$KO_CODE".faa.alg "$KO_CODE/threshold_analysis/"$KO_CODE"_threshold_analysis.csv" "$KO_CODE/threshold_analysis/"$KO_CODE"_surviving_columns.txt"

#Step 9: Use previous files to plot

python /home/jacobg/01-GTDB/pipeline_MetEOr/bin/plot_algorithm.py $KO_CODE/04-trees/"$KO_CODE"_rooted.faa.alg.nw "$KO_CODE/threshold_analysis/"$KO_CODE"_threshold_analysis.csv" "$KO_CODE/threshold_analysis/"$KO_CODE"_surviving_columns.txt" $KO_CODE/02-GTDB2fasta/"$KO_CODE"_protein_length.tsv
