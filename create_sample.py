import gzip

# f = gzip.open('/Users/amandeep/Github/covid-kg/covid/Heng_kgtk_corpus.tsv.gz')
f = open('/Users/amandeep/Github/covid-kg/covid/Heng_kgtk_corpus_v2.tsv')

s_qnode = ('Q00007770PMC6369310', 'Q41924690')
values = list()
result = open('/Users/amandeep/Github/covid-kg/covid/kgtk_sample.tsv', 'w')
result.write('{}\t{}\t{}\t{}\n'.format('node1', 'property', 'node2', 'id'))
seen = {}
seen_2 = {}
for line in f:
    # line = line.decode('utf-8')
    line = line
    vals = line.split('\t')
    qnode = vals[0]
    prop = vals[1]
    value = vals[2]
    id = vals[3].replace('\n', '').replace('\r', '')

    if s_qnode[0] in id or s_qnode[1] in id:
        if id not in seen_2:
            result.write(line)
            seen_2[id] = 1
        if value.startswith('Q'):
            if value not in seen:
                print(value)
                seen[value] = 1
                values.append(value)

sorted_values = sorted(values, reverse=True)
f.close()

print(len(sorted_values))

# f = gzip.open('/Users/amandeep/Github/covid-kg/covid/Heng_kgtk_corpus.tsv.gz')
f = open('/Users/amandeep/Github/covid-kg/covid/Heng_kgtk_corpus_v2.tsv')
for line in f:
    vals = line.split('\t')
    qnode = vals[0]
    prop = vals[1]
    value = vals[2]
    id = vals[3].replace('\n', '').replace('\r', '')
    if any(x in id for x in sorted_values):
        if id not in seen_2:
            print('First: {}'.format(id))
            seen_2[id] = 1
            result.write(line)
f.close()
print('Done')

# time cat kgtk_sample.tsv | tail -n +2 | LANG=C gsort -t $'\t' -S 5G --parallel=4 --key=4 > kgtk_sample_temp.tsv
# head -n 1 kgtk_sample.tsv > header
# cat header kgtk_sample_temp.tsv > kgtk_sample_sorted.tsv
# rm header
# rm kgtk_sample_temp
