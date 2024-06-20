#!/usr/bin/env python3

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ete4 import Tree

def main():
    if len(sys.argv) < 3:
        sys.exit('usage: %s NEWICK_FILE CSV_FILE' % sys.argv[0])

    # Read the tree from the Newick file
    t = Tree(open(sys.argv[1]))

    # Create a new text file to save the leaf names
    output_file_leaf_names = os.path.join(os.path.dirname(sys.argv[2]), os.path.basename(sys.argv[1]).replace('.nw', '_leaf_names.txt'))

    # Write the leaf names to the text file
    with open(output_file_leaf_names, 'w') as f:
        for leaf in t.leaves():
            f.write(leaf.name + '\n')

    print(f"Leaf names saved to {output_file_leaf_names}")

    # Read the CSV file (assuming it's comma-separated)
    df = pd.read_csv(sys.argv[2])

    # Read the order of proteins from the text file
    with open(output_file_leaf_names, 'r') as f:
        protein_order = [line.strip() for line in f]

    # Extract threshold and protein data
    thresholds = df['Threshold']
    protein_data = df.iloc[:, 2:]  # Exclude the first two columns (Threshold and Surviving Sites)

    # Reorder the columns of protein_data based on the order specified in the text file
    protein_data_ordered = protein_data[protein_order]

    # Create heatmap
    plt.figure(figsize=(7, 5))
    ax = sns.heatmap(protein_data_ordered.T, fmt="d", cmap="YlGnBu", xticklabels=thresholds, yticklabels=False)
    plt.title('Counts for Each Protein by Consensus Threshold')
    plt.xlabel('Consensus Fraction Threshold')
    plt.ylabel('Protein')
    plt.xticks(rotation=45, ha='right')

    # Remove y-axis ticks
    ax.yaxis.set_ticks([])

    # Add a secondary x-axis for surviving sites
    secax = ax.twiny()
    secax.set_xticks([i + 0.4 for i in range(len(thresholds))])
    secax.set_xticklabels(df['Surviving Sites'], rotation=45, ha='center')
    secax.set_xlabel('Surviving Sites')

    plt.tight_layout()

    # Save the plot as PNG
    heatmap_output_path = os.path.join(os.path.dirname(sys.argv[2]), 'heatmap.png')
    plt.savefig(heatmap_output_path)
    print(f"Heatmap saved to {heatmap_output_path}")


############DOTPLOT
    # Read the CSV file
    df = pd.read_csv(sys.argv[2])

    # Exclude the "Surviving Sites" column
    df = df.drop(columns=['Surviving Sites'])

    # Extract gene names and total counts
    genes = df.columns[1:]
    total_counts_per_gene = df.iloc[:, 1:].sum()

    # Create a DataFrame for Seaborn
    data = {
        'Protein': genes,
        'Total Counts': total_counts_per_gene
    }
    df_seaborn = pd.DataFrame(data)

    # Order the genes according to the gene_order
    df_seaborn['Protein'] = pd.Categorical(df_seaborn['Protein'], categories=protein_order, ordered=True)

    # Create a boxplot
    plt.figure(figsize=(12, 6))
    sns.set(style="whitegrid")
    sns.boxplot(x='Total Counts', y='Protein', data=df_seaborn, orient='h')
    plt.title('Total Counts per Gene Across Different Consensus Fraction Thresholds')
    plt.xlabel('Total Counts')
    plt.ylabel('Gene')
    plt.tight_layout()
    plt.yticks([])

    # Save the plot as PNG
    dotplot_output_path = os.path.join(os.path.dirname(sys.argv[2]), 'dotplot.png')
    plt.savefig(dotplot_output_path)
    print(f"Dotplot saved to {dotplot_output_path}")


######Count vs Length

   # Read the CSV file with protein lengths
    protein_length_df = pd.read_csv(sys.argv[4], sep="\t")
    print(protein_length_df)
    
    # Remove ">" from the 'name' column
    protein_length_df['Gene'] = protein_length_df['#name'].str.replace(">", "")
    protein_length_df['Length'] = protein_length_df['protein_length']


    df = pd.read_csv(sys.argv[2])

    # Exclude the "Surviving Sites" column
    df = df.drop(columns=['Surviving Sites'])

    # Melt the DataFrame to the appropriate format for Seaborn
    df_melted = df.melt(id_vars='Threshold', var_name='Gene', value_name='Count')
    #print(df_melted)
    # Merge with protein length DataFrame
    df_melted_length = pd.merge(df_melted, protein_length_df, on='Gene')

    # Filter DataFrame for the desired threshold
    threshold_value = 0.90
    df_filtered = df_melted_length[df_melted_length['Threshold'] == threshold_value]

    # Calculate mean and standard deviation of protein length and count
    mean_length = df_filtered['Length'].mean()
    std_length = df_filtered['Length'].std()
    mean_count = df_filtered['Count'].mean()
    std_count = df_filtered['Count'].std()

