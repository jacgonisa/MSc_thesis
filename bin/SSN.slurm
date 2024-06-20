#!/bin/bash
#SBATCH --mem=100GB

#SBATCH -t 01-00:00

#SBATCH -p medium

KO_CODE="$1"
mkdir -p "$KO_CODE/tmp"


source ~/miniforge3/etc/profile.d/conda.sh

conda activate diamond 

#OUTPUT=$(basename -- $FILE)
#OUTPUT="nets/${OUTPUT/.fasta/_allAgainstAll.similarities}"
#DB="${FILE/.fasta/.db}"

FASTA="$KO_CODE/02-GTDB2fasta/"$KO_CODE"_sequences_filtered.faa"
DB="${FASTA}.db"
OUTPUT="$KO_CODE/05-SSN/"$KO_CODE"_allvsall"

# First let's make a database out of the file
echo "  Creating a database for "$KO_CODE" sequences "
diamond makedb --in $FASTA --db $DB
wait
echo ""

# Now running all against all search
echo "  Running diamond blastp 'all-against-all'"
#blastp -query $FASTA -db $DB -evalue 1e-5 -max_target_seqs 3000 -max_hsps 1 -num_threads 20 -outfmt "6 qseqid sseqid evalue pident bitscore qstart qend qlen sstart send slen" -out $OUTPUT 
diamond blastp -q $FASTA  --db $DB --max-target-seqs 3000 --evalue 1e-5 --iterate --sensitive  --threads 20  -o $OUTPUT \
-f 6 qseqid sseqid evalue pident bitscore qstart qend qlen sstart send slen \
--tmpdir ./$KO_CODE/tmp

wait

echo ""

echo "SNN done"

echo "Cleaning SNN"

python /home/jacobg/01-GTDB/pipeline_MetEOr/bin/clean_diamond.py -f $OUTPUT -o "${OUTPUT}.clean"

wait

echo "Build SNN"

python /home/jacobg/01-GTDB/pipeline_MetEOr/bin/build_network.py -f "${OUTPUT}.clean" -i "30" -c 50 -o "${OUTPUT}.clean.net"

wait

echo "Annotate clusters"


python /home/jacobg/01-GTDB/pipeline_MetEOr/bin/identify_clusters_net.py "${OUTPUT}.clean.net" "${OUTPUT}.clean.net.clusters.tsv"

wait

# Extract header and sort only data lines
(head -n 1 "${OUTPUT}.clean.net.clusters.tsv"; tail -n +2 "${OUTPUT}.clean.net.clusters.tsv" | sort -u) > tmp && mv tmp "${OUTPUT}.clean.net.clusters.tmp"

echo "End, ready to annotate with TreeProfiler!"
