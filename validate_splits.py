f = open('covid/Heng_kgtk_corpus_v2.tsv')
_ = {}
for line in f:
    line = line.strip()
    vals = line.split('\t')
    id = vals[3]
    _[id] = 1

sp = 'covid/heng_split'

import glob

count = 0
for g in glob.glob('{}/*tsv'.format(sp)):
    t = open(g)
    for line in t:
        id = line.strip().split('\t')[3]
        if id not in _:
            count += 1
            print(id)

print(count)
