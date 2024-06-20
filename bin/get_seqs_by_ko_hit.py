#!/usr/bin/env python3

"""
Print entries corresponding to the given KOs from the gtdb or combined database.

The output format is tab-separated (tsv).
"""

import argparse
import sqlite3


def main():
    args = get_args()

    # Define paths and tables
    if args.db == 'gtdb':
        db_path = '/home/jacobg/01-GTDB/pipeline_KO-Tree/bin/gtdb2kegg_besthits.sqlite'
        table = 'gtdb2kegg'
    elif args.db == 'combined':
        db_path = '/home/jacobg/02-MAGs/sql/combinedgtdb2kegg_besthits.sqlite'
        table = 'combinedgtdb2kegg'

    # Query the database
    query = create_query(table, args.kos, args.evalue, args.identity, args.seq_cov, args.kegg_seq_cov)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(query)

        # Output column names
       # print('\t'.join(desc[0] for desc in cursor.description))

        # Output results
        for row in cursor:
            print('\t'.join(map(str, row)))


def get_args():
    """Return the parsed command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    add = parser.add_argument  # shortcut

    add('kos', nargs='+', help='one or several KO ids to query')
    add('-d', '--db', choices=['gtdb', 'combined'], default='gtdb',
        help='database to use (default: gtdb)')
    add('-e', '--evalue', type=float, help='maximum e-value')
    add('-i', '--identity', type=float, help='minimum identity (similarity)')
    add('-s', '--seq-cov', type=float,  help='minimum sequence coverage')
    add('-k', '--kegg-seq-cov', type=float, help='minimum KEGG sequence coverage')

    return parser.parse_args()


def create_query(table, kos, evalue, identity, seq_cov, kegg_seq_cov):
    """Return the corresponding SQL query."""
    ko_list = ','.join(f'"{ko}"' for ko in kos)

    query = f'SELECT * FROM {table} WHERE ko IN ({ko_list})'

    if evalue:       query += f' AND evalue <= {evalue}'
    if identity:     query += f' AND pident >= {identity}'
    if seq_cov:      query += f' AND qcovhsp >= {seq_cov}'
    if kegg_seq_cov: query += f' AND scovhsp >= {kegg_seq_cov}'

    return query


if __name__ == '__main__':
    main()
