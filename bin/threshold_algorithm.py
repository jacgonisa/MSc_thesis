#!/usr/bin/env python3

"""
A program to see the number of sites with a value different from
the consensus.
"""

import sys
import csv
from collections import OrderedDict

import argparse

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='A program to see the number of sites with a value different from the consensus.')
    parser.add_argument('ALIGN_FILE', help='Input alignment file')
    parser.add_argument('OUTPUT_CSV', help='Output CSV file')
    parser.add_argument('OUTPUT_TXT', help='Output text file')
    parser.add_argument('--threshold', type=str, help='Threshold range (e.g., "80,97")', required=True)
    parser.add_argument('--by', type=int, help='Step size', required=True)

    # Parse command-line arguments
    args = parser.parse_args()
    
    # Check if required arguments are provided
    if not all([args.ALIGN_FILE, args.OUTPUT_CSV, args.OUTPUT_TXT]):
        print("Error: Required arguments missing.")
        parser.print_help()
        sys.exit(1)

        
    # Get threshold range and step size
    threshold_range = [int(x) for x in args.threshold.split(',')]
    step_size = args.by

    # Get the alignment file from the command-line arguments
    falign = args.ALIGN_FILE

    # Print a message indicating the file being read
    print('Reading alignment file:', falign)

    # Read sequences from the alignment file
    proteins, msa = zip(*read_seqs(falign).items())

    # Determine the number of sequences and locations in the alignment
    nseqs, nlocs = len(msa), len(msa[0])  # number of sequences and locations
    assert all(len(seq) == nlocs for seq in msa)

    # Print information about the alignment
    print(f'Read {nseqs} sequences, each one with {nlocs} locations.')
    print('The proteins we have are:')
    for i, prot in enumerate(proteins):
        print(i + 1, prot)

    # Calculate consensus proportions and print the results for various thresholds
    proportions = consensus_props(msa)
    print('Min consensus fraction -> (surviving) '
          'number of sites differing from consensus, per sequence')

    # Create a list to store data for writing to CSV
    csv_data = []

    # Create threshold values using the provided range and step size
    pmin_values = [x/100 for x in range(threshold_range[0], threshold_range[1] + 1, step_size)]

    surviving_all = []  # surviving columns, for each pmin threshold

    for pmin in pmin_values:
    
        surviving = [i for i, (x, p) in enumerate(proportions) if p >= pmin]
        surviving_all.append(surviving)
        n_differing = differing(msa, proportions, pmin)
        print('%.2f ->' % pmin, '(%3d)' % len(surviving),  ## this len is very important
              ' '.join('%3d' % n for n in n_differing))
        
        row_data = [len(surviving)] + n_differing
        csv_data.append([pmin] + row_data)
        
    # Write the data to a CSV file
    with open(args.OUTPUT_CSV, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Threshold'] + ['Surviving Sites'] + list(proteins))
        csvwriter.writerows(csv_data)

    print('The surviving columns are:')
    for surviving, pmin in zip(surviving_all, pmin_values):
        print('%.2f ->' % pmin, ','.join('%d' % i for i in surviving))
        
    # Write the surviving columns information to a text file
    with open(args.OUTPUT_TXT, 'w') as txtfile:
        for surviving, pmin in zip(surviving_all, pmin_values):
            txtfile.write('%.2f \t' % pmin + ', '.join('%d' % i for i in surviving) + '\n')


# Function to calculate the number of differing sites from the consensus
def differing(msa, proportions=None, pmin=0.75):
    """Return the number of positions that differ from the consensus sequence.

    For sites where at least a `pmin` fraction of amino acids are the
    same at that position through the sequences in `msa`.
    """
    props = proportions or consensus_props(msa)  # consensus proportions

    nrows, ncols = len(msa), len(msa[0])  # number of rows and columns
    assert len(props) == ncols and all(len(x) == ncols for x in msa)

    return [sum(1 for aa,(x,p) in zip(seq, props) if aa != x and p >= pmin) # important the 'and', because only interested in differences in highly similar sites
            for seq in msa]


# Function to calculate consensus proportions
def consensus_props(msa):
    """Return list of most common letter and its proportion in the given msa.

    The output looks like [(s0, prop0), (s1, prop1), ...].
    """
    nrows, ncols = len(msa), len(msa[0])  # number of rows and columns
    assert all(len(x) == ncols for x in msa)

    props = []
    for col in range(ncols):
        count = {}
        for row in range(nrows):
            aa = msa[row][col]  # amino acid in position [row][col]
            count.setdefault(aa, 0)
            count[aa] += 1
        # Exclude positions where the consensus is "-"
        if '-' in count:
            del count['-']
        if count:  # Check if count is not empty after excluding "-"
            aa_consensus, n = max(count.items(), key=lambda x: x[1])
            props.append((aa_consensus, n / nrows))

    return props

# Function to read sequences from a FASTA file
def read_seqs(fasta):
    """Return a dictionary containing the sequences in the given fasta file."""
    description = None
    seqs = OrderedDict()
    for line in open(fasta):
        line = line.strip()
        if line.startswith('>'):
            if description is not None:
                seqs[description] = seq
            description = line[1:]
            seq = ''
        else:
            seq += line

    if description is not None:
        seqs[description] = seq

    return seqs



# We are not using this function, but it may be nice to have. Should
# be similar to the one in biopython.
def consensus(msa, pmin=0.75, undef=['X']):
    """Return the consensus sequence for the given multiple sequence alignment.

    The sequences in `msa` must have the same aminoacid in at least a
    proportion `pmin` of them for it to appear in the consensus
    sequence. Otherwise, it uses the character `undef` at that position.
    """
    nrows, ncols = len(msa), len(msa[0])  # number of rows and columns
    assert all(len(x) == ncols for x in msa)

    seq = ''  # will be the consensus sequence
    for col in range(ncols):
        count = {}
        for row in range(nrows):
            aa = msa[row][col]  # aminoacid in position [row][col]
            count.setdefault(aa, 0)
            count[aa] += 1
        aa_consensus, n = max(count.items(), key=lambda x: x[1])
        seq += aa_consensus if n / nrows >= pmin else undef

    return seq

if __name__ == '__main__':
    main()