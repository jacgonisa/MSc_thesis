#!/usr/bin/env python3

import argparse
import sqlite3

# Argument parser setup
parser = argparse.ArgumentParser(
    description='Given one or several KO ids, returns a list of combined ref sequences whose best hit is that KO\
    example: \
    python get_combine2kegg_hits.py K13525 --evalue_thr 0.00001 --min_identity 100 --min_combined_seq_cov 99 --min_kegg_seq_cov 90'
)

parser.add_argument('query_kos', nargs='+', help='One or several KO ids to query')
parser.add_argument('--evalue_thr', type=float, help='Evalue threshold')
parser.add_argument('--min_identity', type=float, help='Minimum identity percentage')
parser.add_argument('--min_combined_seq_cov', type=float, help='Minimum COMBINED sequence coverage')
parser.add_argument('--min_kegg_seq_cov', type=float, help='Minimum KEGG sequence coverage')

args = parser.parse_args()

####################### Start Qeury ###############################

# Jacob combined2kegg sql database
database = "/home/jacobg/02-MAGs/sql/combined2kegg_besthits.sqlite"
table = 'combined2kegg'

# connect to db
conn = sqlite3.connect(database)
cursor = conn.cursor()

# parse ko list
ko_list = ','.join(f'"{ko}"' for ko in set(args.query_kos))

# sql command
sql_cmd = f"SELECT * FROM {table} WHERE ko IN ({ko_list} )"

if args.evalue_thr is not None:
    sql_cmd += f' AND evalue <= {args.evalue_thr}'

if args.min_identity is not None:
    sql_cmd += f' AND pident >= {args.min_identity}'

if args.min_combined_seq_cov is not None:
    sql_cmd += f' AND qcovhsp >= {args.min_combined_seq_cov}'

if args.min_kegg_seq_cov is not None:
    sql_cmd += f' AND scovhsp >= {args.min_kegg_seq_cov}'

# execute the query 
cursor.execute(sql_cmd)
rows = cursor.fetchall()

# column names
columns = ['combined_id', 'ko', 'kegg_id', 'pident', 'length', 'mismatch', 'gapopen', 'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore', 'qcovhsp', 'scovhsp']

# output 
print('\t'.join(columns))
for hits in cursor.execute(sql_cmd):
    print('\t'.join(map(str, hits)))

# close the connection
conn.close()
