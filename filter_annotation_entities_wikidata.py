import json
import gzip

annotations_entities_path = "covid/entities_to_qnode.json"
annotations = json.load(open(annotations_entities_path))

qnodes_annotations = {}
for k in annotations:
    qnodes_annotations[annotations[k]['qnode']] = 1

edges_file = "/Users/amandeep/Documents/covid_data/wikidata_edges_20200330_truncated.tsv.gz"

o_dir = "/Users/amandeep/Github/covid-kg/covid/qnode_details"

f = gzip.open(edges_file)
o_file = open('{}/annotations_wikidata.tsv'.format(o_dir), 'w')
o_file.write('{}\t{}\t{}\t{}\n'.format('id', 'node1', 'property', 'node2'))
i = 0
for line in f:
    if i % 10000 == 0:
        print(i)
    line = line.decode('utf-8')
    qnode = line.split('\t')[1]
    if qnode in qnodes_annotations:
        o_file.write(line)
    i += 1

print('Done')