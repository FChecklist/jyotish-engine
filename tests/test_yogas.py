import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import yogas as Y, rules_norm as N, influence as I, atoms_store as S, swisseph as swe, charts, transit
Z = lambda **k: {p: 0 for p in range(9)} | {int(a[1:]): v for a, v in k.items()}
H1 = {p: 1 for p in range(9)}
# nakshatra: 13d20m each
assert Y.nak_of(0) == 1 and Y.nak_of(13.34) == 2 and Y.nak_of(359.99) == 27 and Y.nak_of(40) == 4 and Y.nak_of(120) == 10
# planet_from counted in signs
assert Y.planet_from(4, 1, Z(p1=3, p4=7), (5,)) and not Y.planet_from(4, 1, Z(p1=3, p4=7), (4,)) and Y.planet_from(4, 1, Z(p1=3, p4=3), (1,))
# combust orbs: Venus 10 (8 retro), Mercury 14 (12 retro), Moon 12
lon = {0: 100.0, 1: 111.0, 3: 113.0, 5: 109.0}
assert Y.combust(1, lon, set()) and not Y.combust(1, {**lon, 1: 113}, set()) and Y.combust(3, lon, set()) and not Y.combust(3, lon, {3})
assert Y.combust(5, lon, set()) and not Y.combust(5, {**lon, 5: 109.0}, {5}) and not Y.combust(0, lon, set())
SP = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9}          # every planet in its own sign: no conjunctions
# yogas on crafted charts (signs): Moon in sign 0
assert Y.yoga('gajakesari', Z(p1=0, p4=3), H1) and Y.yoga('gajakesari', Z(p1=0, p4=0), H1) and not Y.yoga('gajakesari', Z(p1=0, p4=1), H1)
assert Y.yoga('budhaditya', Z(p0=5, p3=5), H1) and not Y.yoga('budhaditya', Z(p0=5, p3=6), H1)
assert Y.yoga('guru_chandala', Z(p4=2, p7=2), H1) and Y.yoga('grahan', {**SP, 0: 9}, H1) and not Y.yoga('grahan', SP, H1) and Y.yoga('grahan', {**SP, 1: 8}, H1)
far = Z(p1=0, p2=4, p3=5, p4=6, p5=7, p6=8)                        # Moon sign 0; Mars..Saturn in signs 4..8: none in 1st, 2nd or 12th from Moon
assert Y.yoga('kemadruma', far, H1) and not Y.yoga('kemadruma', {**far, 2: 1}, H1) and not Y.yoga('kemadruma', {**far, 2: 11}, H1) and not Y.yoga('kemadruma', {**far, 2: 0}, H1)
assert Y.yoga('sunapha', {**far, 2: 1}, H1) and not Y.yoga('sunapha', {**far, 2: 1, 3: 11}, H1) and Y.yoga('duradhara', {**far, 2: 1, 3: 11}, H1) and Y.yoga('anapha', {**far, 2: 11}, H1)
sun = Z(p0=6, p1=0, p2=10, p3=2, p4=3, p5=4, p6=5)                 # Sun in sign 6; Mars in 10 (not 2nd/12th); Saturn in 5 is 12th from Sun
assert Y.yoga('vosi', sun, H1) and not Y.yoga('vesi', sun, H1) and Y.yoga('ubhayachari', {**sun, 3: 7}, H1)
# pancha mahapurusha: Mars own (Aries) in kendra; fails in house 6; Saturn exalted Libra in kendra
assert Y.yoga('ruchaka', Z(p2=0), {**H1, 2: 10}) and not Y.yoga('ruchaka', Z(p2=0), {**H1, 2: 6}) and not Y.yoga('ruchaka', Z(p2=1), {**H1, 2: 10}) and Y.yoga('sasa', Z(p6=6), {**H1, 6: 7})
# parser
p = lambda t, s='': N.parse(t, s)
assert p('Jupiter in 5th from Moon')['atoms'] == [('planet_from', 4, 1, (5,))] and p('Jupiter in 5th from Moon')['status'] == 'parsed'
assert p('Saturn in 2nd, 12th from Sun')['atoms'] == [('planet_from', 6, 0, (2, 12))]
assert p('Moon in Rohini')['atoms'] == [('planet_in_nak', 1, (4,))] and p('Sun in Purva Phalguni nakshatra')['atoms'] == [('planet_in_nak', 0, (11,))]
assert p('Saturn retrograde')['atoms'] == [('retro', 6)] and p('Mercury combust')['atoms'] == [('combust', 3)] and p('Sun retrograde')['status'] == 'unparsed'
assert p('Gajakesari yoga')['atoms'] == [('yoga', 'gajakesari')] and p('Hamsa yoga')['atoms'] == [('yoga', 'hamsa')] and p('Guru Chandala yoga')['atoms'] == [('yoga', 'guru_chandala')]
assert p('Gajakesari yoga with strong Jupiter')['status'] == 'partial'
assert p('Jupiter in 5th from Lagna')['atoms'] == [('planet_in_house', 4, (5,))]            # lagna stays the house frame
# validator
ok = lambda **k: {'id': 'x', 'complete': True, **k}
assert S.entry(ok(atoms=[{'t': 'planet_in_nak', 'p': 'Moon', 'nak': ['Rohini', 'Hasta']}]))[1] == (('planet_in_nak', 1, (4, 13)),)
assert S.entry(ok(atoms=[{'t': 'planet_from', 'p': 'Jupiter', 'ref': 'Moon', 'h': [5]}]))[1] == (('planet_from', 4, 1, (5,)),)
assert S.entry(ok(atoms=[{'t': 'yoga', 'name': 'sasa'}, {'t': 'retro', 'p': 'Saturn'}, {'t': 'combust', 'p': 'Venus'}]))[1][0] == ('yoga', 'sasa')
for bad in ({'t': 'retro', 'p': 'Sun'}, {'t': 'combust', 'p': 'Sun'}, {'t': 'yoga', 'name': 'raja'}, {'t': 'planet_from', 'p': 'Moon', 'ref': 'Moon', 'h': [1]}, {'t': 'planet_in_nak', 'p': 'Moon', 'nak': ['Nowhere']}):
    try: S.entry(ok(atoms=[bad])); raise SystemExit(f'accepted {bad}')
    except S.Bad: pass
