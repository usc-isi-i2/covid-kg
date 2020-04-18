import os
import gzip
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('shell_scripts/covid.env')

edges_file = "{}/{}".format(os.getenv('input_path'), os.getenv('edges_file'))
nodes_file = "{}/{}".format(os.getenv('input_path'), os.getenv('node_file'))

all_papers_path = "{}/papers_qnodes_in_corpus.txt".format(os.getenv('covid_kg_path'))

o_dir = "{}/qnode_details".format(os.getenv('covid_kg_path'))
Path(o_dir).mkdir(parents=True, exist_ok=True)

all_papers_f = open(all_papers_path)
all_papers = {}
for line in all_papers_f:
    qnode = line.replace('\n', '')
    all_papers[qnode] = 1

annotations_entities_path = "{}/entities_to_qnode.json".format(os.getenv('covid_kg_path'))
annotations = json.load(open(annotations_entities_path))

qnodes_annotations = {}
for k in annotations:
    qnodes_annotations[annotations[k]['qnode']] = 1

paper_file = open('{}/papers_wikidata.tsv'.format(o_dir), 'w')
paper_file.write('{}\t{}\t{}\t{}\n'.format('id', 'node1', 'property', 'node2'))

annotations_file = open('{}/annotations_wikidata.tsv'.format(o_dir), 'w')
annotations_file.write('{}\t{}\t{}\t{}\n'.format('id', 'node1', 'property', 'node2'))

f = gzip.open(edges_file)
i = 0
for line in f:
    if i % 10000 == 0:
        print(i)
    line = line.decode('utf-8')
    qnode = line.split('\t')[1]
    if qnode in all_papers:
        paper_file.write(line)
    if qnode in qnodes_annotations:
        annotations_file.write(line)
    i += 1

f.close()

f = gzip.open(nodes_file)
i = 0
for line in f:
    if i % 10000 == 0:
        print(i)
    line = line.decode('utf-8')
    vals = line.split('\t')
    qnode = vals[0]
    edge_id = '{}-label-1'.format(qnode)
    if qnode in all_papers:
        paper_file.write('{}\t{}\t{}\t{}\n'.format(edge_id, qnode, 'label', vals[1]))
    if qnode in qnodes_annotations:
        annotations_file.write('{}\t{}\t{}\t{}\n'.format(edge_id, qnode, 'label', vals[1]))
    i += 1
f.close()

print('Done')
