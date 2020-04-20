import os
import json
import gzip
from glob import glob
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv('shell_scripts/covid.env')
f = json.load(open('/Volumes/GoogleDrive/Shared drives/KGTK/datasets/covid/KG-Heng/Analysis/type_counts.json'))

d = set()


def create_properties_dict(prop_path):
    p685_dict = {}
    p351_dict = {}
    p486_dict = {}
    p5055_dict = {}
    f = open(prop_path)
    for line in f:
        vals = line.split('\t')

        qnode = vals[1]
        val = vals[3].replace("\"", "").replace('\n', '')
        property = vals[2]

        if qnode.startswith('Q'):
            if property == 'P685':
                p685_dict[val] = {'qnode': qnode, 'property': property, 'value': val}

            elif property == 'P351':
                p351_dict[val] = {'qnode': qnode, 'property': property, 'value': val}

            elif property == 'P486':
                p486_dict[val] = {'qnode': qnode, 'property': property, 'value': val}

            elif property == 'P5055':
                p5055_dict[val] = {'qnode': qnode, 'property': property, 'value': val}

    return p685_dict, p351_dict, p486_dict, p5055_dict


def link_entities_in_covid_data(f_path):
    ids_dict = {
        'species': 'P685',
        'strain': 'P685',
        'chemical': 'P486',
        'disease': 'P486',
        'MESH': 'P486',
        'gene': 'P351',
        'genus': 'P5055'
    }

    p685_dict, p351_dict, p486_dict, p5055_dict = create_properties_dict('{}/pubmed_properties.tsv'.format(f_path))

    type_dict = {
        'P685': p685_dict,
        'P486': p486_dict,
        'P351': p351_dict,
        'P5055': p5055_dict
    }
    result = {}
    no_go = list()
    not_found = dict()
    type_to_qnode_dict = {}
    found = dict()
    for tup in f:
        id_str = tup[0]
        vals = id_str.split('@')
        type = vals[0]
        property = ids_dict.get(type)
        identifiers = vals[1]

        if 'MESH' in identifiers:
            identifier = [identifiers.split(':')[1]]
        elif ';' in identifiers:
            identifier = identifiers.split(';')
        else:
            identifier = [identifiers]
        for i in identifier:
            if property in type_dict:
                if i in type_dict[property]:
                    if type not in type_to_qnode_dict:
                        type_to_qnode_dict[type] = set()
                    type_to_qnode_dict[type].add(type_dict[property][i]['qnode'])
                    result['{}@{}'.format(type, i)] = type_dict[property][i]
                    if type not in found:
                        found[type] = set()
                    found[type].add(i)

                else:
                    no_go.append({'type': type, 'str': id_str, 'reason': 'not found in wikidata'})
                    if type not in not_found:
                        not_found[type] = set()
                    not_found[type].add(i)
            else:
                no_go.append({'type': type, 'str': id_str, 'reason': 'property unknown'})
                if type not in not_found:
                    not_found[type] = set()
                not_found[type].add(i)

    open('{}/entities_to_qnode.json'.format(os.getenv('covid_kg_path')), 'w').write(json.dumps(result))
    open('{}/entities_not_found.json'.format(os.getenv('covid_kg_path')), 'w').write(json.dumps(no_go))

    for k in type_to_qnode_dict:
        open('{}/{}_qnodes.txt'.format(os.getenv('covid_kg_path'), k), 'w').write(
            '\n'.join(list(type_to_qnode_dict[k])))


def create_pubmedid_to_qnode(f_path):
    f = open('{}/pubmed_properties.tsv'.format(f_path))
    pubmed_dict = {}
    pmcid_dict = {}
    for line in f:
        vals = line.split('\t')
        qnode = vals[1]
        property = vals[2]
        pid = vals[3].replace("\"", "").replace('\n', '')
        if property == 'P698':
            pubmed_dict[pid] = qnode
        if property == 'P932':
            pmcid_dict[pid] = qnode

    gzip.open('{}/pubmed_to_qnode.json.gz'.format(os.getenv('covid_kg_path')), 'w').write(
        bytes(json.dumps(pubmed_dict), encoding='utf-8'))
    gzip.open('{}/pmcid_to_qnode.json.gz'.format(os.getenv('covid_kg_path')), 'w').write(
        bytes(json.dumps(pmcid_dict), encoding='utf-8'))


