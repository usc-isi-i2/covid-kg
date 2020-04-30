def isnodeequal(node1, node2):
    if node1.strip() == node2.strip():
        return True
    if node1.strip() in node2.strip() and '-' in node2:
        return True
    return False


f = open('covid/Heng_kgtk_corpus_v2.tsv')

prev = None
lines_to_write = list()
file_number = 0
for line in f:
    line = line.strip()
    vals = line.split('\t')
    node = vals[0]
    if node.startswith('Q') or node.startswith('P'):
        if prev is None:
            prev = node

        if not isnodeequal(prev, node):
            prev = node
            if len(lines_to_write) >= 1000000:
                o = open('covid/heng_split/heng_corpus_split_{}.tsv'.format(file_number), 'w')
                o.write('node1\tproperty\tnode2\tid\n')
                o.write('\n'.join(lines_to_write))

                lines_to_write = list()
                file_number += 1

        lines_to_write.append(line)

if len(lines_to_write) > 0:
    o = open('covid/heng_split/heng_corpus_split_{}.tsv'.format(file_number), 'w')
    o.write('\n'.join(lines_to_write))

    lines_to_write = list()
    file_number += 1
print('Done')
