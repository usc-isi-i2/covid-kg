import json

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

ctd_gene_dict = json.load(open('/Users/amandeep/Github/covid-kg/covid/ctd_gene_dict.json'))
ctd_disease_dict = json.load(open('/Users/amandeep/Github/covid-kg/covid/ctd_disease_dict.json'))
ctd_chemical_dict = json.load(open('/Users/amandeep/Github/covid-kg/covid/ctd_chemical_dict.json'))


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
        return 'Q00005550-gene-{}'.format(self.P351)

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
        return 'Q00005550-chemical-{}'.format(self.P486)

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
        return 'Q00005550-disease-{}'.format(self.P486)

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
