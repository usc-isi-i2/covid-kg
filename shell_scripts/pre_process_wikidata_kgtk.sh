source covid.env

i_file_no_ext=$(echo $edges_file | cut -d'.' -f 1)

# cut the required columns first
echo "Truncating the input edges file..."
time gzcat $input_path/$edges_file | mlr --tsvlite --otsv cut -x -f magnitude,unit,lower,upper,latitude,longitude,precision,calendar,entity-type | gzip >"$input_path/$i_file_no_ext"_truncated.tsv.gz
echo "Finished truncating the edges file!"

# filter out the properties
echo "Filtering out properties related to papers..."
time gzcat "$input_path/$i_file_no_ext"_truncated.tsv.gz | kgtk filter -p ";P685,P486,P351,P5055,P698,P932;" --datatype tsv --subj "node1" --pred "label" --obj "node2" >$input_path/pubmed_properties.tsv
echo "Finished filtering out properties related to papers!"

# filter out labels for all qnodes
echo "Cutting labels from nodes files..."
time gzcat $input_path/$node_file | cut -d$'\t' -f 1,2 | gzip >$input_path/labels.tsv.gz
echo "Finished cutting labels from nodes file!"

# sort labels file by qnodes
echo "Sorting the labels..."
cat $input_path/labels.tsv.gz ../covid/covid_kg_new_properties.tsv.gz >$input_path/labels_covid.tsv.gz
time gzcat $input_path/labels_covid.tsv.gz | tail -n +2 | LANG=C gsort -t $'\t' -S 5G --parallel=4 --key=1,1 | gzip >>$input_path/labels_sorted_temp.tsv.gz
gzcat $input_path/labels_covid.tsv.gz | head -n 1 | gzip >$input_path/labels_header.tsv.gz
cat $input_path/labels_header.tsv.gz $input_path/labels_sorted_temp.tsv.gz >$input_path/labels_sorted.tsv.gz
rm $input_path/labels_header.tsv.gz
rm $input_path/labels_sorted_temp.tsv.gz
rm $input_path/labels_covid.tsv.gz
rm labels.tsv.gz

echo "Finished sorting the labels!"

