papers_path = 'covid/Heng_kgtk_corpus.tsv'

f = open(papers_path)
# papers = list()
papers = set()
for line in f:
    vals = line.replace('\n', '').split('\t')
    if vals[1] == 'P31' and vals[2] == 'Q13442814':
        papers.add(vals[0])


print(len(papers))
