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