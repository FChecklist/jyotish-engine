"""Atom-conversion batches for rules the classifier marked runnable_vocab and that have no atoms yet. Usage: python make_batches_runv.py OUTDIR BATCH_SIZE RULEGLOB..."""
import sys, os, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
import apply_rules, atoms_store
out, size = sys.argv[1], int(sys.argv[2]); os.makedirs(out, exist_ok=True)
runv = set()
for fn in glob.glob('/home/claude/jyotish-code/rules/classified_v*.jsonl'):
    for l in open(fn):
        if l.strip():
            r = json.loads(l)
            if r['cls'] == 'runnable_vocab': runv.add(r['id'])
done, _ = atoms_store.load('/home/claude/jyotish-code/rules/atoms_ai_v*.jsonl')
todo = [r for r in apply_rules.load(sys.argv[3:]) if r['id'] in runv and r['id'] not in done]
for k in range(0, len(todo), size):
    with open(f'{out}/b{k // size + 1:04d}.in.jsonl', 'w') as f:
        for r in todo[k:k + size]: f.write(json.dumps({'id': r['id'], 'system': r['system'], 'input': r['input']}) + '\n')
print(len(todo), 'runnable rules,', (len(todo) + size - 1) // size, 'batches')
