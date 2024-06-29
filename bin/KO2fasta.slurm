#!/bin/bash 

#SBATCH --mem=200GB
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
python /home/jacobg/01-GTDB/pipeline_MetEOr/bin/get_seqs_by_ko_hit.py --db $database --evalue 1e-3 --identity $min_similarity --seq-cov $min_coverage --kegg-seq-cov $min_kegg_coverage "$KO_CODE" > "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches.tsv"
echo "$KO_CODE - Number of sequences:"
echo "$(wc -l < "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches.tsv")"

echo "Retrieving matches for $KO_CODE"

# Step 2: Get the GTDB IDs
cut -f1 "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches.tsv" > "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches_onlyIDs.tsv"

# Step 3: Extract sequences

# Define paths based on the selected database
if [ "$database" == "gtdb" ]; then
    protein_db="/home/jacobg/gtdb_proteins_aa_reps_r207_complete_id.faa"
    nucleotide_db="/home/jacobg/gtdb_nt_reps_r207_complete_id.fna.bzip"
    ids_file="$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches_onlyIDs.tsv"

elif [ "$database" == "combined" ]; then
    protein_db_combined="/home/jacobg/02-MAGs/microbial_genomes-v1.proteins.dups_reformatted.faa"
    nucleotide_db_combined="/home/jacobg/02-MAGs/microbial_genomes-v1.proteins.dups_reformatted.fna"
    ids_file_combined="$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches_onlyIDs.tsv"

    # Separate GTDB and combined IDs
    grep -v "@" "$ids_file_combined" > "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches_onlyIDs_gtdb.tsv"
    grep "@" "$ids_file_combined" > "$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches_onlyIDs_combined.tsv"
    ids_file_gtdb="$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches_onlyIDs_gtdb.tsv"
    ids_file_combined_filtered="$KO_CODE/01-KO2GTDB/"$KO_CODE"_matches_onlyIDs_combined.tsv"

    # Set paths for GTDB database
    protein_db_gtdb="/home/jacobg/gtdb_proteins_aa_reps_r207_complete_id.faa"
    nucleotide_db_gtdb="/home/jacobg/gtdb_nt_reps_r207_complete_id.fna.bzip"

else
    echo "ERR: Unsupported database type: $database. Exiting."
    exit 1
fi

# Extract sequences using samtools faidx
if [ "$database" == "gtdb" ]; then
    samtools faidx "$protein_db" -r "$ids_file" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences.faa"
    samtools faidx "$nucleotide_db" -r "$ids_file" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences.fna"
elif [ "$database" == "combined" ]; then
    # Retrieve sequences from GTDB database
    samtools faidx "$protein_db_gtdb" -r "$ids_file_gtdb" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_gtdb.faa"
    samtools faidx "$nucleotide_db_gtdb" -r "$ids_file_gtdb" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_gtdb.fna"

    # Retrieve sequences from combined database
    samtools faidx "$protein_db_combined" -r "$ids_file_combined_filtered" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_combined.faa"
    samtools faidx "$nucleotide_db_combined" -r "$ids_file_combined_filtered" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_combined.fna"

    # Merge the results
    cat "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_gtdb.faa" "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_combined.faa" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences.faa"
    cat "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_gtdb.fna" "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_combined.fna" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences.fna"

    # Optionally, remove intermediate files
    rm "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_gtdb.faa" "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_combined.faa"
    rm "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_gtdb.fna" "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_combined.fna"
fi

echo "Retrieving sequences for $KO_CODE"

wait

#Step 3.1. Filter by length
python /home/jacobg/01-GTDB/pipeline_MetEOr/bin/filter_by_length.py "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences.faa"  "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_filtered.faa"

# Step 4: Calculate protein length and write to output file
echo -e "#name\tprotein_length" > "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_protein_length.tsv"

awk '/^>/ { if (seqlen) print name "\t" seqlen; name = $1; seqlen = 0; next } { seqlen += length($0) } END { if (seqlen) print name "\t" seqlen }' "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_filtered.faa" >> "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_protein_length.tsv"

echo "Processing of KO code $KO_CODE completed."




