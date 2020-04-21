source covid.env

cd $covid_kg_path || exit

gzip -f $covid_kg_path/papers_wikidata_kgtk.tsv
gzip -f $covid_kg_path/entities_wikidata_kgtk.tsv