#!/bin/env python3

import subprocess
import os
import argparse

def usage():
    print("""
SYNOPSIS

  main_script.py [--min_identity MIN_IDENTITY] [--min_seq_cov MIN_GTDB_SEQ_COV] [--min_kegg_seq_cov MIN_KEGG_SEQ_COV] [--database DATABASE] [--annotation ANNOTATION] KO_list_path

DESCRIPTION

  This script processes a list of KO IDs provided in a text file.

OPTIONS

  --min_identity          Minimum identity value (default: 20)
  --min_seq_cov           Minimum retrieved sequence coverage (default: 20)
  --min_kegg_seq_cov      Minimum KEGG sequence coverage (default: 20)
  --database              Database to use (gtdb or combined, default: gtdb)
  --annotation            Annotation method to use (default or swissprot, default: default)

AUTHOR

  Your name goes here
""")

def submit_job(command):
    result = subprocess.run(command, capture_output=True, text=True)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    print(f"Command: {' '.join(command)}")
    print(f"STDOUT: {stdout}")
    print(f"STDERR: {stderr}")

    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command, output=stdout, stderr=stderr)

    if stdout:
        job_id = stdout.split()[-1]
        return job_id
    else:
        raise ValueError("No output from sbatch command. Unable to retrieve job ID.")

def main():
    parser = argparse.ArgumentParser(description='Process KO list and submit jobs.')
    parser.add_argument('KO_list_path', help='Path to the KO list file')
    parser.add_argument('--min_identity', type=int, default=20, help='Minimum identity value (default: 20)')
    parser.add_argument('--min_seq_cov', type=int, default=20, help='Minimum retrieved sequence coverage (default: 20)')
    parser.add_argument('--min_kegg_seq_cov', type=int, default=20, help='Minimum KEGG sequence coverage (default: 20)')
    parser.add_argument('--database', default='gtdb', choices=['gtdb', 'combined'], help='Database to use (default: gtdb)')
    parser.add_argument('--annotation', default='default', choices=['default', 'swissprot'], help='Annotation method to use (default: default)')

    args = parser.parse_args()

    KO_list_path = os.path.abspath(args.KO_list_path)

    print(f"The list with KO IDs passed is: {KO_list_path}")
    print("")

    print("Step 1: KO code -> multiple FASTA -> MSA -> tree")
    print("")

    with open(KO_list_path, 'r') as file:
        KO_list = file.readlines()

    num_KOs = len(KO_list)
    print(f"There are {num_KOs} KO IDs")
    print("")

    os.makedirs('logs', exist_ok=True)

    KO2fasta_jobids = []
    SSN_jobids = []
    emapper_jobids = []
    treebuilder_jobids = []
    treeannotator_jobids = []

    for KO_CODE in KO_list:
        KO_CODE = KO_CODE.strip()
        if not KO_CODE:
            continue

        os.system('source ~/miniforge3/etc/profile.d/conda.sh && conda activate ete')

        KO2fasta_command = [
            "sbatch",
            "--output", f"./logs/KO2fasta_{KO_CODE}_%j.out",
            "--error", f"./logs/KO2fasta_{KO_CODE}_%j.err",
            "--export", f"KO_CODE={KO_CODE},min_similarity={args.min_identity},min_coverage={args.min_seq_cov},min_kegg_coverage={args.min_kegg_seq_cov},database={args.database}",
            "/home/jacobg/01-GTDB/pipeline_MetEOr/bin/KO2fasta.slurm"
        ]
        KO2fasta_jobid = submit_job(KO2fasta_command)
        KO2fasta_jobids.append(KO2fasta_jobid)

        print(f"Submitted KO2fasta job for KO code: {KO_CODE}")
        print(f"Job ID: {KO2fasta_jobid}")

        os.system('source ~/miniforge3/etc/profile.d/conda.sh && conda activate ete')

        SSN_command = [
            "sbatch",
            "--dependency", f"afterok:{KO2fasta_jobid}",
            "--output", f"./logs/SNN_{KO_CODE}_%j.out",
            "--error", f"./logs/SNN_{KO_CODE}_%j.err",
            "/home/jacobg/01-GTDB/pipeline_MetEOr/bin/SSN.slurm",
            KO_CODE
        ]
        SSN_jobid = submit_job(SSN_command)
        SSN_jobids.append(SSN_jobid)

        print(f"Submitted SSN job for KO code: {KO_CODE}")
        print(f"Job ID: {SSN_jobid}")

        os.system('source ~/miniforge3/etc/profile.d/conda.sh && conda activate emap')

        emapper_command = [
            "sbatch",
            "--dependency", f"afterok:{KO2fasta_jobid}",
            "--output", f"./logs/emapper_{KO_CODE}_%j.out",
            "--error", f"./logs/emapper_{KO_CODE}_%j.err",
            "/home/jacobg/01-GTDB/pipeline_MetEOr/bin/emapper.slurm",
            KO_CODE,
            args.annotation
        ]
        emapper_jobid = submit_job(emapper_command)
        emapper_jobids.append(emapper_jobid)

        print(f"Submitted emapper job for KO code: {KO_CODE}")
        print(f"Job ID: {emapper_jobid}")

        os.system('source ~/miniforge3/etc/profile.d/conda.sh && conda activate ete')

        treebuilder_command = [
            "sbatch",
            "--dependency", f"afterok:{KO2fasta_jobid}",
            "--output", f"./logs/treebuilder_{KO_CODE}_%j.out",
            "--error", f"./logs/treebuilder_{KO_CODE}_%j.err",
            "/home/jacobg/01-GTDB/pipeline_MetEOr/bin/treebuilder.slurm",
            KO_CODE
        ]
        treebuilder_jobid = submit_job(treebuilder_command)
        treebuilder_jobids.append(treebuilder_jobid)

        print(f"Submitted treebuilder job for KO code: {KO_CODE}")
        print(f"Job ID: {treebuilder_jobid}")

        treeannotator_command = [
            "sbatch",
            "--output", f"./logs/treeannotator_{KO_CODE}_%j.out",
            "--error", f"./logs/treeannotator_{KO_CODE}_%j.err",
            "--dependency", f"afterok:{treebuilder_jobid}:{emapper_jobid}:{SSN_jobid}",
            "/home/jacobg/01-GTDB/pipeline_MetEOr/bin/treeannotator.slurm",
            KO_CODE,
            args.database
        ]
        treeannotator_jobid = submit_job(treeannotator_command)
        treeannotator_jobids.append(treeannotator_jobid)

        print(f"Submitted treeannotator job for KO code: {KO_CODE}")
        print(f"Job ID: {treeannotator_jobid}")

if __name__ == "__main__":
    ete
