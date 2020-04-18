source covid.env

i_file_no_ext=$(echo $edges_file | cut -d'.' -f 1)

# cut the required columns first
time gzcat $input_path/$edges_file | mlr --tsvlite --otsv cut -x -f magnitude,unit,lower,upper,latitude,longitude,precision,calendar,entity-type | gzip >"$input_path/$i_file_no_ext"_truncated.tsv.gz

# filter out the properties
gzcat "$input_path/$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P685;" --datatype tsv --subj "node1" --pred "label" --obj "node2" >$input_path/property_p685.tsv
gzcat "$input_path/$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P486;" --datatype tsv --subj "node1" --pred "label" --obj "node2" >$input_path/property_p486.tsv
gzcat "$input_path/$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P351;" --datatype tsv --subj "node1" --pred "label" --obj "node2" >$input_path/property_p351.tsv
gzcat "$input_path/$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P5055;" --datatype tsv --subj "node1" --pred "label" --obj "node2" >$input_path/property_p5055.tsv

# filter qnodes with pmc and pm ids
gzcat "$input_path/$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P698,P932;" --datatype tsv --subj "node1" --pred "label" --obj "node2" >$input_path/property_pubmeds.tsv

# filter out labels for all qnodes
time gzcat $input_path/$node_file | cut -d$'\t' -f 1,2 | gzip >$input_path/labels.tsv.gz

# sort labels file by qnodes
cat $input_path/labels.tsv.gz ../covid/covid_kg_new_properties.tsv.gz >$input_path/labels_covid.tsv.gz
time gzcat $input_path/labels_covid.tsv.gz | tail -n +2 | LANG=C gsort -t $'\t' -S 5G --parallel=4 --key=1,1 | gzip >>$input_path/labels_sorted_temp.tsv.gz
gzcat $input_path/labels_covid.tsv.gz | head -n 1 | gzip >$input_path/labels_header.tsv.gz
cat $input_path/labels_header.tsv.gz $input_path/labels_sorted_temp.tsv.gz >$input_path/labels_sorted.tsv.gz
rm $input_path/labels_header.tsv.gz
rm $input_path/labels_sorted_temp.tsv.gz
