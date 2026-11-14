import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import rules_norm as N, influence as I, swisseph as swe, charts
p = lambda t, s='': N.parse(t, s)
assert p('Venus dasha')['atoms'] == [('dasha', 5, 'maha')] and p('Venus dasha')['status'] == 'parsed'
assert p('Saturn antardasha')['atoms'] == [('dasha', 6, 'antar')] and p('Rahu bhukti')['atoms'] == [('dasha', 7, 'antar')]
assert p('Jupiter bhukti in Saturn dasha')['atoms'] == [('dasha', 4, 'antar'), ('dasha', 6, 'maha')] or sorted(p('Jupiter bhukti in Saturn dasha')['atoms']) == [('dasha', 4, 'antar'), ('dasha', 6, 'maha')]
assert p('dasha of the 7th lord')['atoms'] == [('dasha_house_lord', 7)] and p('7th lord dasha')['atoms'] == [('dasha_house_lord', 7)]
assert N.evaluate(p('Venus dasha'), {'asc': 0, 'signs': {i: 0 for i in range(9)}}) is None      # no date => not evaluated
inp = (1990, 1, 1, 6, 0, 0, 5.5, 28.6139, 77.209)
c = charts.natal(*inp, factors=(1,))['charts'][1]
pos = {k: v[0] * 30 + v[1] for k, v in c.items() if k != 'asc'}; sg = {k: v[0] for k, v in c.items() if k != 'asc'}
V = I.bundle(swe.julday(1990, 1, 1, 6 - 5.5), 28.6139, 77.209, pos)
assert I.fit(p('Venus dasha'), V, sg) is None                                                  # missing context: never guessed
ctx = {'maha': 5, 'antar': 3}
assert I.fit(p('Venus dasha'), V, sg, ctx) == 1.0 and I.fit(p('Saturn dasha'), V, sg, ctx) == 0.0 and I.fit(p('Mercury antardasha'), V, sg, ctx) == 1.0
# lord-of-house dasha: shares over houses 1..12 of "dasha of the n-th lord" must equal the weight of lord signs; each sign has one lord, so the sum over the 12 houses of the fraction of
# each house ruled by (Venus or Mercury) equals the same fraction summed over every house = number of Venus/Mercury signs counted with house shares (2 signs each, 12 signs total across views)
Vw = I.bundle(swe.julday(1990, 1, 1, 6 - 5.5), 28.6139, 77.209, pos, weights={'d9': 0, 'equal_asc': 0, 'equal_mid': 0, 'sripati': 0, 'porphyry': 0, 'placidus': 0})   # whole-sign view: every house is exactly one sign
tot = sum(I.fit(p(f'dasha of the {h}th lord'), Vw, sg, ctx) for h in range(1, 13))
assert abs(tot - 4.0) < 1e-9, tot       # 4 signs (Taurus, Libra, Gemini, Virgo) ruled by Venus or Mercury, spread over the 12 houses
# combined with a natal atom: both must hold
q = p('Venus dasha and Moon in Aries'); assert q['status'] == 'parsed' and len(q['atoms']) == 2
print('dasha rule tests passed')
