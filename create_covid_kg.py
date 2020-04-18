import os
import json
import gzip
import pandas as pd
from glob import glob
from typing import List
from dotenv import load_dotenv
from covid_kg_classes import TextFragment, Entity, Article, ScholarlyArticle
from covid_kg_classes import create_chemical_kg, create_disease_kg, create_gene_kg, create_scholarly_article

load_dotenv('shell_scripts/covid.env')

papers = glob('{}/*json'.format(os.getenv('pm_path'))) + glob(
    '{}/*json'.format(os.getenv('pmc_path')))

pmc_dict = json.load(gzip.open('{}/pmcid_to_qnode.json.gz'.format(os.getenv('covid_kg_path'))))
pm_dict = json.load(gzip.open('{}/pubmed_to_qnode.json.gz'.format(os.getenv('covid_kg_path'))))

entity_dict = json.load(open('{}/entities_to_qnode.json'.format(os.getenv('covid_kg_path'))))

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
                        statements.append({'node1': qnode, 'property': k, 'node2': author['name'], 'id': edge_id})
                        # series ordinal for authors
                        statements.append({'node1': edge_id, 'property': 'P1545', 'node2': author['ordinal'],
                                           'id': '{}-1'.format(edge_id)})
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

statements.to_csv('{}/covid_kgtk_statements.tsv'.format(os.getenv('covid_kg_path')), sep='\t', index=False)
qualifiers.to_csv('{}/covid_kgtk_qualifiers.tsv'.format(os.getenv('covid_kg_path')), sep='\t', index=False)
