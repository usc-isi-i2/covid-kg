import json
import gzip
import pandas as pd
from typing import List
from glob import glob


class TextFragment(object):
    def __init__(self, label, qnode, offset, section):
        self.label = label
        self.qnode = qnode
        self.offset = offset
        self.section = section

    def serialize(self):
        return {
            'label': self.label,
            'qnode': self.qnode,
            'P4153': self.offset,
            'P958': self.section,
        }


class Entity(object):
    def __init__(self, offset, length, attributed_to, stated_as, text_fragment: TextFragment, type, qnode):
        self.offset = offset
        self.length = length
        self.attributed_to = attributed_to
        self.stated_as = stated_as
        self.text_fragment = text_fragment
        self.type = type
        self.qnode = qnode

    def serialize(self):
        return {
            'P4153': self.offset,
            'P2043': self.length,
            'P1932': self.stated_as,
            'P2020008': self.attributed_to,
            'P2020001': self.text_fragment.qnode,
            'type': self.type,
            'qnode': self.qnode
        }


class Article(object):
    def __init__(self, qnode, file_name):
        self.qnode = qnode
        self.text_frags = []
        self.entities = []
        self.file_name = file_name

    def add_text_frag(self, text_frag: TextFragment):
        self.text_frags.append(text_frag)

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def serialize(self):
        tfs = []
        ens = []
        s = {}
        for tf in self.text_frags:
            tfs.append(tf.serialize())

        for entity in self.entities:
            ens.append(entity.serialize())

        s['text_fragments'] = tfs
        s['entities'] = ens
        s['qnode'] = self.qnode
        s['file_name'] = self.file_name
        return s


papers = glob('{}/*json'.format('/Users/amandeep/Documents/pmid_abs')) + glob(
    '{}/*json'.format('/Users/amandeep/Documents/pmcid'))

pmc_dict = json.load(gzip.open('covid/pmcid_to_qnode.json.gz'))
pm_dict = json.load(gzip.open('covid/pubmed_to_qnode.json.gz'))

entity_dict = json.load(open('covid/entities_to_qnode.json'))

e_type_to_property_map = {
    'gene': 'P2020002',
    'disease': 'P2020003',
    'chemical': 'P2020004',
    'genus': 'P2020005',
    'strain': 'P2020006',
    'species': 'P2020007'
}


def create_kgtk():
    articles = []
    for paper in papers:
        print(paper)
        file_name = paper.split('/')[-1]
        pj = json.load(open(paper))
        pmcid = pj.get('pmcid', None)
        if pmcid and 'PMC' in pmcid:
            pmcid = pmcid[3:]

        pmid = pj.get('pmid', None)
        if pmid:
            pmid = str(pmid)

        qnode = pmc_dict.get(pmcid, None)
        if not qnode:
            qnode = pm_dict.get(pmid, None)
        if qnode:
            article = Article(qnode, file_name)
            passages = pj.get('passages', [])

            for i in range(len(passages)):
                passage = passages[i]
                t_qnode = '{}-text-{}'.format(qnode, i)
                offset = passage.get('offset')
                label = passage.get('text', '')
                start = 0
                section = passage['infons']['section']
                text_frag = TextFragment(label, t_qnode, offset, section)
                article.add_text_frag(text_frag)
                annotations = passage.get('annotations', [])
                for annotation in annotations:
                    # identifier, type, offset, length, qnode, text_fragment
                    infons = annotation['infons']
                    e_identifier = infons['identifier']
                    e_type = infons['type'].lower()
                    e_offset = annotation['locations'][0]['offset']
                    e_length = annotation['locations'][0]['length']
                    stated_as = annotation['text']
                    if e_identifier:
                        if 'MESH' in e_identifier:
                            e_identifier = e_identifier.split(':')[1]
                        e_qnode = entity_dict.get('{}@{}'.format(e_type, e_identifier), {'qnode': None})['qnode']
                        if e_qnode:
                            entity = Entity(e_offset, e_length, 'http://blender.cs.illinois.edu/', stated_as, text_frag,
                                            e_type, e_qnode)
                            article.add_entity(entity)

            articles.append(article)
    return articles


def create_kgtk_format(articles: List[Article]):
    statements = list()
    qualifiers = list()
    for article in articles:
        a_s = article.serialize()
        qnode = a_s['qnode']
        tfs = a_s['text_fragments']
        entities = a_s['entities']
        file_name = a_s['file_name']

        for i in range(len(entities)):
            entity = entities[i]
            e_node = entity['qnode']
            e_prop = e_type_to_property_map[entity['type']]
            e_edge_id = '{}-{}-{}-{}'.format(qnode, e_prop, file_name, i)
            statements.append({'node1': qnode, 'property': e_prop, 'node2': e_node, 'id': e_edge_id})
            c = 0
            for k in entity:
                if k not in ('qnode', 'type'):
                    qualifiers.append({'node1': e_edge_id, 'property': k, 'node2': entity[k],
                                       'id': '{}-{}'.format(e_edge_id, c)})
                    c += 1

        for i in range(len(tfs)):
            tf = tfs[i]
            t_node = tf['qnode']
            t_edge_id_prop = '{}-{}-{}-{}'.format(qnode, 'P2020001', file_name, i)
            t_label_edge_id = '{}-{}-{}-{}'.format(t_node, 'label', file_name, i)
            statements.append({'node1': qnode, 'property': 'P2020001', 'node2': t_node, 'id': t_edge_id_prop})
            statements.append({'node1': t_node, 'property': 'label', 'node2': tf['label'], 'id': t_label_edge_id})
            c = 0
            for k in tf:
                if k not in ('qnode', 'label'):
                    qualifiers.append({'node1': t_edge_id_prop, 'property': k, 'node2': tf[k],
                                       'id': '{}-{}'.format(t_edge_id_prop, c)})
                    c += 1

    return pd.DataFrame(statements), pd.DataFrame(qualifiers)


statements, qualifiers = create_kgtk_format(create_kgtk())

statements.to_csv('covid/covid_kgtk_statements.tsv', sep='\t', index=False)
qualifiers.to_csv('covid/covid_kgtk_qualifiers.tsv', sep='\t', index=False)
