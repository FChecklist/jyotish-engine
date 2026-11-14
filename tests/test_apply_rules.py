import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import swisseph as swe, influence as I, apply_rules as A, rules_norm as N, charts
inp = (1990, 1, 1, 6, 0, 0, 5.5, 28.6139, 77.209)
c = charts.natal(*inp, factors=(1,))['charts'][1]
pos = {k: v[0] * 30 + v[1] for k, v in c.items() if k != 'asc'}
sg = {k: v[0] for k, v in c.items() if k != 'asc'}
jd = swe.julday(1990, 1, 1, 6 - 5.5)
V = I.bundle(jd, 28.6139, 77.209, pos)
def row(i, text, system='parashari'):
    return dict(id=i, system=system, engine_role='rule', life_area='x', input=text, outcome='o', timing='', remedy='', source='s', confidence='')
rows = [row('a', 'Saturn in Sagittarius'), row('b', 'Saturn in Leo'), row('c', 'Rahu in example'), row('d', 'Mars in 2nd / Mercury in 2nd / Jupiter in 2nd')]
out = A.apply(rows, V, sg)
ids = [r['id'] for r in out]
assert ids == ['a'], ids                       # fires only the true parsed rule; unparsed/partial/false ones stay out
assert out[0]['fit'] == 1.0 and out[0]['source'] == 's'
# Lal Kitab frame: house = sign number from Aries, so fit is exactly 0 or 1
sat_house = sg['Saturn'] + 1 if 'Saturn' in sg else sg[6] + 1
n = N.parse('Saturn in 4th house', 'lalkitab'); print('frame', n.get('frame'), n['status'])
f = I.fit(n, V, sg)
if n.get('frame') == 'aries_fixed': assert f in (0.0, 1.0) and (f == 1.0) == (sat_house == 4), f
print('apply_rules tests passed')
