import json
import gzip
from glob import glob
from tqdm import tqdm

f = json.load(open('/Volumes/GoogleDrive/Shared drives/KGTK/datasets/covid/KG-Heng/Analysis/type_counts.json'))

d = set()


def create_properties_dict(prop_path):
    """
    # TODO These commands are used to filter rows with specified property from the KGTK Wikidata file
    kgtk filter -p ";P685;" --datatype tsv edges_scholarly_articles_in_subject.tsv > property_p685.tsv
    kgtk filter -p ";P486;" --datatype tsv edges_scholarly_articles_in_subject.tsv > property_p486.tsv
    kgtk filter -p ";P351;" --datatype tsv edges_scholarly_articles_in_subject.tsv > property_p351.tsv
    kgtk filter -p ";P5055;" --datatype tsv edges_scholarly_articles_in_subject.tsv > property_p5055.tsv


    :param prop_path:
    :return:
    """
    f = open(prop_path)
    _ = {}
    for line in f:
        vals = line.split('\t')

        qnode = vals[1]
        val = vals[3].replace("\"", "").replace('\n', '')
        if qnode.startswith('Q'):
            _[val] = {'qnode': qnode, 'property': vals[2], 'value': val}

    return _


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

    p685_dict = create_properties_dict('{}/property_p685.tsv'.format(f_path))
    p351_dict = create_properties_dict('{}/property_p351.tsv'.format(f_path))
    p486_dict = create_properties_dict('{}/property_p486.tsv'.format(f_path))
    p5055_dict = create_properties_dict('{}/property_p5055.tsv'.format(f_path))
    print(p685_dict)

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
                # print(i, property)
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

    print(len(no_go))
    for k in not_found:
        print(k, len(not_found[k]))
    for k in found:
        print(k, len(found[k]))
    open('covid/entities_to_qnode.json', 'w').write(json.dumps(result))
    open('covid/entities_not_found.json', 'w').write(json.dumps(no_go))

    for k in type_to_qnode_dict:
        open('covid/{}_qnodes.txt'.format(k), 'w').write('\n'.join(list(type_to_qnode_dict[k])))


def create_pubmedid_to_qnode(f_path):
    """
    # TODO This command filters rows mentioning PMCIds and pub med ids.
    kgtk filter -p ";P698,P932;" --datatype tsv edges_scholarly_articles_in_subject.tsv > property_pubmeds.tsv
    :return:
    """

    f = open('{}/property_pubmeds.tsv'.format(f_path))
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

    gzip.open('covid/pubmed_to_qnode.json.gz', 'w').write(bytes(json.dumps(pubmed_dict), encoding='utf-8'))
    gzip.open('covid/pmcid_to_qnode.json.gz', 'w').write(bytes(json.dumps(pmcid_dict), encoding='utf-8'))


def pubmed_analysis():
    """
    find out which papers in the corpus are not in Wikidata
    :return:
    """
    pmcid_path = '/Users/amandeep/Documents/pmcid'
    pubmed_path = '/Users/amandeep/Documents/pmid_abs'

    pmc_dict = json.load(gzip.open('covid/pmcid_to_qnode.json.gz'))
    pm_dict = json.load(gzip.open('covid/pubmed_to_qnode.json.gz'))

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
    open('covid/papers_in_wikidata_with_both_ids.txt', 'w').write('\n'.join(both))
    open('covid/papers_in_wikidata_with_pmc_ids.txt', 'w').write('\n'.join(pmc_only))
    open('covid/papers_in_wikidata_with_pm_ids.txt', 'w').write('\n'.join(pm_only))
    open('covid/papers_not_found_in_wikidata.txt', 'w').write('\n'.join(not_found))
    open('covid/papers_qnodes_in_corpus.txt', 'w').write('\n'.join(list(qnodes)))


def ctd_diseases():
    f_path = '/Volumes/GoogleDrive/Shared drives/KGTK/datasets/covid/CTD_diseases.tsv'
    f = open(f_path)
    i = 0
    disease_dict = {}
    for line in f:
        if i < 29:
            i += 1
            continue
        line = line.split('\t')
        if len(line) > 1:
            disease_id = line[1]

            disease_dict[disease_id] = line

    open('covid/ctd_disease_dict.json', 'w').write(json.dumps(disease_dict))


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

    open('covid/ctd_gene_dict.json', 'w').write(json.dumps(gene_dict))


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
    open('covid/ctd_chemical_dict.json', 'w').write(json.dumps(chemical_dict))


def create_qnodes_list_ron():
    d = json.load(gzip.open('covid/pmcid_to_qnode.json.gz'))
    print(len(d.values()))
    # print(d.values())


# link_entities_in_covid_data('/Users/amandeep/Documents/covid_data')
# create_pubmedid_to_qnode('/Users/amandeep/Documents/covid_data')
