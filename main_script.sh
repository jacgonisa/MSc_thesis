#!/bin/bash

# Define usage function
function usage() {
    cat <<EOF

SYNOPSIS

  main_script.sh      - run pipeline

  main_script.sh help - display this help message

DESCRIPTION

  This script processes a list of KO IDs provided in a text file.

AUTHOR

  Your name goes here

EOF
}

# Define info function
function info() {
    echo "INFO: $@" >&2
}

# Define error function
function error() {
    echo "ERR:  $@" >&2
}

# Define fatal function
function fatal() {
    echo "ERR:  $@" >&2
    exit 1
}

# Show help message if "help" argument is provided or no argument is provided
if [[ "$1" == "help" || $# -eq 0 ]]; then
    usage
    exit
fi

# Check for valid number of arguments
if [[ $# -ne 1 ]]; then
    error "Invalid number of arguments provided."
    usage
    exit 1
fi

# Check if the provided file exists
if [[ ! -f "$1" ]]; then
    error "File '$1' not found."
    usage
    exit 1
fi
################################################################################
#                          Find KO list		                           #
################################################################################


# Access the KO ID list path
KO_list_path=$1

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


# Define an array to store job IDs 
KO2fasta_jobids=()

emapper_jobids=()

treebuilder_jobids=()

treeannotator_jobids=()

# Loop through each KO ID in the list
while IFS= read -r KO_CODE; do
    
    # Submit KO2fasta job for the current KO code
    KO2fasta_jobid=$(sbatch --output="./KO2fasta_"$KO_CODE"_%j.out" --error="./KO2fasta_"$KO_CODE"_%j.err" /home/jacobg/01-GTDB/pipeline_for/bin/KO2fasta.slurm "$KO_CODE")
#    
    KO2fasta_jobid=${KO2fasta_jobid##* }

    # Extract the job ID and add it to the array
    KO2fasta_jobids+=("$KO2fasta_jobid")
  
    echo "Submitted KO2fasta job for KO code: $KO_CODE "
    
    echo "Job ID: $KO2fasta_jobid"


source ~/miniforge3/etc/profile.d/conda.sh
conda activate emap

    #Submit eggnogmapper job
   emapper_jobid=$(sbatch --dependency=afterok:"$KO2fasta_jobid" --output="./emapper_"$KO_CODE"_%j.out" --error="./emapper_"$KO_CODE"_%j.err" /home/jacobg/01-GTDB/pipeline_for/bin/emapper.slurm "$KO_CODE")
#    
    emapper_jobid=${emapper_jobid##* }

    # Extract the job ID and add it to the array
    emapper_jobids+=("$emapper_jobid")

    echo "Submitted emapper job for KO code: $KO_CODE "

    echo "Job ID: $emapper_jobid"


source ~/miniforge3/etc/profile.d/conda.sh
conda activate ete

    # Submit treebuilder job
    treebuilder_jobid=$(sbatch --dependency=afterok:"$KO2fasta_jobid" --output="./treebuilder_"$KO_CODE"_%j.out" --error="./treebuilder_"$KO_CODE"_%j.err" /home/jacobg/01-GTDB/pipeline_for/bin/treebuilder.slurm "$KO_CODE")
#    
    treebuilder_jobid=${treebuilder_jobid##* }

    # Extract the job ID and add it to the array
    treebuilder_jobids+=("$treebuilder_jobid")

    echo "Submitted treebuilder job for KO code: $KO_CODE "

    echo "Job ID: $treebuilder_jobid"



    # Submit treeannotator job with dependency on treebuilder job
    treeannotator_jobid=$(sbatch --output="./treeannotator_"$KO_CODE"_%j.out" --error="./treeannotator_"$KO_CODE"_%j.err" --dependency=afterok:"$treebuilder_jobid:$emapper_jobid" /home/jacobg/01-GTDB/pipeline_for/bin/treeannotator.slurm "$KO_CODE")
    
    treeannotator_jobid=${treeannotator_jobid##* }

    # Extract the job ID and add it to the array
    treeannotator_jobids+=("$treeannotator_jobid")
    
    echo "Submitted treeannotator job for KO code: $KO_CODE."
    echo "Job ID: $treeannotator_jobid"

done < "$KO_list_path"

# Print the submitted job IDs
#echo "Submitted treebuilder jobs: ${treebuilder_jobids[@]}"
#echo "Submitted treeannotator jobs: ${treeannotator_jobids[@]}"


