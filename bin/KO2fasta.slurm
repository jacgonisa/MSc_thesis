#!/bin/bash 

#SBATCH --mem=50GB
#SBATCH -t 2:00:00
#SBATCH -p fast
#SBATCH --export=ALL

source ~/miniforge3/etc/profile.d/conda.sh
conda activate ete

# Access the KO code passed from the main script
#KO_CODE="$1"
# Check if the environment is activated successfully
#conda info --envs
#which samtools
# Access the arguments passed from the main script

# Create directory structure for the current KO code
mkdir -p "$KO_CODE/01-KO2GTDB" "$KO_CODE/02-GTDB2fasta" "$KO_CODE/03-MSA" "$KO_CODE/04-trees" "$KO_CODE/05-SSN"

# Step 1: Run get_gtdb.py script
python /home/jacobg/01-GTDB/pipeline_KO-Tree/bin/get_gtdb_seqs_by_ko_hit.py --evalue_thr 1e-3 --min_identity $min_similarity --min_gtdb_seq_cov $min_gtdb_coverage --min_kegg_seq_cov $min_kegg_coverage "$KO_CODE" > "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches.tsv"
echo "$KO_CODE - Number of sequences in GTDB:"
echo "$(wc -l < "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches.tsv")"

echo "Retrieving matches for $KO_CODE"

# Step 2: Get the GTDB IDs
cut -f1 "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches.tsv" > "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches_onlyIDs.tsv"

# Step 3: Extract GTDB sequences
samtools faidx /home/jacobg/gtdb_proteins_aa_reps_r207_complete_id.faa -r "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches_onlyIDs.tsv" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_GTDB_sequences.faa"
samtools faidx /home/jacobg/gtdb_nt_reps_r207_complete_id.fna.bzip -r "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches_onlyIDs.tsv" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_GTDB_sequences.fna"
echo "Retrieving sequences for $KO_CODE"

#Step 3.1. Filter by length
python /home/jacobg/01-GTDB/pipeline_KO-Tree/bin/filter_by_length.py "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_GTDB_sequences.faa"  "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_GTDB_sequences_filtered.faa"

# Step 4: Calculate protein length and write to output file
echo -e "#name\tprotein_length" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_protein_length.tsv"

awk '/^>/ { if (seqlen) print name "\t" seqlen; name = $1; seqlen = 0; next } { seqlen += length($0) } END { if (seqlen) print name "\t" seqlen }' "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_GTDB_sequences_filtered.faa" >> "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_protein_length.tsv"

echo "Processing of KO code $KO_CODE completed."




