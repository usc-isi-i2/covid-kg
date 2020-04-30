import os
import json
from typing import List
from dotenv import load_dotenv

load_dotenv('shell_scripts/covid.env')
ctd_gene_header_dict = {
    0: 'GeneSymbol',
    1: 'label',
    2: 'P351',  # entrez gene id
    3: 'AltGeneIDs',
    4: 'aliases',
    5: 'BioGRIDIDs',
    6: 'P7001',  # PharmGKBIDs
    7: 'P352'  # UniProtIDs
}

ctd_gene_dict = json.load(open('{}/ctd_gene_dict.json'.format(os.getenv('covid_kg_path'))))
ctd_disease_dict = json.load(open('{}/ctd_disease_dict.json'.format(os.getenv('covid_kg_path'))))
ctd_chemical_dict = json.load(open('{}/ctd_chemical_dict.json'.format(os.getenv('covid_kg_path'))))


class Gene(object):
    def __init__(self, gene_id, label, aliases, pharma_gkb_ids, uniprot_ids, gene_symbol):
        self.P351 = gene_id
        self.label = label if label.strip() != "" else None
        self.aliases = aliases if aliases.strip() != "" else None
        self.P7001 = pharma_gkb_ids if pharma_gkb_ids.strip() != "" else None
        self.P352 = uniprot_ids if uniprot_ids.strip() != "" else None
        self.gene_symbol = gene_symbol if gene_symbol.strip() != "" else None
        self.qnode = self.create_qnode()
        self.P31 = 'Q7187'

    def create_qnode(self):
        return 'Q00005550-gene-{}'.format(self.P351).replace(':', '')

    def serialize(self):
        _d = {'P31': self.P31}
        aliases = self.aliases
        if aliases:
            aliases = aliases.split('|')

        if self.gene_symbol:
            if aliases:
                aliases.append(self.gene_symbol)
            else:
                aliases = [self.gene_symbol]
        if aliases:
            _d['aliases'] = aliases

        _d['P351'] = self.P351
        if self.P7001:
            _d['P7001'] = self.P7001

        if self.P352:
            _d['P352'] = self.P352
        _d['qnode'] = self.qnode
        if self.label:
            _d['label'] = self.label
        return _d


def create_gene_kg(gene_id):
    if gene_id in ctd_gene_dict:
        o = ctd_gene_dict[gene_id]
        return Gene(o[2], o[1], o[4], o[6], o[7], o[0])
    return None


ctd_chemical_header_dict = {
    0: 'ChemicalName',
    1: 'ChemicalID',
    2: 'CasRN',
    3: 'Definition',
    4: 'ParentIDs',
    5: 'TreeNumbers',
    6: 'ParentTreeNumbers',
    7: 'Synonyms',
    8: 'DrugBankIDs'
}


class Chemical(object):
    def __init__(self, chemical_id, chemical_name, cas_rn, aliases):
        self.P31 = 'Q11344'
        self.P486 = chemical_id
        self.label = chemical_name if chemical_name.strip() != '' else None
        self.P231 = cas_rn if cas_rn.strip() != '' else None
        self.aliases = aliases if aliases.strip() != '' else None
        self.qnode = self.create_qnode()

    def create_qnode(self):
        return 'Q00005550-chemical-{}'.format(self.P486).replace(':', '')

    def serialize(self):
        _d = {'P31': self.P31, 'qnode': self.qnode, 'P486': self.P486}

        if self.label:
            _d['label'] = self.label

        if self.P231:
            _d['P231'] = self.P231

        if self.aliases:
            _d['aliases'] = self.aliases.split('|')
        return _d


def create_chemical_kg(chemical_id):
    if chemical_id.startswith('MESH:'):
        chemical_id = chemical_id[5:]
    if chemical_id in ctd_chemical_dict:
        o = ctd_chemical_dict[chemical_id]
        return Chemical(o[1], o[0], o[2], o[7])
    return None


ctd_disease_header_dict = {
    0: 'DiseaseName',
    1: 'DiseaseID',
    2: 'AltDiseaseIDs',
    3: 'Definition',
    4: 'ParentIDs',
    5: 'TreeNumbers',
    6: 'ParentTreeNumbers',
    7: 'Synonyms',
    8: 'SlimMappings'
}


