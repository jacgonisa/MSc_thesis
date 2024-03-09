from Bio import SeqIO
import sys

def filter_sequences(fasta_file, output_file):
    # Open the output file for writing
    with open(output_file, 'w') as out_fasta:
        # Iterate over sequences in the multifasta file
        for record in SeqIO.parse(fasta_file, "fasta"):
            sequence_length = len(record.seq)

            # Check if the sequence length is within the desired range
            if 100 <= sequence_length <= 1500:
                # Write the record to the output file
                SeqIO.write(record, out_fasta, "fasta")

if __name__ == "__main__":
    # Check if the user provided the input and output fasta files
    if len(sys.argv) != 3:
        print("Usage: python script.py input.fasta output.fasta")
        sys.exit(1)

    input_fasta = sys.argv[1]
    output_fasta = sys.argv[2]

    # Apply the filter and create the new fasta file
    filter_sequences(input_fasta, output_fasta)

    print("Filtered sequences saved to %s" % output_fasta)