def pubmed_analysis():
    """
    find out which papers in the corpus are not in Wikidata
    :return:
    """
    pmcid_path = os.getenv('pmc_path')
    pubmed_path = os.getenv('pm_path')

    pmc_dict = json.load(gzip.open('{}/pmcid_to_qnode.json.gz'.format(os.getenv('covid_kg_path'))))
    pm_dict = json.load(gzip.open('{}/pubmed_to_qnode.json.gz'.format(os.getenv('covid_kg_path'))))

    both = []
    pmc_only = []
    pm_only = []
    not_found = []

    qnodes = set()

    for f in tqdm(glob('{}/*json'.format(pmcid_path)) + glob('{}/*json'.format(pubmed_path))):

        x = json.load(open(f))
        f_name = f.split('/')[-1]
        pmcid = x.get('pmcid', None)
        if pmcid and 'PMC' in pmcid:
            pmcid = pmcid[3:]

        pmid = x.get('pmid', None)
        if pmid:
            pmid = str(pmid)

        if pmcid in pmc_dict and pmid in pm_dict:
            qnodes.add(pmc_dict[pmcid])
            qnodes.add(pm_dict[pmid])
            both.append(f_name)

        elif pmid in pm_dict:
            qnodes.add(pm_dict[pmid])
            pm_only.append(f_name)
        elif pmcid in pmc_dict:
            qnodes.add(pmc_dict[pmcid])
            pmc_only.append(f_name)

        else:
            not_found.append(f_name)

    print('both: {}'.format(len(both)))
    print('pmc only: {}'.format(len(pmc_only)))
    print('pm only: {}'.format(len(pm_only)))
    print('not found: {}'.format(len(not_found)))
    open('{}/papers_in_wikidata_with_both_ids.txt'.format(os.getenv('covid_kg_path')), 'w').write('\n'.join(both))
    open('{}/papers_in_wikidata_with_pmc_ids.txt'.format(os.getenv('covid_kg_path')), 'w').write('\n'.join(pmc_only))
    open('{}/papers_in_wikidata_with_pm_ids.txt'.format(os.getenv('covid_kg_path')), 'w').write('\n'.join(pm_only))
    open('{}/papers_not_found_in_wikidata.txt'.format(os.getenv('covid_kg_path')), 'w').write('\n'.join(not_found))
    open('{}/papers_qnodes_in_corpus.txt'.format(os.getenv('covid_kg_path')), 'w').write('\n'.join(list(qnodes)))


def ctd_diseases():
    f_path = '/Volumes/GoogleDrive/Shared drives/KGTK/datasets/covid/CTD_diseases.tsv.gz'
    f = gzip.open(f_path)
    i = 0
    disease_dict = {}
    for line in f:
        if i < 29:
            i += 1
            continue
        line = line.decode('utf-8').replace('\n', '')
        line = line.split('\t')
        if len(line) > 1:
            disease_id = line[1]

            disease_dict[disease_id] = line

    open('{}/ctd_disease_dict.json'.format(os.getenv('covid_kg_path')), 'w').write(json.dumps(disease_dict))


def ctd_genes():
    f_path = '/Volumes/GoogleDrive/Shared drives/KGTK/datasets/covid/CTD_genes.tsv.gz'
    f = gzip.open(f_path)
    i = 0
    gene_dict = {}
    for line in f:
        line = line.decode('utf-8').replace('\n', '')
        if i < 29:
            i += 1
            continue

        line = line.split('\t')
        if len(line) > 1:
            gene_id = line[2]

            gene_dict[gene_id] = line

    open('{}/ctd_gene_dict.json'.format(os.getenv('covid_kg_path')), 'w').write(json.dumps(gene_dict))


def ctd_chemicals():
    f_path = '/Volumes/GoogleDrive/Shared drives/KGTK/datasets/covid/CTD_chemicals.tsv.gz'
    f = gzip.open(f_path)
    i = 0
    chemical_dict = {}
    for line in f:
        line = line.decode('utf-8').replace('\n', '')
        if i < 29:
            i += 1
            continue

        line = line.split('\t')
        if len(line) > 1:
            chemical_id = line[1]
            if 'MESH:' in chemical_id:
                chemical_id = chemical_id[5:]

            chemical_dict[chemical_id] = line
    open('{}/ctd_chemical_dict.json'.format(os.getenv('covid_kg_path')), 'w').write(json.dumps(chemical_dict))


print('Entity resolving the annotations...')
link_entities_in_covid_data(os.getenv('input_path'))
print('Done!')

print('Creating pubmed ids to qnodes...')
create_pubmedid_to_qnode(os.getenv('input_path'))
print('Done!')

print('Creating helper files...')
pubmed_analysis()
print('Done!')

print('pre processing CTD data...')
ctd_genes()
ctd_diseases()
ctd_chemicals()
print('Done!')
