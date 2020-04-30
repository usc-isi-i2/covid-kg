import os
import gzip
import pandas as pd
from dotenv import load_dotenv

load_dotenv('shell_scripts/covid.env')

kg_path = os.getenv('covid_kg_path')

statements_f = pd.read_csv('{}/covid_kgtk_statements.tsv'.format(kg_path), sep='\t', dtype=object)
qualifiers_f = pd.read_csv('{}/covid_kgtk_qualifiers.tsv'.format(kg_path), sep='\t', dtype=object)
papers_f = pd.read_csv('{}/papers_wikidata_kgtk.tsv'.format(kg_path), sep='\t', dtype=object)
entities_f = pd.read_csv('{}/entities_wikidata_kgtk.tsv'.format(kg_path), sep='\t', dtype=object)
properties_f = pd.read_csv('{}/all_properties.tsv'.format(kg_path), sep='\t', dtype=object)
wikidata_qualfiers_f = pd.read_csv('{}/qualifiers_wikidata_kgtk.tsv'.format(kg_path), sep='\t', dtype=object)

new_properties = gzip.open('/Users/amandeep/Github/covid-kg/covid_kg_new_properties.tsv.gz')

_ = list()
for line in new_properties:
    line = line.decode('utf-8').replace('\r', '').replace('\n', '')
    vals = line.split('\t')
    qnode = vals[0]
    label = vals[1]
    _.append({'id': '{}-label-1'.format(qnode), 'node1': qnode, 'property': 'label', 'node2': label})
p_df = pd.DataFrame(_)

df = pd.concat([statements_f, qualifiers_f, papers_f, entities_f, wikidata_qualfiers_f, properties_f, p_df],
               ignore_index=True)

df.sort_values(by=['id'], ascending=True, inplace=True)

df.to_csv('{}/Heng_kgtk_corpus_v2.tsv'.format(kg_path), index=False, sep='\t')
