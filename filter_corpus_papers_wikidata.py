import gzip

edges_file = "/Users/amandeep/Documents/covid_data/wikidata_edges_20200330_truncated.tsv.gz"

all_papers_path = "/Users/amandeep/Github/covid-kg/covid/papers_qnodes_in_corpus.txt"
o_dir = "/Users/amandeep/Github/covid-kg/covid/qnode_details"

all_papers_f = open(all_papers_path)
all_papers = {}
for line in all_papers_f:
    qnode = line.replace('\n', '')
    all_papers[qnode] = 1

f = gzip.open(edges_file)
o_file = open('{}/papers_wikidata.tsv'.format(o_dir), 'w')
i = 0
for line in f:
    if i % 10000 == 0:
        print(i)
    line = line.decode('utf-8')
    qnode = line.split('\t')[1]
    if qnode in all_papers:
        o_file.write(line)
    i += 1

print('Done')
