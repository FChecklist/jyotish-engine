"""Batches of not-yet-converted rules whose text matches a keyword regex AND a chart-condition word. Usage: python make_batches_kw.py OUTDIR BATCH_SIZE REGEX RULEGLOB...  (blind files: id, system, input)."""
import sys, os, re, json, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
import apply_rules, rules_norm as N, atoms_store
out, size, rx = sys.argv[1], int(sys.argv[2]), re.compile(sys.argv[3], re.I); os.makedirs(out, exist_ok=True)
KEY = re.compile(r'\b(sun|moon|mars|mercury|jupiter|venus|saturn|rahu|ketu|lagna|ascendant|house|lord|bhava|\d{1,2}(?:st|nd|rd|th)|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)\b', re.I)
rows = apply_rules.load(sys.argv[4:]); done, _ = atoms_store.load('/home/claude/jyotish-code/rules/atoms_ai_v*.jsonl')
todo = [r for r in rows if r['id'] not in done and N.parse(r['input'], r['system'])['status'] != 'parsed' and len(r['input']) > 12 and rx.search(r['input']) and KEY.search(r['input'])]
random.Random(7).shuffle(todo)
for k in range(0, len(todo), size):
    with open(f'{out}/b{k // size + 1:04d}.in.jsonl', 'w') as f:
        for r in todo[k:k + size]: f.write(json.dumps({'id': r['id'], 'system': r['system'], 'input': r['input']}) + '\n')
print(len(todo), 'rules,', (len(todo) + size - 1) // size, 'batches')
