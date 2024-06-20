#!/bin/bash
#SBATCH -N 1
#SBATCH --mem=100GB

#SBATCH -t 01-00:00

#SBATCH -p medium




KO_CODE="$1"
database="$2"

# Create directory structure
mkdir -p "$KO_CODE/04-trees/annotation_alignment_taxa_SSN" "$KO_CODE/04-trees/annotation_alignment_taxa_SSN_emapper"


# Step 1: Create KEGG similarity
touch "$KO_CODE/04-trees/KEGG_sim_cov.tsv"
echo -e "#name\tsimilarity\tcoverage_gtdb\tcoverage_kegg" > "$KO_CODE/01-KO2GTDB/KEGG_sim_cov.tsv"
cut -f1,3,13,14 "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches.tsv" >> "$KO_CODE/01-KO2GTDB/KEGG_sim_cov.tsv"


# Step 1: Annotate tree

# Step 1: Annotate tree based on the database selection
if [ "$database" == "gtdb" ]; then
    treeprofiler annotate --tree "$KO_CODE/04-trees/${KO_CODE}_rooted.faa.alg.nw" --alignment "$KO_CODE/03-MSA/${KO_CODE}.faa.alg" --input-type newick --metadata "$KO_CODE/05-SSN/${KO_CODE}_allvsall.clean.net.clusters.tsv" "$KO_CODE/01-KO2GTDB/KEGG_sim_cov.tsv" --outdir "$KO_CODE/04-trees/annotation_alignment_taxa_SSN" --taxadb GTDB --taxon-column name --taxon-delimiter "_protein.faa_" --taxa-field 0

elif [ "$database" == "combined" ]; then
    treeprofiler annotate --tree "$KO_CODE/04-trees/${KO_CODE}_rooted.faa.alg.nw" --alignment "$KO_CODE/03-MSA/${KO_CODE}.faa.alg" --input-type newick --metadata "$KO_CODE/05-SSN/${KO_CODE}_allvsall.clean.net.clusters.tsv" "$KO_CODE/01-KO2GTDB/KEGG_sim_cov.tsv" "$KO_CODE/02-GTDB2fasta/swissprot_annotations.txt" --taxadb GTDB --taxon-column name --taxon-delimiter "_protein.faa_" --taxa-field 0 --outdir "$KO_CODE/04-trees/annotation_alignment_taxa_SSN"
else
    echo "ERR: Unsupported database type: $database. Exiting."
    exit 1
fi

#treeprofiler annotate --tree $KO_CODE/04-trees/"$KO_CODE"_rooted.faa.alg.nw --alignment $KO_CODE/03-MSA/"$KO_CODE".faa.alg --input-type newick --metadata "$KO_CODE/05-SSN/"$KO_CODE"_allvsall.clean.net.clusters.tsv" $KO_CODE/01-KO2GTDB/KEGG_sim_cov.tsv  --outdir $KO_CODE/04-trees/annotation_alignment_taxa_SSN --taxadb GTDB --taxon-column name --taxon-delimiter "_protein.faa_" --taxa-field 0

wait

treeprofiler annotate --tree $KO_CODE/04-trees/annotation_alignment_taxa_SSN/"$KO_CODE"_rooted.faa.alg_annotated.nw --input-type newick --emapper-annotations "$KO_CODE/02-GTDB2fasta/out.emapper.annotations" --emapper-pfam "$KO_CODE/02-GTDB2fasta/out.emapper.pfam" --alignment "$KO_CODE/03-MSA/${KO_CODE}.faa.alg"  --outdir $KO_CODE/04-trees/annotation_alignment_taxa_SSN_emapper 

#$KO_CODE/01-KO2GTDB/KEGG_sim_cov.tsv 
#  --metadata "$KO_CODE/05-SSN/"$KO_CODE"_allvsall.clean.net.clusters.tsv"  --emapper-annotations "$KO_CODE/02-GTDB2fasta/out.emapper.annotations" --emapper-pfam "$KO_CODE/02-GTDB2fasta/out.emapper.pfam" 
# --alignment $KO_CODE/03-MSA/"$KO_CODE"_GTDB.faa.alg 
# treeprofiler annotate --tree annotation_alignment_taxa_emapper_SSN/K21104_GTDB_rooted.faa.alg_annotated.nw --input-type newick --metadata ../05-SSN/TMalign_results_clean.clean.clusters.tsv --outdir annotation_alignment_taxa_emapper_SSN_StrSN 
