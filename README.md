# MetEOr: Metagenomic-driven Enzymatic Ortholog discovery

![MetEOr Logo](MetEOr_logo.png)

MetEOr is an innovative pipeline for discovering enzymatic orthologs using metagenomic data. Developed as part of a Master's thesis, this project aims to streamline the identification and analysis of enzymatic orthologs from complex metagenomic datasets.

## 🚀 Features

- Automated processing of metagenomic data
- Identification of enzymatic orthologs
- Network-based analysis of enzyme relationships
- Phylogenetic tree construction and annotation
- Integration with KEGG Orthology (KO) database

## 📁 Repository Structure
- `main_script.py`: The primary Python script for the pipeline.
- `bin/`: Contains auxiliary scripts used in the pipeline.
- 
  SLURM scripts for job submission in a cluster environment:
  
  - `emapper.slurm`
  - `KO2fasta.slurm`
  - `SSN.slurm`
  - `treeannotator.slurm`
  - `treebuilder.slurm`
  - 
  Python scripts launched dependent on SLURM scripts:

  - `build_network.py`: Builds a network for enzymatic ortholog analysis.
  - `build_network_structure.py`: Structures or extends the network built by `build_network.py`.
  - `clean_diamond.py`: Cleans up data using the Diamond tool.
  - `filter_by_length.py`: Filters sequences based on length criteria.
  - `get_seqs_by_ko_hit.py`: Retrieves sequences based on hits to KEGG Orthology (KO).
  - `identify_clusters_net.py`: Identifies clusters within a network context.
  - `identify_clusters_structural.py`: Identifies structural clusters or patterns.
  - `midpoint_tree.py`: Constructs midpoint trees for phylogenetic analysis.
  - `plot_algorithm.py`: Generates plots related to algorithms or data analysis results.
  - `threshold_algorithm.py`: Implements algorithms with specified thresholds.
  - `trim_alignment.py`: Trims sequence alignments.

## 🛠️ Installation

MetEOr is designed to be run in an HPC cluster. Detailed installation instructions will be provided as the project progresses. We plan to implement it in Nextflow or distribute it via a Singularity container.

### Prerequisites

- Python 3.7+
- SLURM in HPC (High Performance Computing) cluster to run the programme.

## 📘 Usage

Comprehensive usage instructions and examples will be added as the project develops. The pipeline will be designed for ease of use in both local and cluster environments.

## 🤝 Contributing

We welcome contributions to MetEOr! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📞 Contact

For questions, suggestions, or collaborations, please contact:

[jacgonisa](https://github.com/jacgonisa)

---

⚠️ **Note**: This project is under active development. Check back regularly for updates and new features!
