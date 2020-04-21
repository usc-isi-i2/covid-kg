# Create Covid KGTK Format

## Installation instructions

This repository uses python and shell scripts.

Run the following commands,
```.bash
git clone https://github.com/usc-isi-i2/covid-kg
cd covid-kg

python3 -m venv covid_env
source covid_env/bin/activate
pip install -r requirements.txt

```

- Install [`kgtk`](https://github.com/usc-isi-i2/kgtk)
- Install [`mlr`](https://johnkerl.org/miller/doc/build.html)

## Setup `covid.env`

Set the following variables in the `shell_scripts/covid.env` file
-  `input_path`: the folder where the Wikidata edges and node files are present
- `edges_file`: the name of the edges file (gzipped)
- `node_file`: the name of the node file (gzipped)
- `covid_kg_path`: name of the output folder where the files will be created
- `pmc_path`: the folder containing the PMC papers from Heng
- `pm_path`: the folder containing the pubmed papers from Heng

This repository assumes you have access to the shared google drive and have the following files locally downloaded,
1. `KGTK/datasets/covid/KG-HENG/Analysis/type_counts.json`
2. `KGTK/datasets/covid/CTD_diseases.tsv.gz`
3. `KGTK/datasets/covid/CTD_genes.tsv.gz`
4. `KGTK/datasets/covid/CTD_chemicals.tsv.gz`


## Run scripts to generate KGTK Wikidata Files

Run the following scripts in order
```.bash
cd shell_scripts
./pre_process_wikidata_kgtk.sh

cd ..
python covid_analysis.py

python create_covid_kg.py

cd shell_scripts
./add_labels_statements.sh

cd ..
python filter_corpus_papers_annotations_wikidata.py

cd shell_scripts
./compress.sh
```

The following output files will be generated,
1. `<covid_kg_path>/covid_kgtk_statements_with_labels.tsv.gz`: KG Keng annotations file in the KGTK format. It includes
the papers and entities which were not present in Wikidata.
2. `<covid_kg_path>/covid_kgtk_qualifiers.tsv.gz`: qualifiers for the statements file
3. `<covid_kg_path>/qnode_details/papers_wikidata.tsv.gz`: papers found in Wikidata and its properties in KGTK format
4. `<covid_kg_path>/qnode_details/annotations_wikidata.tsv.gz`: entites found in Wikidata and its properties in KGTK format 
