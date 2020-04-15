import gzip


def validate_file(file_name, num_columns, sep='\t'):
    zipped = False
    if file_name.endswith(".gz"):
        f = gzip.open(file_name)
        zipped = True
    else:
        f = open(file_name)
    for line in f:
        if zipped:
            line = line.decode('utf-8')
        x = line.split(sep)

        try:
            assert len(x) == num_columns
        except:
            print(line)


# validate_file('/Users/amandeep/Github/covid-kg/covid/covid_kgtk_statements_sorted_by_node1_wlabel.tsv', 4)
# validate_file('/Users/amandeep/Github/covid-kg/covid/covid_kgtk_statements_sorted_by_property_wlabel.tsv', 6)
validate_file('/Users/amandeep/Documents/covid_data/labels_sorted_temp.tsv.gz', 2)
