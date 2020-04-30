import os
import gzip
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('shell_scripts/covid.env')

edges_file = "{}/{}".format(os.getenv('input_path'), os.getenv('edges_file'))
nodes_file = "{}/{}".format(os.getenv('input_path'), os.getenv('node_file'))
qualifiers_file = "{}/{}".format(os.getenv('input_path'), os.getenv('qualifiers_file'))

all_papers_path = "{}/papers_qnodes_in_corpus.txt".format(os.getenv('covid_kg_path'))

o_dir = os.getenv('covid_kg_path')
Path(o_dir).mkdir(parents=True, exist_ok=True)

all_papers_f = open(all_papers_path)
all_papers = {}
for line in all_papers_f:
    qnode = line.replace('\n', '').strip()
    all_papers[qnode] = 1

annotations_entities_path = "{}/entities_to_qnode.json".format(os.getenv('covid_kg_path'))
annotations = json.load(open(annotations_entities_path))

qnodes_annotations = {}
for k in annotations:
    qnodes_annotations[annotations[k]['qnode'].strip()] = 1

paper_file_path = Path('{}/papers_wikidata_kgtk.tsv'.format(o_dir))
if paper_file_path.is_file():
    paper_file = open(paper_file_path, 'a')
else:
    paper_file = open(paper_file_path, 'w')
    paper_file.write('{}\t{}\t{}\t{}\n'.format('id', 'node1', 'property', 'node2'))

annotations_file_path = Path('{}/entities_wikidata_kgtk.tsv'.format(o_dir))
if annotations_file_path.is_file():
    annotations_file = open(annotations_file_path, 'a')
else:
    annotations_file = open(annotations_file_path, 'w')
    annotations_file.write('{}\t{}\t{}\t{}\n'.format('id', 'node1', 'property', 'node2'))

properties_file = open('{}/all_properties.tsv'.format(os.getenv('covid_kg_path')), 'w')
properties_file.write('{}\t{}\t{}\t{}\n'.format('id', 'node1', 'property', 'node2'))

qualifiers_kgtk_file = open('{}/qualifiers_wikidata_kgtk.tsv'.format(os.getenv('covid_kg_path')), 'w')
qualifiers_kgtk_file.write('{}\t{}\t{}\t{}\n'.format('id', 'node1', 'property', 'node2'))

values_dict = {}

f = gzip.open(edges_file)
i = 0
for line in f:
    if i % 1000000 == 0:
        print(i)
    line = line.decode('utf-8').replace('\n', '').replace('\r', '')

    vals = line.split('\t')
    qnode = vals[1].strip()
    id = vals[0]
    property = vals[2]
    value = vals[3].strip()

    if qnode in all_papers:
        paper_file.write('{}\t{}\t{}\t{}\n'.format(id, qnode, property, value))
        if value.startswith('Q'):
            values_dict[value] = 1
    if qnode in qnodes_annotations:
        if value.startswith('Q'):
            values_dict[value] = 1
        annotations_file.write('{}\t{}\t{}\t{}\n'.format(id, qnode, property, value))
    if qnode.startswith('P'):
        properties_file.write('{}\t{}\t{}\t{}\n'.format(id, qnode, property, value))
    i += 1

f.close()

f = gzip.open(nodes_file)
i = 0
for line in f:
    if i % 1000000 == 0:
        print(i)
    line = line.decode('utf-8')
    vals = line.split('\t')
    qnode = vals[0].strip()
    aliases = vals[4].split('|')
    descriptions = vals[3].split('|')
    edge_id_label = '{}-label-1'.format(qnode)

    if qnode in all_papers or qnode in values_dict:
        paper_file.write('{}\t{}\t{}\t{}\n'.format(edge_id_label, qnode, 'label', vals[1]))
    if qnode in qnodes_annotations:
        annotations_file.write('{}\t{}\t{}\t{}\n'.format(edge_id_label, qnode, 'label', vals[1]))

    if qnode.startswith('P'):
        properties_file.write('{}\t{}\t{}\t{}\n'.format(edge_id_label, qnode, 'label', vals[1]))

        for k in range(len(aliases)):
            edge_id_alias = '{}-alias-{}'.format(qnode, k)
            if aliases[k].strip() != '':
                properties_file.write('{}\t{}\t{}\t{}\n'.format(edge_id_alias, qnode, 'aliases', aliases[k]))

        for j in range(len(descriptions)):
            edge_id_description = '{}-description-{}'.format(qnode, j)
            if descriptions[j].strip() != '':
                properties_file.write(
                    '{}\t{}\t{}\t{}\n'.format(edge_id_description, qnode, 'descriptions', descriptions[j]))

    i += 1
f.close()

f = gzip.open(qualifiers_file)
i = 0
for line in f:
    if i % 1000000 == 0:
        print(i)
    line = line.decode('utf-8')
    vals = line.split('\t')
    id = vals[0]
    node = vals[1]
    property = vals[2]
    value = vals[3]
    qnode = id.split('-')[0]

    if qnode in all_papers or qnode in values_dict:
        qualifiers_kgtk_file.write('{}\t{}\t{}\t{}\n'.format(id, node, property, value))
    if qnode in qnodes_annotations:
        qualifiers_kgtk_file.write('{}\t{}\t{}\t{}\n'.format(id, node, property, value))

    i += 1

f.close()

f = gzip.open(edges_file)
i = 0
print(len(list(values_dict)))
for line in f:
    if i % 1000000 == 0:
        print(i)
    line = line.decode('utf-8')

    vals = line.split('\t')
    qnode = vals[1].strip()
    id = vals[0]
    property = vals[2]
    value = vals[3].strip()

    if qnode in values_dict:
        paper_file.write('{}\t{}\t{}\t{}\n'.format(id, qnode, property, value))

    i += 1

f.close()

print('Done')
