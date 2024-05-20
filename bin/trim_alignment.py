import sys
from Bio import SeqIO
from collections import Counter, defaultdict
from argparse import ArgumentParser

def gap_clean(algfile, min_res_abs, min_res_percent):
    
    #print("# seqs:%s, alg_length:%d, min_res_thr:%d" %(len(alg), len(next(alg.iter_entries())[1]), min_res))
    counter = Counter()
    nseqs = 0 
    for record in SeqIO.parse(algfile, format="fasta"):
        nseqs += 1
        for i, ch in enumerate(str(record.seq)):
            if ch != args.gap_symbol:
                counter[i] += 1
    min_res = min(int((nseqs * min_res_percent)), min_res_abs)

    col_selection = []
    c_columns, r_columns = 0, 0
    for col, v in counter.items():
        if v > 1 and v > min_res:
            c_columns += 1
            col_selection.append(col)
        else:
            r_columns += 1
    col_selection.sort()

    with open(args.output, 'w') as OUT: 
        for record in SeqIO.parse(algfile, format="fasta"):
            name = record.id
            seq = str(record.seq)
            trimmed_seq = ''.join([seq[c] for c in col_selection])
            print('>%s\n%s' %(name, trimmed_seq), file=OUT)


if __name__ == "__main__":
    parser = ArgumentParser(description='A very basic program that removes gap columns from a multiple sequence alignment')

    parser.add_argument('--version', action='version',
                                     version='%(prog)s 0.1')

    parser.add_argument('-i', dest='input_alg', type=str, required=True,
                        help='input alignment in FASTA format')

    parser.add_argument('--alg_format', dest='alg_format', choices=['fasta', 'iphylip_relaxed'], default="fasta")

    parser.add_argument('-o', dest='output', type=str, required=True,
                        help='output file name')

    parser.add_argument('--min_res_abs', dest='min_res_abs', type=int, required=True,
                        help='Min number of aligned residues in a column to keep it ')

    parser.add_argument('--min_res_percent', dest='min_res_percent', type=float,  required=True, 
                        help='Min percentage of aligned residues in a column to keep it (unless --min_res_abs is lower)')

    parser.add_argument('--gap_symbol', dest='gap_symbol', type=str, default='-')


    args = parser.parse_args()
    gap_clean(args.input_alg, args.min_res_abs, args.min_res_percent)

