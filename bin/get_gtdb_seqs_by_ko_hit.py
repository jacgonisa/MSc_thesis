#! /usr/bin/env python


import sqlite3
import sys
import argparse 
import os

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
parser = argparse.ArgumentParser(
                    description='Given one or several KO ids, returns a list of GTDB ref sequences whose best hit is that KO', 
    epilog = 'Example:\n  $get_gtdb_seqs_by_ko_hit.py K07466 --evalue_thr 0.00001 --min_identity 100 --min_gtdb_seq_cov 99 --min_kegg_seq_cov 99'
)

parser.add_argument('target_kos', nargs='+')
parser.add_argument('--min_identity', type=float)      
parser.add_argument('--evalue_thr', type=float)      
parser.add_argument('--min_gtdb_seq_cov', type=float)      
parser.add_argument('--min_kegg_seq_cov', type=float)      

args = parser.parse_args()
#print(args)

conn = sqlite3.connect(os.path.join(BASE_PATH, "gtdb2kegg_besthits.sqlite"))
cur = conn.cursor()
ko_list = ','.join(map(lambda x: '"%s"' %x, set(args.target_kos)))
cmd = "SELECT * FROM gtdb2kegg WHERE gtdb2kegg.ko IN (%s)" %ko_list

if args.min_identity is not None: 
    cmd += ' AND pident >= %f' %args.min_identity

if args.min_gtdb_seq_cov is not None: 
    cmd += ' AND qcovhsp >= %f' %args.min_gtdb_seq_cov

if args.min_kegg_seq_cov is not None: 
    cmd += ' AND scovhsp >= %f' %args.min_kegg_seq_cov

if args.evalue_thr is not None: 
    cmd += ' AND evalue <= %f' %args.evalue_thr


for m in cur.execute(cmd):
    print('\t'.join(map(str, m)))


