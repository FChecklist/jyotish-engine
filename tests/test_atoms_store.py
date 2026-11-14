import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import atoms_store as S, influence as I, swisseph as swe, charts
ok = lambda **k: {'id': 'x', 'complete': True, **k}
assert S.entry(ok(atoms=[{'t': 'planet_in_house', 'p': 'Sun', 'h': [10, 1]}])) == ('x', (('planet_in_house', 0, (1, 10)),))
assert S.entry(ok(atoms=[{'t': 'dignity', 'p': 'Saturn', 's': 'debilitated'}, {'t': 'not', 'of': {'t': 'conj', 'p': 'Saturn', 'q': 'Mars'}}]))[1][1] == ('not', ('conj', 6, 2))
assert S.entry(ok(atoms=[{'t': 'any', 'of': [{'t': 'planet_in_sign', 'p': 'Moon', 'sign': 'Cancer'}, {'t': 'planet_in_sign', 'p': 'Moon', 'sign': 'Taurus'}]}]))[1][0][0] == 'any'
bad = [ok(atoms=[{'t': 'planet_in_house', 'p': 'Pluto', 'h': [1]}]), ok(atoms=[{'t': 'planet_in_house', 'p': 'Sun', 'h': [13]}]), ok(atoms=[{'t': 'dignity', 'p': 'Rahu', 's': 'own'}]),
       ok(atoms=[{'t': 'yoga', 'name': 'raja'}]), ok(atoms=[{'t': 'conj', 'p': 'Sun', 'q': 'Sun'}]), ok(atoms=[{'t': 'any', 'of': [{'t': 'conj', 'p': 'Sun', 'q': 'Moon'}]}]),
       ok(atoms=[]), {'id': 'x', 'complete': False, 'atoms': [{'t': 'conj', 'p': 'Sun', 'q': 'Moon'}]}, ok(atoms=[{'t': 'planet_in_sign', 'p': 'Sun', 'sign': 'Leo '}])]
for b in bad:
    try: S.entry(b); raise SystemExit(f'accepted bad entry {b}')
    except S.Bad: pass
# loader: conflicts dropped, invalid counted
d = tempfile.mkdtemp(); A = {'id': 'r1', 'complete': True, 'atoms': [{'t': 'conj', 'p': 'Sun', 'q': 'Moon'}]}; B = {'id': 'r1', 'complete': True, 'atoms': [{'t': 'conj', 'p': 'Sun', 'q': 'Mars'}]}
C = {'id': 'r2', 'complete': True, 'atoms': [{'t': 'conj', 'p': 'Sun', 'q': 'Moon'}]}
open(d + '/a.jsonl', 'w').write('\n'.join(json.dumps(x) for x in (A, C, bad[0])) + '\n'); open(d + '/b.jsonl', 'w').write('\n'.join(json.dumps(x) for x in (B, C)) + '\n')
m, c = S.load(d + '/*.jsonl'); assert 'r1' not in m and 'r2' in m and c['conflict'] == 1 and c['rejected'] == 1, (m, c)
# engine: any / not give consistent values on a neutral chart
inp = (1990, 1, 1, 6, 0, 0, 5.5, 28.6139, 77.209); c1 = charts.natal(*inp, factors=(1,))['charts'][1]
pos = {k: v[0] * 30 + v[1] for k, v in c1.items() if k != 'asc'}; sg = {k: v[0] for k, v in c1.items() if k != 'asc'}
V = I.bundle(swe.julday(1990, 1, 1, 6 - 5.5), 28.6139, 77.209, pos)
norm = lambda at: {'status': 'parsed', 'atoms': S.entry(ok(atoms=at))[1], 'frame': 'lagna'}
A1 = {'t': 'planet_in_house', 'p': 'Mars', 'h': [1]}; A12 = {'t': 'planet_in_house', 'p': 'Mars', 'h': [12]}
f1, f12 = I.fit(norm([A1]), V, sg), I.fit(norm([A12]), V, sg)
V3 = I.bundle(swe.julday(1990, 1, 1, 6 - 5.5), 28.6139, 77.209, pos, weights={'d9': 0})
assert abs(I.fit(norm([{'t': 'any', 'of': [A1, A12]}]), V3, sg) - 1.0) < 1e-9                                  # without the D9 view, Mars is in 12 or 1 in every view
assert I.fit(norm([{'t': 'any', 'of': [A1, A12]}]), V, sg) >= max(f1, f12)                                      # OR is never below either branch
assert abs(I.fit(norm([{'t': 'not', 'of': A1}]), V, sg) - (1 - f1)) < 1e-9
assert I.fit(norm([{'t': 'dasha', 'p': 'Venus', 'level': 'maha'}]), V, sg) is None                              # date needed, even inside not/any
assert I.fit(norm([{'t': 'not', 'of': {'t': 'dasha', 'p': 'Venus', 'level': 'maha'}}]), V, sg) is None
assert I.fit(norm([{'t': 'any', 'of': [A1, {'t': 'dasha', 'p': 'Venus', 'level': 'maha'}]}]), V, sg) is None
print('atoms_store tests passed')
