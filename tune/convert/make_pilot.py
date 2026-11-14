"""Build the pilot sample: GOLD = rules the parser already reads fully (answer known), HARD = rules the parser cannot read. Blind files hold only id, system, input."""
import sys, os, json, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
import apply_rules, rules_norm as N
rows = apply_rules.load(sys.argv[2:]); out = sys.argv[1]; os.makedirs(out, exist_ok=True); rnd = random.Random(2026)
gold, hard = [], []
for r in rows:
    n = N.parse(r['input'], r['system'])
    (gold if n['status'] == 'parsed' else hard if n['status'] in ('partial', 'unparsed') and len(r['input']) > 12 else []).append((r, n))
G = rnd.sample(gold, 150); H = rnd.sample(hard, 150)
def dump(name, items):
    for k in range(0, len(items), 50):
        with open(f'{out}/{name}_{k // 50 + 1}.in.jsonl', 'w') as f:
            for r, _ in items[k:k + 50]: f.write(json.dumps({'id': r['id'], 'system': r['system'], 'input': r['input']}) + '\n')
dump('gold', G); dump('hard', H)
json.dump({r['id']: {'atoms': [list(a) for a in n['atoms']], 'frame': n['frame']} for r, n in G}, open(f'{out}/gold_answers.json', 'w'), default=str)
print(len(G), len(H), 'written to', out)
