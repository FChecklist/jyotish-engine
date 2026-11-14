import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import swisseph as swe, influence as I, rules_norm as N, charts
inp = (1975, 8, 24, 5, 39, 4, 5.5, 25.1833, 75.8333)
c = charts.natal(*inp, factors=(1,))['charts'][1]
pos = {k: v[0] * 30 + v[1] for k, v in c.items() if k != 'asc'}
sgn = {k: v[0] for k, v in c.items() if k != 'asc'}
jd = swe.julday(1975, 8, 24, 5 + 39 / 60 + 4 / 3600 - 5.5)
V = I.bundle(jd, 25.1833, 75.8333, pos)
sh = I.house_sign_shares(V)
assert sh[1]['main'] == 'Leo' and 'Cancer' in sh[1]['minor'], sh[1]                       # the user's case
for h, d in sh.items(): assert abs(sum(d["shares"].values()) - 1) < 2e-3, h                  # shares sum to 1
ph = I.planet_house_shares(V)
for p, d in ph.items(): assert abs(sum(d.values()) - 1) < 1e-9, p                             # each planet is somewhere
# rules: fit values and sum properties
f = lambda t, s='': I.fit(N.parse(t, s), V, sgn)
V3 = I.bundle(jd, 25.1833, 75.8333, pos, weights={'d9': 0}); g = lambda t: I.fit(N.parse(t), V3, sgn)
assert g('Moon in 8th house') == 1.0 and g('Moon in 9th house') == 0.0       # without D9 view the Moon is in the 8th in every view
assert abs(f("Moon in 8th house") - 6/7) < 1e-4 or f('Moon in 8th house') == 1.0   # with D9 view one of seven views may differ
m1, m2 = g('Mercury in 1st house'), g('Mercury in 2nd house'); assert 0 < m1 < 1 and abs(m1 + m2 - 1) < 1e-3, (m1, m2)   # Mercury straddles houses 1 and 2 (no D9)
assert abs(sum(f(f'Mercury in {h}th house') for h in range(1, 13)) - 1) < 1e-3
for n in range(1, 13): assert abs(sum(f(f'{n}th lord in {h}th house') for h in range(1, 13)) - 1) < 1e-3, n   # a lord is always somewhere
assert f('Saturn in Cancer') == 1.0 and f('Jupiter and Venus') == 0.0 and f('Rahu in example') is None
# weights: dropping D9 and non-KP views changes nothing about invariants
V2 = I.bundle(jd, 25.1833, 75.8333, pos, weights={'d9': 0, 'whole': 0, 'equal_asc': 0, 'equal_mid': 0, 'sripati': 0, 'porphyry': 0})
assert list(V2) == ['placidus'] and abs(I.fit(N.parse('Moon in 8th house'), V2, sgn) - 1) < 1e-9
print('influence tests passed. House 1:', sh[1]['shares'], '| Mercury in 1st', m1, 'in 2nd', m2)
