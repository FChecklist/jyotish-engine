"""Merge AI conversion outputs. Usage: python merge_ai.py FULL_DIR OUT.jsonl RULES_GLOB...
Keeps only valid+complete entries whose id is in the input; where pass B exists, keeps only A==B. Reports agreement with the parser on rules it already reads (a free gold check)."""
import sys, os, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
import atoms_store as S, apply_rules, rules_norm as N
import score_pilot as P
d, out = sys.argv[1], sys.argv[2]
rows = {r['id']: r for r in apply_rules.load(sys.argv[3:])}
kept = []; st = dict(lines=0, complete=0, valid=0, bad_id=0, dropped_disagree=0, dup=0)
bad = {}
seen = set()
for pa in sorted(glob.glob(f'{d}/b*.outA.jsonl')):
    pb = pa.replace('.outA.', '.outB.'); B = {e['id']: e for e in P.read(pb)} if os.path.exists(pb) else None
    for e in P.read(pa):
        st['lines'] += 1
        if not e.get('complete'): continue
        st['complete'] += 1
        try: i, at = S.entry(e)
        except Exception as x: bad[str(x)[:40]] = bad.get(str(x)[:40], 0) + 1; continue
        if i not in rows: st['bad_id'] += 1; continue
        if i in seen: st['dup'] += 1; continue
        if B is not None:
            eb = B.get(i)
            if not (eb and eb.get('complete') and P.ai(eb) == P.ai(e)): st['dropped_disagree'] += 1; continue
        seen.add(i); st['valid'] += 1
        kept.append({'id': i, 'atoms': e['atoms'], 'complete': True, 'missing': '', 'origin': 'ai_v2_single_pass' if B is None else 'ai_v2_two_pass_agreed'})
# agreement with parser where parser reads the rule fully
chk = ok = 0; mism = []
for k in kept:
    r = rows[k['id']]; n = N.parse(r['input'], r['system'])
    if n['status'] == 'parsed':
        chk += 1
        want = frozenset(P.canon(P.listify(a)) for a in n['atoms']); got = P.ai(k)
        if got == want: ok += 1
        else: mism.append(k['id'])
with open(out, 'w') as f:
    for k in kept: f.write(json.dumps(k) + '\n')
print(json.dumps(st), bad); print('parser-gold check:', ok, '/', chk, 'exact', 'mismatch ids', mism[:15])
