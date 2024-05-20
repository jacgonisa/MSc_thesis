#!/bin/bash

# Define usage function
function usage() {
    cat <<EOF

SYNOPSIS

  main_script.sh [--min_identity MIN_IDENTITY] [--min_gtdb_seq_cov MIN_GTDB_SEQ_COV] [--min_gtdb_kegg_cov MIN_GTDB_KEGG_COV] KO_list_path

DESCRIPTION

  This script processes a list of KO IDs provided in a text file.

OPTIONS

  --min_identity          Minimum identity value (default: 20)
  --min_gtdb_seq_cov      Minimum GTDB sequence coverage (default: 20)
  --min_kegg_seq_cov     Minimum GTDB KEGG coverage (default: 20)

AUTHOR

  Your name goes here

EOF
}

# Default values for optional arguments
min_similarity=20
min_gtdb_coverage=20
min_kegg_coverage=20

# Show help message if "help" argument is provided or no argument is provided
if [[ "$1" == "help" || $# -eq 0 ]]; then
    usage
    exit
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --min_identity)
            min_similarity="$2"
            shift # past argument
            shift # past value
            ;;
        --min_gtdb_seq_cov)
            min_gtdb_coverage="$2"
            shift # past argument
            shift # past value
            ;;
        --min_kegg_seq_cov)
            min_kegg_coverage="$2"
            shift # past argument
            shift # past value
            ;;
        *)
            # Assuming the remaining argument is KO_list_path
            KO_list_path="$1"
            shift # past argument
            ;;
    esac
done

# Check if mandatory argument KO_list_path is provided
if [ -z "$KO_list_path" ]; then
    echo "ERR: KO_list_path is mandatory. Please provide the path to the KO list."
    usage
    exit 1
fi

################################################################################
#                          Find KO list                                       #
################################################################################

# Convert the relative path to an absolute path
KO_list_path=$(realpath "$KO_list_path")

echo "The list with KO IDs passed is: $KO_list_path"
echo ""

echo "Step 1: KO code -> multiple FASTA -> MSA -> tree"
echo ""

num_KOs=$(cat "$KO_list_path" | wc -l)

echo "There are $num_KOs KO IDs"
echo ""


source ~/miniforge3/etc/profile.d/conda.sh
conda activate ete

################################################################################
#				SUBMIT JOBS				# 
###############################################################################

mkdir -p logs

# Define an array to store job IDs 
KO2fasta_jobids=()

SSN_jobids=()

emapper_jobids=()

treebuilder_jobids=()

treeannotator_jobids=()

# Loop through each KO ID in the list
# Ensure the IFS is set to handle spaces in file paths correctly
IFS=$'\n'
while IFS= read -r KO_CODE; do
source ~/miniforge3/etc/profile.d/conda.sh
conda activate ete

    # Submit KO2fasta job for the current KO code
    #KO2fasta_jobid=$(sbatch --output="./logs/KO2fasta_"$KO_CODE"_%j.out" --error="./logs/KO2fasta_"$KO_CODE"_%j.err" /home/jacobg/01-GTDB/pipeline_KO-Tree/bin/KO2fasta.slurm "$KO_CODE")
    KO2fasta_jobid=$(sbatch --output="./logs/KO2fasta_${KO_CODE}_%j.out" \
                        --error="./logs/KO2fasta_${KO_CODE}_%j.err" \
                        --export=KO_CODE="$KO_CODE",min_similarity="$min_similarity",min_gtdb_coverage="$min_gtdb_coverage",min_kegg_coverage="$min_kegg_coverage" \
                        /home/jacobg/01-GTDB/pipeline_KO-Tree/bin/KO2fasta.slurm)
 
    KO2fasta_jobid=${KO2fasta_jobid##* }

    # Extract the job ID and add it to the array
    KO2fasta_jobids+=("$KO2fasta_jobid")
  
    echo "Submitted KO2fasta job for KO code: $KO_CODE "
    
    echo "Job ID: $KO2fasta_jobid"
#######################

source ~/miniforge3/etc/profile.d/conda.sh
conda activate diamond

    # Submit KO2fasta job for the current KO code
    SSN_jobid=$(sbatch --dependency=afterok:"$KO2fasta_jobid" --output="./logs/SNN_"$KO_CODE"_%j.out" --error="./logs/SNN_"$KO_CODE"_%j.err" /home/jacobg/01-GTDB/pipeline_KO-Tree/bin/SSN.slurm "$KO_CODE")
    
    SSN_jobid=${SSN_jobid##* }

    # Extract the job ID and add it to the array
    SSN_jobids+=("$SSN_jobid")

    echo "Submitted SSN job for KO code: $KO_CODE "

    echo "Job ID: $SSN_jobid"



#######################
source ~/miniforge3/etc/profile.d/conda.sh
conda activate emap

    #Submit eggnogmapper job
    emapper_jobid=$(sbatch --dependency=afterok:"$KO2fasta_jobid" --output="./logs/emapper_"$KO_CODE"_%j.out" --error="./logs/emapper_"$KO_CODE"_%j.err" /home/jacobg/01-GTDB/pipeline_KO-Tree/bin/emapper.slurm "$KO_CODE")
#    
    emapper_jobid=${emapper_jobid##* }

    # Extract the job ID and add it to the array
    emapper_jobids+=("$emapper_jobid")

    echo "Submitted emapper job for KO code: $KO_CODE "

    echo "Job ID: $emapper_jobid"


source ~/miniforge3/etc/profile.d/conda.sh
conda activate ete

    # Submit treebuilder job
    treebuilder_jobid=$(sbatch --dependency=afterok:"$KO2fasta_jobid" --output="./logs/treebuilder_"$KO_CODE"_%j.out" --error="./logs/treebuilder_"$KO_CODE"_%j.err" /home/jacobg/01-GTDB/pipeline_KO-Tree/bin/treebuilder.slurm "$KO_CODE")
#    
    treebuilder_jobid=${treebuilder_jobid##* }

    # Extract the job ID and add it to the array
    treebuilder_jobids+=("$treebuilder_jobid")

    echo "Submitted treebuilder job for KO code: $KO_CODE "

    echo "Job ID: $treebuilder_jobid"



    # Submit treeannotator job with dependency on treebuilder job
    #treeannotator_jobid=$(sbatch --output="./logs/treeannotator_"$KO_CODE"_%j.out" --error="./logs/treeannotator_"$KO_CODE"_%j.err" --dependency=afterok:"$treebuilder_jobid:$emapper_jobid:$SSN_jobid" /home/jacobg/01-GTDB/pipeline_KO-Tree/bin/treeannotator.slurm "$KO_CODE")
    treeannotator_jobid=$(sbatch --output="./logs/treeannotator_${KO_CODE}_%j.out" --error="./logs/treeannotator_${KO_CODE}_%j.err" --dependency=afterok:"${treebuilder_jobid}:${emapper_jobid}:${SSN_jobid}" /home/jacobg/01-GTDB/pipeline_KO-Tree/bin/treeannotator.slurm "${KO_CODE}")

    treeannotator_jobid=${treeannotator_jobid##* }

    # Extract the job ID and add it to the array
    treeannotator_jobids+=("$treeannotator_jobid")
    
    echo "Submitted treeannotator job for KO code: $KO_CODE."
    echo "Job ID: $treeannotator_jobid"

done < "$KO_list_path"

# Print the submitted job IDs
#echo "Submitted treebuilder jobs: ${treebuilder_jobids[@]}"
#echo "Submitted treeannotator jobs: ${treeannotator_jobids[@]}"


