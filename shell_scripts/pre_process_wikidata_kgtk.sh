i_path="/Users/amandeep/Documents/covid_data"
i_file="wikidata_edges_20200330.tsv.gz"
n_file="wikidata_nodes_20200330.tsv.gz"
cd $i_path || exit
pwd

i_file_no_ext=$(echo $i_file | cut -d'.' -f 1)


# cut the required columns first
#time gzcat $i_file | mlr --tsvlite --otsv cut -x -f magnitude,unit,lower,upper,latitude,longitude,precision,calendar,entity-type | gzip >"$i_file_no_ext"_truncated.tsv.gz

# filter out the properties
#gzcat "$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P685;" --datatype tsv --subj "node1" --pred "label" --obj "node2" > property_p685.tsv
#gzcat "$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P486;" --datatype tsv --subj "node1" --pred "label" --obj "node2" > property_p486.tsv
#gzcat "$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P351;" --datatype tsv --subj "node1" --pred "label" --obj "node2" > property_p351.tsv
#gzcat "$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P5055;" --datatype tsv --subj "node1" --pred "label" --obj "node2" > property_p5055.tsv


# filter qnodes with pmc and pm ids
#gzcat "$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P698,P932;" --datatype tsv --subj "node1" --pred "label" --obj "node2" > property_pubmeds.tsv


# filter out labels for all qnodes
#time gzcat $n_file | cut -d$'\t' -f 1,2 |  gzip > labels.tsv.gz

# sort labels file by qnodes
#cat labels.tsv.gz /Users/amandeep/Github/covid-kg/covid/covid_kg_new_properties.tsv.gz > labels_covid.tsv.gz
#time gzcat labels_covid.tsv.gz | tail -n +2 | LANG=C gsort -t $'\t' -S 5G --parallel=4 --key=1,1 | gzip >> labels_sorted_temp.tsv.gz
#gzcat labels_covid.tsv.gz | head -n 1 | gzip > labels_header.tsv.gz
#cat labels_header.tsv.gz labels_sorted_temp.tsv.gz > labels_sorted.tsv.gz
rm labels_header.tsv.gz
rm labels_sorted_temp.tsv.gz




#echo "node1\tlabel" | gzip > labels_header.tsv.gz
#time gzcat labels.tsv.gz | tail -n +2 | LANG=C gsort -t $'\t' -S 5G --parallel=4 --key=1,1 | gzip >> labels_sorted_temp.tsv.gz