# Filter genes within protein length range but outside count range
    special_genes = df_filtered[
    (df_filtered['Length'] >= mean_length - 2*std_length) & 
    (df_filtered['Length'] <= mean_length + 2*std_length) & 
    ((df_filtered['Count'] < mean_count - 2*std_count) | (df_filtered['Count'] > mean_count + 2*std_count))
    ]

# Create scatter plot with Seaborn
    plt.figure(figsize=(10, 6))

# Plot all points
    sns.scatterplot(data=df_filtered, x='Length', y='Count', label='_nolegend_')
    for index, row in special_genes.iterrows():
        plt.scatter(row['Length'], row['Count'], color='red')
    
# Plot lines indicating the area of interest
    plt.axvline(x=mean_length - 2*std_length, color='red', linestyle='--', label='Mean - 2*Std (Length)')
    plt.axvline(x=mean_length + 2*std_length, color='red', linestyle='--', label='Mean + 2*Std (Length)')
    plt.axhline(y=mean_count - 2*std_count, color='blue', linestyle='--', label='Mean - 2*Std (Count)')
    plt.axhline(y=mean_count + 2*std_count, color='blue', linestyle='--', label='Mean + 2*Std (Count)')

# Customize plot
    plt.title(f'Count vs Protein Length at Threshold {threshold_value}')
    plt.xlabel('Protein Length')
    plt.ylabel('Count')
    
    
    
    
    


# Save list of special genes to a TSV file
    output_directory = os.path.dirname(sys.argv[2])
    special_genes.drop(columns=["#name", "protein_length"], inplace=True)
    special_genes_output_path = os.path.join(output_directory, 'special_genes.tsv')
    special_genes.to_csv(special_genes_output_path, sep='\t', index=False)
    print(f"Candidate genes saved to {special_genes_output_path}")


    # Save the scatter plot as PNG
    scatterplot_output_path = os.path.join(os.path.dirname(sys.argv[2]), 'scatterplot.png')
    plt.savefig(scatterplot_output_path)
    print(f"Scatter plot saved to {scatterplot_output_path}")

    #plt.show()

#########

    plt.figure(figsize=(10, 6))

    sns.scatterplot(data=df_filtered, x='Length', y='Count', label='_nolegend_')
    #for index, row in special_genes.iterrows():
    #    plt.scatter(row['Length'], row['Count'], color='red')

    # Plot lines indicating the area of interest
    plt.axvline(x=mean_length - 2*std_length, color='red', linestyle='--', label='Mean - 2*Std (Length)')
    plt.axvline(x=mean_length + 2*std_length, color='red', linestyle='--', label='Mean + 2*Std (Length)')
    plt.axhline(y=mean_count + 2*std_count, color='blue', linestyle='--', label='Mean + 2*Std (Count)')

    # Step 1: Get the subset of "target proteins" (length within 2 std)
    target_proteins = df_filtered[
        (df_filtered['Length'] >= mean_length - 2*std_length) &
        (df_filtered['Length'] <= mean_length + 2*std_length)
    ]

    # Step 2: Calculate the std of the count of "target proteins"
    std_count_target = target_proteins['Count'].std()

    # Step 3: Plot the std as lines
    #plt.axhline(y=mean_count - 2*std_count_target, color='green', linestyle='--', label='-2*Std (Count of Target Proteins)')
    plt.axhline(y=mean_count + 2*std_count_target, color='green', linestyle='--', label='+2*Std (of proteins within length range)')

    # Plot candidate genes based on count of target proteins
    candidate_genes = df_filtered[
        (df_filtered['Length'] >= mean_length - 2*std_length) &
        (df_filtered['Length'] <= mean_length + 2*std_length) &
        ((df_filtered['Count'] < mean_count - 2*std_count_target) | (df_filtered['Count'] > mean_count + 2*std_count_target))
    ]
    for index, row in candidate_genes.iterrows():
        plt.scatter(row['Length'], row['Count'], color='green')

    # Customize plot
    plt.title(f'Count vs Protein Length at Threshold {threshold_value}')
    plt.xlabel('Protein Length')
    plt.ylabel('Count')
    plt.legend()

    # Print list of special genes
    print("Candidate Genes (within 2*Std for Length but outside 2*Std for Count of Target Proteins):")
    print(candidate_genes['Gene'].tolist())

    # Show plot
    
    #plt.show()


# Save list of special genes to a TSV file
    output_directory = os.path.dirname(sys.argv[2])
    candidate_genes.drop(columns=["#name", "protein_length"], inplace=True)
    candidate_genes_output_path = os.path.join(output_directory, 'candidate_genes.tsv')
    candidate_genes.to_csv(candidate_genes_output_path, sep='\t', index=False)
    print(f"Candidate genes saved to {candidate_genes_output_path}")


    # Save the scatter plot as PNG
    scatterplot_candidate_output_path = os.path.join(os.path.dirname(sys.argv[2]), 'scatterplot_candidate_genes.png')
    plt.savefig(scatterplot_candidate_output_path)
    print(f"Scatter plot saved to {scatterplot_candidate_output_path}")


if __name__ == "__main__":
    main()
