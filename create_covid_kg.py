import json
import gzip
import pandas as pd
from typing import List
from glob import glob
from create_annotations_kg import create_chemical_kg, create_disease_kg, create_gene_kg


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


class ScholarlyArticle(object):
    def __init__(self, title, authors, publication_date, pmc_id, pm_id, file_name):
        self.P31 = 'Q13442814'  # instance of
        self.P1476 = title  # title
        self.label = title
        self.P2093 = authors  # author name string
        self.P577 = publication_date  # publication date
        self.P932 = pmc_id
        self.P698 = pm_id
        self.file_name = file_name
        self.qnode = self.create_qnode()

    def create_qnode(self):
        qnode = None
        if self.P932:
            qnode = 'Q00007770{}'.format(self.P932)
        elif self.P698:
            qnode = 'Q00007770{}'.format(self.P698)
        return qnode

    def serialize(self):
        _d = {'P31': self.P31, 'label': self.label, 'qnode': self.qnode, 'file_name': self.file_name}
        if self.P577:
            _d['P577'] = self.P577
        if self.P1476:
            _d['P1476'] = self.P1476

        if self.P2093:
            _d['P2093'] = self.P2093
        if self.P932:
            _d['P932'] = self.P932
        if self.P698:
            _d['P698'] = self.P698
        return _d


def create_scholarly_article(paper_json, pmid, pmc_id, file_name):
    authors = paper_json.get('authors')
    published_date = paper_json.get('year')
    passages = paper_json.get('passages', [])
    title = ""
    if not isinstance(passages, list):
        passages = [passages]
    for passage in passages:
        infons = passage.get('infons', None)
        if infons:
            if infons['section'].lower() == 'title':
                title = passage['text']
                break

    return ScholarlyArticle(title, authors, published_date, pmc_id, pmid, file_name)


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
    scholarly_articles = []
    annotation_entities = []
    for paper in papers:
        print(paper)
        file_name = paper.split('/')[-1]
        pj = json.load(open(paper))
        pmcid = None
        full_pmc_id = pj.get('pmcid', None)
        if full_pmc_id and 'PMC' in full_pmc_id:
            pmcid = full_pmc_id[3:]

        pmid = pj.get('pmid', None)
        if pmid:
            pmid = str(pmid)

        qnode = pmc_dict.get(pmcid, None)
        if not qnode:
            qnode = pm_dict.get(pmid, None)
        if not qnode:
            sa = create_scholarly_article(pj, pmid, full_pmc_id, file_name)
            qnode = sa.qnode
            scholarly_articles.append(sa)
        if qnode:
            article = Article(qnode, file_name)
            passages = pj.get('passages', [])

            for i in range(len(passages)):
                passage = passages[i]
                t_qnode = '{}-text-{}'.format(qnode, i)
                offset = passage.get('offset')
                label = passage.get('text', '')
                annotations = passage.get('annotations', [])
                section = passage['infons']['section']
                if len(annotations) > 0:
                    text_frag = TextFragment(label, t_qnode, offset, section)
                    article.add_text_frag(text_frag)

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
                                entity = Entity(e_offset, e_length, 'http://blender.cs.illinois.edu/', stated_as,
                                                text_frag,
                                                e_type, e_qnode)
                                article.add_entity(entity)
                            else:
                                obj = None
                                if e_type == 'disease':
                                    obj = create_disease_kg(e_identifier)
                                elif e_type == 'chemical':
                                    obj = create_chemical_kg(e_identifier)
                                elif e_type == 'gene':
                                    obj = create_gene_kg(e_identifier)

                                if obj:
                                    annotation_entities.append(obj)

            articles.append(article)
    return articles, scholarly_articles, annotation_entities


def create_kgtk_format(articles: List[Article], scholarly_articles: List[ScholarlyArticle], annotation_entities):
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

    for scholarly_article in scholarly_articles:
        sa = scholarly_article.serialize()
        qnode = sa['qnode']
        file_name = sa['file_name']
        i = 0
        for k in sa:
            if k not in ('qnode', 'file_name'):

                if k == 'P2093':
                    authors = sa[k]
                    for author in authors:
                        edge_id = '{}-{}-{}-{}'.format(qnode, k, file_name, i)
                        statements.append({'node1': qnode, 'property': k, 'node2': author, 'id': edge_id})
                        i += 1
                else:
                    edge_id = '{}-{}-{}-{}'.format(qnode, k, file_name, i)
                    statements.append({'node1': qnode, 'property': k, 'node2': sa[k], 'id': edge_id})
                    i += 1

    for obj in annotation_entities:
        o = obj.serialize()
        qnode = o['qnode']
        i = 0
        for k in o:
            if k not in ('qnode'):
                if k == 'aliases':
                    aliases = o[k]
                    for alias in aliases:
                        edge_id = '{}-{}-{}'.format(qnode, k, i)
                        statements.append({'node1': qnode, 'property': k, 'node2': alias, 'id': edge_id})
                        i += 1
                else:
                    edge_id = '{}-{}-{}'.format(qnode, k, i)
                    statements.append({'node1': qnode, 'property': k, 'node2': o[k], 'id': edge_id})
                    i += 1

    return pd.DataFrame(statements), pd.DataFrame(qualifiers)


articles, scholarly_articles, annotation_entities = create_kgtk()
statements, qualifiers = create_kgtk_format(articles, scholarly_articles, annotation_entities)

statements.to_csv('covid/covid_kgtk_statements.tsv', sep='\t', index=False)
qualifiers.to_csv('covid/covid_kgtk_qualifiers.tsv', sep='\t', index=False)
