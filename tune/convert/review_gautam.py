"""Flag low-value Gautam rows. Deletes nothing. Writes data/gautam/review_flags.jsonl + counts."""
import json, glob, os, collections
D = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'gautam')
rows = []
for f in sorted(glob.glob(os.path.join(D, 'video*.jsonl'))):
    v = os.path.basename(f)[5:7]
    for line in open(f, encoding='utf-8'):
        line = line.strip()
        if line:
            r = json.loads(line); r['_v'] = v; rows.append(r)
seen = collections.Counter((r.get('says') or '').strip().lower() for r in rows if r.get('type') == 'stmt')
stats = collections.defaultdict(collections.Counter)
out = open(os.path.join(D, 'review_flags.jsonl'), 'w', encoding='utf-8')
for r in rows:
    fl = []
    s = (r.get('says') or '').strip()
    if r.get('type') == 'skip': fl.append('skip')
    else:
        if len(s) < 40: fl.append('short_says')
        if len((r.get('hindi') or '').split()) < 5: fl.append('short_hindi')
        if s and seen[s.lower()] > 1: fl.append('duplicate_says')
        if not (r.get('cells_stated') or r.get('cells_derived_method') or r.get('derived_examples') or r.get('charts')): fl.append('no_rule_content')
        if r.get('confidence') == 'low': fl.append('low_conf')
    st = stats[r['_v']]; st['rows'] += 1
    for x in fl: st[x] += 1
    if any(x != 'skip' for x in fl):
        out.write(json.dumps({'id': r.get('id'), 'flags': fl}) + '\n')
    if len([x for x in fl if x not in ('skip', 'low_conf')]) >= 2: st['multi_flag'] += 1
keys = ['rows','skip','short_says','short_hindi','duplicate_says','no_rule_content','low_conf','multi_flag']
print('video', *keys, sep='\t')
for v in sorted(stats): print(v, *[stats[v][k] for k in keys], sep='\t')
print('TOTAL', *[sum(stats[v][k] for v in stats) for k in keys], sep='\t')