class Disease(object):
    def __init__(self, disease_name, disease_id, aliases):
        self.P31 = 'Q12136'
        self.label = disease_name if disease_name.strip() != "" else None
        self.P486 = disease_id
        self.aliases = aliases if aliases.strip() != "" else None
        self.qnode = self.create_qnode()

    def create_qnode(self):
        return 'Q00005550-disease-{}'.format(self.P486).replace(':', '')

    def serialize(self):
        _d = {'P31': self.P31, 'qnode': self.qnode, 'P486': self.P486}

        if self.label:
            _d['label'] = self.label

        if self.aliases:
            _d['aliases'] = self.aliases.split('|')
        return _d


def create_disease_kg(disease_id):
    if not disease_id.startswith('MESH:'):
        disease_id = 'MESH:{}'.format(disease_id)
    if disease_id in ctd_disease_dict:
        o = ctd_disease_dict[disease_id]
        return Disease(o[0], o[1], o[7])
    return None


class TextFragment(object):
    def __init__(self, label, qnode, offset, section):
        self.text = label
        self.qnode = qnode
        self.offset = offset
        self.section = section
        self.P31 = 'Q1385610'

    def serialize(self):
        return {
            'P2020012': self.text,
            'qnode': self.qnode,
            'P4153': self.offset,
            'P958': self.section,
            'P31': self.P31
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


class Author(object):
    def __init__(self, first_name, surname, ordinal):
        self.name = '{}, {}'.format(surname, first_name)
        self.ordinal = ordinal

    def serialize(self):
        return {'name': self.name, 'ordinal': self.ordinal}


class ScholarlyArticle(object):
    def __init__(self, title, authors: List[Author], publication_date, pmc_id, pm_id, file_name, doi):
        self.P31 = 'Q13442814'  # instance of
        self.P1476 = title  # title
        self.label = title
        self.P2093 = authors  # author name string
        self.P577 = publication_date  # publication date
        self.P932 = pmc_id
        self.P698 = pm_id
        self.P356 = doi
        self.file_name = file_name
        self.qnode = self.create_qnode()

    def create_qnode(self):
        qnode = None
        if self.P932:
            qnode = 'Q00007770{}'.format(self.P932)
        elif self.P698:
            qnode = 'Q00007770{}'.format(self.P698)
        if ':' in qnode:
            qnode = qnode.replace(':', '')
        return qnode

    def serialize(self):
        _d = {'P31': self.P31, 'label': self.label, 'qnode': self.qnode, 'file_name': self.file_name}
        if self.P577:
            _d['P577'] = self.P577
        if self.P1476:
            _d['P1476'] = self.P1476

        if self.P2093:
            _d['P2093'] = [author.serialize() for author in self.P2093]
        if self.P932:
            _d['P932'] = self.P932
        if self.P698:
            _d['P698'] = self.P698
        if self.P356:
            _d['P356'] = self.P356
        return _d


def create_scholarly_article(paper_json, pmid, pmc_id, file_name):
    published_date = paper_json.get('year')
    passages = paper_json.get('passages', [])
    title = ""
    doi = None
    authors = []
    if not isinstance(passages, list):
        passages = [passages]
    for passage in passages:
        infons = passage.get('infons', None)
        if infons:
            if infons['section'].lower() == 'title':
                doi = infons.get('article-id_doi', None)
                title = passage['text']

                for k in infons:
                    if k.startswith('name_'):
                        authors.append(create_author_kg(k, infons[k]))

                break

    return ScholarlyArticle(title, authors, published_date, pmc_id, pmid, file_name, doi)


def create_author_kg(field, value):
    ordinal = int(field.split('_')[1])
    first_name = ''
    surname = ''
    names = value.split(';')
    for name in names:
        if name.startswith('given-names:'):
            first_name = name.split(':')[1]
        if name.startswith('surname:'):
            surname = name.split(':')[1]
    return Author(first_name, surname, ordinal)
