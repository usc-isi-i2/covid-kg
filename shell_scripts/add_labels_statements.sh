source covid.env

cd $covid_kg_path || exit

# first sort by node1
echo "Sorting by node1..."
time cat covid_kgtk_statements.tsv | tail -n +2 | LANG=C gsort -t $'\t' -S 5G --parallel=4 --key=1 >covid_kgtk_statements_sorted_by_node1_temp.tsv
head -n 1 covid_kgtk_statements.tsv >header
cat header covid_kgtk_statements_sorted_by_node1_temp.tsv >covid_kgtk_statements_sorted_by_node1.tsv
rm header
echo "Done!\n"

# join labels for node1
echo "adding labels for node1..."
time mlr --prepipe gunzip --tsvlite --otsv join --ul --lp '' --rp 'node1_' -s -j node1 -l node1 -r id -f covid_kgtk_statements_sorted_by_node1.tsv then unsparsify $input_path/labels_sorted.tsv.gz >covid_kgtk_statements_sorted_by_node1_wlabel.tsv
echo "Done!\n"

# sort by node2
echo "Sorting by node2..."
time cat covid_kgtk_statements_sorted_by_node1_wlabel.tsv | tail -n +2 | LANG=C gsort -t $'\t' -S 5G --parallel=4 --key=3,3 >covid_kgtk_statements_sorted_by_node2_temp.tsv
head -n 1 covid_kgtk_statements_sorted_by_node1_wlabel.tsv >header
cat header covid_kgtk_statements_sorted_by_node2_temp.tsv >covid_kgtk_statements_sorted_by_node2.tsv
rm header
echo "Done!\n"

# join labels for node 2
echo "adding labels for node2..."
time mlr --prepipe gunzip --tsvlite --otsv join --ul --lp '' --rp 'node2_' -s -j node2 -l node2 -r id -f covid_kgtk_statements_sorted_by_node2.tsv then unsparsify $input_path/labels_sorted.tsv.gz >covid_kgtk_statements_sorted_by_node2_wlabel.tsv
echo "Done!\n"

# sort by property
echo "Sorting by property..."
time cat covid_kgtk_statements_sorted_by_node2_wlabel.tsv | tail -n +2 | LANG=C gsort -t $'\t' -S 5G --parallel=4 --key=2,2 >covid_kgtk_statements_sorted_by_property_temp.tsv
head -n 1 covid_kgtk_statements_sorted_by_node2_wlabel.tsv >header
cat header covid_kgtk_statements_sorted_by_property_temp.tsv >covid_kgtk_statements_sorted_by_property.tsv
rm header
echo "Done!\n"

# join labels for property
echo "adding labels for property..."
time mlr --prepipe gunzip --tsvlite --otsv join --ul --lp '' --rp 'property_' -s -j property -l property -r id -f covid_kgtk_statements_sorted_by_property.tsv then unsparsify $input_path/labels_sorted.tsv.gz >covid_kgtk_statements_sorted_by_property_wlabel.tsv
mv covid_kgtk_statements_sorted_by_property_wlabel.tsv covid_kgtk_statements_with_labels_order.tsv
mlr --itsv --otsv reorder -f node1 covid_kgtk_statements_with_labels_order.tsv >covid_kgtk_statements_with_labels.tsv
echo "Done!\n"

rm covid_kgtk_statements_sorted_by_node1.tsv
rm covid_kgtk_statements_sorted_by_node1_temp.tsv
rm covid_kgtk_statements_sorted_by_node1_wlabel.tsv
rm covid_kgtk_statements_sorted_by_node2_temp.tsv
rm covid_kgtk_statements_sorted_by_node2.tsv
rm covid_kgtk_statements_sorted_by_node2_wlabel.tsv
rm covid_kgtk_statements_sorted_by_property_temp.tsv
rm covid_kgtk_statements_sorted_by_property.tsv
rm covid_kgtk_statements_with_labels_order.tsv
rm covid_kgtk_statements.tsv

echo "compressing statements file..."
time gzip -f covid_kgtk_statements_with_labels.tsv
echo "Done!"

echo "compressing qualifiers file..."
time gzip -f covid_kgtk_qualifiers.tsv
echo "Done!"