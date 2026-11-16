"""Batches of NOT-executable rules for AI classification. Usage: python make_batches_classify.py OUTDIR BATCH_SIZE RULEGLOB...
Groups by (system, life_area) so concepts cluster. Skips ids already in classified_v*.jsonl."""
import sys, os, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
import apply_rules, rules_norm as N, atoms_store
out, size = sys.argv[1], int(sys.argv[2]); os.makedirs(out, exist_ok=True)
rows = apply_rules.load(sys.argv[3:]); done, _ = atoms_store.load('/home/claude/jyotish-code/rules/atoms_ai_v*.jsonl')
cl = set()
for fn in glob.glob('/home/claude/jyotish-code/rules/classified_v*.jsonl'):
    for l in open(fn):
        if l.strip(): cl.add(json.loads(l)['id'])
todo = [r for r in rows if r['id'] not in done and r['id'] not in cl and N.parse(r['input'], r['system'])['status'] != 'parsed']
todo.sort(key=lambda r: (r.get('system', ''), r.get('life_area', ''), r['id']))
F = ('id', 'system', 'life_area', 'input', 'outcome', 'timing', 'strength_note', 'remedy', 'source')
for k in range(0, len(todo), size):
    with open(f'{out}/c{k // size + 1:04d}.in.jsonl', 'w') as f:
        for r in todo[k:k + size]: f.write(json.dumps({x: r.get(x, '') for x in F}) + '\n')
print(len(todo), 'rules,', (len(todo) + size - 1) // size, 'batches')
