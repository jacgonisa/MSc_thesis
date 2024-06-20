#!/bin/bash

#SBATCH --cpus-per-task=20
#SBATCH --mem=200GB
#SBATCH -t 1-00:00
#SBATCH -p long,bigmem

KO_CODE="$1"
ANNOTATION="${2:-default}"

# Ensure the output directories exist
mkdir -p "$KO_CODE/02-GTDB2fasta"

source ~/miniforge3/etc/profile.d/conda.sh

conda activate emap

# Run eggNOG-mapper
emapper.py --cpu 20 --mp_start_method forkserver --num_servers 1 --num_workers 2 -m diamond --dmnd_ignore_warnings \
    -i "$KO_CODE/02-GTDB2fasta/${KO_CODE}_sequences_filtered.faa" -o out --dbmem --evalue 0.001 --itype proteins \
    --tax_scope auto --target_orthologs all --decorate_gff yes --num_servers 2 --score 60 --pident 40 --query_cover 20 \
    --subject_cover 20 --pfam_realign denovo --cut_ga --override --output_dir "$KO_CODE/02-GTDB2fasta/"

# Check if the annotation type is swissprot
if [[ "$ANNOTATION" == "swissprot" ]]; then
    echo "Running BLASTP against SwissProt database"
    source ~/miniforge3/etc/profile.d/conda.sh

    conda activate blast
    
    blastp -query "$KO_CODE/02-GTDB2fasta/${KO_CODE}_sequences.faa" \
           -db /home/jacobg/01-GTDB/K21104/blast_ncbi/ref_blast_rep_proteomes/swissprot \
           -out "$KO_CODE/02-GTDB2fasta/blastp_swissprot.txt" -outfmt 6 -max_target_seqs 5
    wait
    # Filter the results to get only those with a similarity higher than 95
    awk '$3 > 95' "$KO_CODE/02-GTDB2fasta/blastp_swissprot.txt" > "$KO_CODE/02-GTDB2fasta/blastp_swissprot_filtered.txt"

    echo "Filtered BLASTP results saved to $KO_CODE/02-GTDB2fasta/blastp_swissprot_filtered.txt"

    {
        echo -e "#name\tswissprot"
        awk '{print $1 "\t" $2}' "$KO_CODE/02-GTDB2fasta/blastp_swissprot_filtered.txt"
    } > "$KO_CODE/02-GTDB2fasta/swissprot_annotations.txt"

    echo "Created filtered SwissProt annotations."
fi

