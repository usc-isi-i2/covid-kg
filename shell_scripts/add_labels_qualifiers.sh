covid_kg_path="/Users/amandeep/Github/covid-kg/covid"

cd $covid_kg_path || exit
pwd


#  sort by property
time cat covid_kgtk_qualifiers.tsv | tail -n +2 | LANG=C gsort -t $'\t' -S 5G --parallel=4 --key=2,2 >covid_kgtk_qualifiers_sorted_by_property_temp.tsv
head -n 1 covid_kgtk_qualifiers.tsv > header
cat header covid_kgtk_qualifiers_sorted_by_property_temp.tsv >covid_kgtk_qualifiers_sorted_by_property.tsv
rm header

# join labels for property
mlr --prepipe gunzip --tsvlite --otsv join --ul --lp '' --rp 'property_' -s -j property -l property -r id -f covid_kgtk_qualifiers_sorted_by_property.tsv then unsparsify ~/Documents/covid_data/labels_sorted.tsv.gz >covid_kgtk_qualifiers_with_labels.tsv

rm covid_kgtk_qualifiers_sorted_by_property_temp.tsv
rm covid_kgtk_qualifiers_sorted_by_property.tsv