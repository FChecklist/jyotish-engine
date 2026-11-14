import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import swisseph as swe, influence as I, rules_norm as N, charts
inp = (1990, 1, 1, 6, 0, 0, 5.5, 28.6139, 77.209)
c = charts.natal(*inp, factors=(1,))['charts'][1]
pos = {k: v[0] * 30 + v[1] for k, v in c.items() if k != 'asc'}
sgn = {k: v[0] for k, v in c.items() if k != 'asc'}
jd = swe.julday(1990, 1, 1, 6 - 5.5)
V = I.bundle(jd, 28.6139, 77.209, pos)
sh = I.house_sign_shares(V)
assert sh[1]['main'] == 'Sagittarius' and 'Scorpio' in sh[1]['minor'], sh[1]             # a main sign plus a minor sign in one house (neutral test chart)
for h, d in sh.items(): assert abs(sum(d["shares"].values()) - 1) < 2e-3, h                  # shares sum to 1
ph = I.planet_house_shares(V)
for p, d in ph.items(): assert abs(sum(d.values()) - 1) < 1e-9, p                             # each planet is somewhere
# rules: fit values and sum properties
f = lambda t, s='': I.fit(N.parse(t, s), V, sgn)
V3 = I.bundle(jd, 28.6139, 77.209, pos, weights={'d9': 0}); g = lambda t: I.fit(N.parse(t), V3, sgn)
assert abs(g('Venus in 2nd house') - 0.8333) < 2e-3 and g('Venus in 9th house') == 0.0   # regression values for the neutral chart, no D9 view
m1, m2 = g('Mars in 1st house'), g('Mars in 12th house'); assert 0 < m1 < 1 and abs(m1 + m2 - 1) < 1e-3, (m1, m2)   # Mars straddles houses 12 and 1 (no D9)
assert abs(sum(f(f'Mars in {h}th house') for h in range(1, 13)) - 1) < 1e-3
for n in range(1, 13): assert abs(sum(f(f'{n}th lord in {h}th house') for h in range(1, 13)) - 1) < 1e-3, n   # a lord is always somewhere
assert f('Saturn in Sagittarius') == 1.0 and f('Jupiter and Venus') == 0.0 and f('Rahu in example') is None
# weights: dropping D9 and non-KP views changes nothing about invariants
V2 = I.bundle(jd, 28.6139, 77.209, pos, weights={'d9': 0, 'whole': 0, 'equal_asc': 0, 'equal_mid': 0, 'sripati': 0, 'porphyry': 0})
assert list(V2) == ['placidus'] and abs(sum(I.fit(N.parse(f'Moon in {h}th house'), V2, sgn) for h in range(1, 13)) - 1) < 1e-9
print('influence tests passed. House 1:', sh[1]['shares'], '| Mercury in 1st', m1, 'in 2nd', m2)
