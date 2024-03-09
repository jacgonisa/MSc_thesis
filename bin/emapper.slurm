#!/bin/bash

#SBATCH --cpus-per-task=20

#SBATCH --mem=100GB

#SBATCH -t 2:00:00

#SBATCH -p fast,medium

KO_CODE="$1"


emapper.py --cpu 20 --mp_start_method forkserver --num_servers 1 --num_workers 2 -m diamond --dmnd_ignore_warnings -i "$KO_CODE/02-GTDB2fasta/"$KO_CODE"_GTDB_sequences_filtered.faa" -o out --dbmem --evalue 0.001 --itype proteins --tax_scope auto --target_orthologs all --decorate_gff yes --num_servers 2 --score 60 --pident 40 --query_cover 20 --subject_cover 20 --pfam_realign denovo --cut_ga --override --output_dir "$KO_CODE/02-GTDB2fasta/"
