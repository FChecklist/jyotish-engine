"""Build the full-run batches: unread rules (partial or unparsed) that mention a chart-condition word. Blind files hold only id, system, input.
Usage: python make_batches.py OUTDIR BATCH_SIZE RULEGLOB..."""
import sys, os, re, json, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
import apply_rules, rules_norm as N, atoms_store
KEY = re.compile(r'\b(sun|moon|mars|mercury|jupiter|venus|saturn|rahu|ketu|lagna|ascendant|\d{1,2}(?:st|nd|rd|th)|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|house|bhava|lord|kendra|trikona|dasha|dasa|bhukti|antardasha|yoga|aspect|conjunct|nakshatra|retrograde|combust|exalted|debilitated|own sign|aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces)\b', re.I)
out, size = sys.argv[1], int(sys.argv[2]); os.makedirs(out, exist_ok=True)
rows = apply_rules.load(sys.argv[3:]); done, _ = atoms_store.load('/home/claude/jyotish-code/rules/atoms_ai_v*.jsonl')
todo = []
for r in rows:
    if r['id'] in done: continue
    if N.parse(r['input'], r['system'])['status'] == 'parsed': continue
    if len(r['input']) > 12 and KEY.search(r['input']): todo.append(r)
random.Random(1).shuffle(todo)
for k in range(0, len(todo), size):
    with open(f'{out}/b{k // size + 1:04d}.in.jsonl', 'w') as f:
        for r in todo[k:k + size]: f.write(json.dumps({'id': r['id'], 'system': r['system'], 'input': r['input']}) + '\n')
print(len(rows), 'rules;', len(todo), 'to convert;', (len(todo) + size - 1) // size, 'batches of', size)