# engine on a neutral chart: totals are exact
inp = (1990, 1, 1, 6, 0, 0, 5.5, 28.6139, 77.209); c1 = charts.natal(*inp, factors=(1,))['charts'][1]
pos = {k: v[0] * 30 + v[1] for k, v in c1.items() if k != 'asc'}; sg = {k: v[0] for k, v in c1.items() if k != 'asc'}
V = I.bundle(swe.julday(1990, 1, 1, 6 - 5.5), 28.6139, 77.209, pos)
retro = set(q for q in transit.transit(*inp)['retro'] if q <= 6); ctx = {'lon': pos, 'retro': retro}
tot = sum(I.fit(p(f'Moon in {n}'), V, sg, ctx) for n in ('Ashwini Bharani Krittika Rohini Mrigashira Ardra Punarvasu Pushya Ashlesha Magha Hasta Chitra Swati Vishakha Anuradha Jyeshtha Mula Shravana Dhanishta Shatabhisha Revati'.split()) + ['Purva Phalguni', 'Uttara Phalguni', 'Purva Ashadha', 'Uttara Ashadha', 'Purva Bhadrapada', 'Uttara Bhadrapada'])
assert abs(tot - 1) < 1e-9, tot                                                               # the Moon is in exactly one of 27 nakshatras
assert abs(sum(I.fit(p(f'Jupiter in {h}th from Moon'), V, sg) for h in range(1, 13)) - 1) < 1e-9
assert I.fit(p('Moon in Rohini'), V, sg) is None and I.fit(p('Saturn retrograde'), V, sg) is None            # no context: not evaluated
assert I.fit(p('Mercury combust'), V, sg, {'lon': pos}) is None                                     # retro flags missing: not evaluated
assert I.fit(p('Gajakesari yoga'), V, sg) in (0.0, 1.0)                                              # sign based: same in every view
print('yogas/nak/retro/combust tests passed')
