#!/bin/bash
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mem=100GB

#SBATCH -t 07-00:00

#SBATCH -p long



KO_CODE=$1

#Step 4: Alignment
srun mafft --auto $KO_CODE/02-GTDB2fasta/"$KO_CODE"_GTDB_sequences_filtered.faa > $KO_CODE/03-MSA/"$KO_CODE"_GTDB.faa.alg

#Step 5: Trim alignment

srun python /home/jacobg/01-GTDB/K00244_digoxin/03-MSA/trim_alignment.py -i $KO_CODE/03-MSA/"$KO_CODE"_GTDB.faa.alg -o $KO_CODE/03-MSA/"$KO_CODE"_GTDB_trimmed.faa.alg --min_res_percent 0.1  --min_res_abs 3

#Step 6: Tree
srun FastTree $KO_CODE/03-MSA/"$KO_CODE"_GTDB_trimmed.faa.alg > $KO_CODE/04-trees/"$KO_CODE"_GTDB.faa.alg.nw

#Step 7: Root the tree
srun python /home/jacobg/01-GTDB/K00244_digoxin/04-trees/midpoint_tree.py $KO_CODE/04-trees/"$KO_CODE"_GTDB.faa.alg.nw > $KO_CODE/04-trees/"$KO_CODE"_GTDB_rooted.faa.alg.nw


###OPTIONAL, only if trees should be annotated###

# Create directory structure
#mkdir -p $KO_CODE/04-trees/annotation_alignment_taxa_kegg


# Step 8: Create KEGG similarity
#echo -e "#name\tsimilarity" > $KO_CODE/04-trees/KEGG_similarity.tsv
#cut -f1,3 $KO_CODE/01-KO2GTDB/$KO_CODE\_matches.tsv >> $KO_CODE/04-trees/KEGG_similarity.tsv


# Step 9: Annotate tree
#srun treeprofiler annotate --tree $KO_CODE/04-trees/$KO_CODE\_GTDB_rooted.faa.alg.nw --input-type newick --alignment $KO_CODE/03-MSA/$KO_CODE\_GTDB.faa.alg --taxonomic-profile --taxadb GTDB --taxon-column name --taxon-delimiter "_protein.faa_" --taxa-field 0 --metadata $KO_CODE/04-trees/KEGG_similarity.tsv --outdir $KO_CODE/04-trees/annotation_alignment_taxa_kegg

