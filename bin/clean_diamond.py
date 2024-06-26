#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description="Removes reciprocal hits (A-B = B-A).")

# Add the arguments to the parser
requiredArgs = parser.add_argument_group('required arguments')

requiredArgs.add_argument("-f", "--file", dest="file_in", required=True,
                    help="Input file. This assumes a file with the following columns: 'qseqid sseqid evalue pident bitscore qstart qend qlen sstart send slen'.")

requiredArgs.add_argument("-o", "--output", dest="file_out", required=True,
                    help="Output file. Returns the filtered file to the specified location.")

args = parser.parse_args()

print("Cleaning")

clean = {}
hits = set()
lines = 0
removed = 0
selfHit = 0
accepted = 0
with open(args.file_out, "w") as outfile:
    for line in open(args.file_in):
        lines += 1
        line = line.strip().split()
        seq1 = line[0]
        seq2 = line[1]
        if seq1 == seq2:  # Check for self-hit
            selfHit += 1
            continue  # Skip the line
        hit = str(seq1) + "\t" + str(seq2)
        hitr = str(seq2) + "\t" + str(seq1)
        if hit in clean or hitr in clean:
            removed += 1
            continue  # Skip the line
        else:
            accepted += 1
            hits.add(hit)
            hits.add(hitr)
            values = "\t".join(str(val) for val in line[2:])
            clean[hit] = values
            print(hit + "\t" + clean[hit], file=outfile)

print("  Hits in:      ", lines)
print("  Hits removed: ", removed)
print("  Self hits:    ", selfHit)
print("  Hits out:     ", accepted)
print("Done")
