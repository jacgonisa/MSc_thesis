#!/bin/bash
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mem=100GB

#SBATCH -t 01-00:00

#SBATCH -p medium




KO_CODE="$1"

# Create directory structure
mkdir -p "$KO_CODE/04-trees/annotation_alignment_taxa_kegg"


# Step 1: Create KEGG similarity
touch "$KO_CODE/04-trees/KEGG_sim_cov.tsv"
echo -e "#name\tsimilarity\tcoverage_gtdb\tcoverage_kegg" > "$KO_CODE/01-KO2GTDB/KEGG_sim_cov.tsv"
cut -f1,3,13,14 "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches.tsv" >> "$KO_CODE/01-KO2GTDB/KEGG_sim_cov.tsv"


# Step 1: Annotate tree
srun treeprofiler annotate --tree $KO_CODE/04-trees/"$KO_CODE"_GTDB_rooted.faa.alg.nw --input-type newick --alignment $KO_CODE/03-MSA/"$KO_CODE"_GTDB.faa.alg --taxonomic-profile --taxadb GTDB --taxon-column name --taxon-delimiter "_protein.faa_" --taxa-field 0 --metadata $KO_CODE/01-KO2GTDB/KEGG_sim_cov.tsv --emapper-annotations "$KO_CODE/02-GTDB2fasta/out.emapper.annotations" --emapper-pfam "$KO_CODE/02-GTDB2fasta/out.emapper.pfam"  --outdir $KO_CODE/04-trees/annotation_alignment_taxa_kegg
