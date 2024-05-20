#!/usr/bin/env python3
import sys
import networkx as nx
import pandas as pd
import re

def create_network(file_path):
    G = nx.Graph()
    df = pd.read_csv(file_path, sep='\t', header=None, names=['source', 'target', 'rmsd'])
    
    # Add edges to the graph
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['target'], rmsd=row['rmsd'])
    
    # Find connected components
    clusters = list(nx.connected_components(G))
    
    # Assign clusters to nodes
    cluster_mapping = {}
    for i, cluster in enumerate(clusters):
        for node in cluster:
            cluster_mapping[node] = f'cluster{str(i+1).zfill(2)}'
    
    return cluster_mapping

def annotate_clusters(input_file, output_file):
    cluster_mapping = create_network(input_file)
    df = pd.read_csv(input_file, sep='\t', header=None, names=['source', 'target', 'rmsd'])
    
    # Annotate clusters
    annotated_clusters = []
    for _, row in df.iterrows():
        annotated_clusters.append((row['source'], cluster_mapping[row['source']]))
        annotated_clusters.append((row['target'], cluster_mapping[row['target']]))
    
    # Save annotated clusters to file
    with open(output_file, 'w') as f:
        f.write("#name\tcluster_type\n")  # Header
        for item in annotated_clusters:
            f.write(f"{item[0]}\t{item[1]}\n")
    
    # Apply the transformation to the 'source' column in the final output file
    with open(output_file, 'r') as f:
        lines = f.readlines()
    with open(output_file, 'w') as f:
        f.write("#name\tstructural_cluster_type\n")  # Header
        for line in lines[1:]:  # Skip the header line
            source, cluster_type = line.strip().split('\t')
            source = source.split('_unrelaxed_rank_')[0]
            f.write(f"{source}\t{cluster_type}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    annotate_clusters(input_file, output_file)
