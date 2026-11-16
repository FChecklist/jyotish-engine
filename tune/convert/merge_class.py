"""Validate and merge AI classification outputs. Usage: python merge_class.py INDIR OUT.jsonl
Each cNNNN.out.jsonl must cover exactly the ids in cNNNN.in.jsonl. Bad rows are dropped and listed (never silently kept)."""
import sys, os, json, glob, collections
CLS = {'needs_feature', 'runnable_vocab', 'definition', 'remedy_advice', 'timing', 'commentary', 'duplicate_of', 'unclear'}
FEAT = {'lalkitab_state', 'jaimini', 'dasha_other', 'divisional', 'tajika', 'dosha', 'upagraha', 'nodes_eclipse', 'house_strength', 'benefic_malefic_strength', 'panchang', 'transit', 'nakshatra', 'yoga_named', 'ashtakavarga', 'kp', 'prasna', 'muhurta', 'numerology', 'remedy_db', 'other'}
VERD = {'agrees', 'partly', 'differs', 'not_found'}
def check(r, ids):
    if r.get('id') not in ids: return 'id not in batch'
    if r.get('cls') not in CLS: return 'bad cls'
    if not isinstance(r.get('needs'), list) or any(x not in FEAT for x in r['needs']): return 'bad needs'
    if r['cls'] == 'needs_feature' and not r['needs']: return 'needs_feature without needs'
    for k in ('meaning', 'inference'):
        if not isinstance(r.get(k), str): return 'no ' + k
    if r['cls'] != 'unclear' and len(r['meaning'].strip()) < 8: return 'empty meaning'
    if not isinstance(r.get('variants'), list) or not all(isinstance(v, str) for v in r['variants']): return 'bad variants'
    w = r.get('web')
    if not isinstance(w, dict) or not isinstance(w.get('checked'), bool) or w.get('verdict') not in VERD or not isinstance(w.get('urls'), list): return 'bad web'
    if any(not (isinstance(u, str) and u.startswith('https://')) for u in w['urls']): return 'bad url'
    if w['checked'] and w['verdict'] != 'not_found' and not w['urls']: return 'verdict without url'
    if r.get('conf') not in ('low', 'med', 'high'): return 'bad conf'
    return None
src, out = sys.argv[1], sys.argv[2]; good = {}; bad = collections.Counter(); missing = 0
for fi in sorted(glob.glob(src + '/c*.in.jsonl')):
    ids = {json.loads(l)['id'] for l in open(fi) if l.strip()}; fo = fi.replace('.in.', '.out.')
    if not os.path.exists(fo): continue
    seen = set()
    for l in open(fo):
        try: r = json.loads(l)
        except Exception: bad['json'] += 1; continue
        e = check(r, ids)
        if e or r['id'] in seen: bad[e or 'duplicate'] += 1; continue
        seen.add(r['id']); good[r['id']] = {k: r[k] for k in ('id', 'cls', 'needs', 'meaning', 'inference', 'variants', 'web', 'conf')}
        if r['cls'] == 'duplicate_of' and isinstance(r.get('dup'), str): good[r['id']]['dup'] = r['dup']
    missing += len(ids - seen)
with open(out, 'w') as f:
    for r in good.values(): f.write(json.dumps(r) + '\n')
print(len(good), 'kept; dropped', dict(bad), '; ids missing from outputs', missing)
print('cls', dict(collections.Counter(r['cls'] for r in good.values())))
print('web checked', sum(r['web']['checked'] for r in good.values()), 'needs', dict(collections.Counter(x for r in good.values() for x in r['needs']).most_common(8)))
