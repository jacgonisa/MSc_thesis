#!/usr/bin/env python3

import argparse
import re

def clean_data(input_file, output_file):
    clean = {}
    removed = 0
    accepted = 0
    selfHit = 0
    with open(output_file, "w") as outfile:
        with open(input_file, "r") as infile:
            next(infile)  # Skip the header line
            for line in infile:
                line = line.strip().split()
                seq1 = line[0]
                seq2 = line[1]
                
                if seq1 == seq2:
                    selfHit += 1
                    continue  # Skip self-hits
                
                hit = str(seq1) + "\t" + str(seq2)
                hitr = str(seq2) + "\t" + str(seq1)
                
                if hit in clean or hitr in clean:
                    removed += 1
                    continue  # Skip reciprocal hits
                else:
                    values = "\t".join(str(val) for val in line[2:])
                    clean[hit] = values
                    accepted += 1
                    print(hit + "\t" + clean[hit], file=outfile)
    
    print("  Hits in:      ", accepted + removed)
    print("  Hits removed: ", removed)
    print("  Self hits:    ", selfHit)
    print("  Hits out:     ", accepted)
    print("")

def create_network(input_file, output_file, rmsd_threshold):
    with open(output_file, "w") as outfile:
        with open(input_file, "r") as infile:
            next(infile)  # Skip the header line
            for line in infile:
                data = line.strip().split("\t")
                seq1, seq2, rmsd = data[:3]
                if seq1 != seq2 and float(rmsd) <= rmsd_threshold:
                    out_line = f"{seq1}\t{seq2}\t{rmsd}"  # Modify according to the actual column order
                    print(out_line, file=outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Removes reciprocal hits (A-B = B-A) and creates a network file with a given RMSD threshold.")
    parser.add_argument("-f", "--file", dest="file_in", required=True, help="Input file with columns: 'seq1 seq2 rmsd ...'.")
    parser.add_argument("-o", "--output", dest="file_out", required=True, help="Output file for cleaned data.")
    parser.add_argument("-r", "--rmsd", dest="rmsd", type=float, required=True, help="RMSD threshold to establish a connection between nodes.")
    args = parser.parse_args()
    
    print("Cleaning the file:")
    clean_data(args.file_in, args.file_out)
    
    print("Creating network file:")
    create_network(args.file_out, args.file_out + ".net", args.rmsd)
    
    print("Done")

