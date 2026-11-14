import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import dignity as D, rules_norm as N, influence as I, swisseph as swe, charts
# hand-checked dignity
assert D.states(0, 0) >= {'exalted'} and 'debilitated' in D.states(0, 6) and 'own' in D.states(0, 4)
assert D.states(3, 5) == {'exalted', 'own'}                  # Mercury in Virgo: both
assert D.states(6, 2) == {'friend'} and D.states(2, 2) == {'enemy'} and D.states(1, 4) == {'friend'}   # Saturn in Gemini (Mercury), Mars in Gemini (Mercury), Moon in Leo (Sun)
assert D.states(1, 0) == {'neutral'} and D.states(7, 3) == set()
assert D.states(4, 3) == {'exalted', 'friend'}   # Jupiter in Cancer: exalted; lord Moon is a friend
# aspects: counts and offsets
assert D.aspects_house(4, 1) == {5, 7, 9} and D.aspects_house(6, 1) == {3, 7, 10} and D.aspects_house(2, 10) == {1, 4, 5} and D.aspects_house(0, 8) == {2}
assert D.aspects_planet(6, 1, 10) and not D.aspects_planet(6, 1, 9)
# parsing: parsed, and unsafe cases stay out
p = lambda t, s='': N.parse(t, s)
assert p('Sun exalted')['atoms'] == [('dignity', 0, 'exalted')] and p('Sun exalted')['status'] == 'parsed'
assert p('Jupiter in own sign')['atoms'] == [('dignity', 4, 'own')]
assert p('Saturn debilitated')['atoms'] == [('dignity', 6, 'debilitated')]
assert p('Mars in an enemy sign')['atoms'] == [('dignity', 2, 'enemy')]
assert p('Jupiter aspects 7th house')['atoms'] == [('aspects_house', 4, (7,))] and p('Jupiter aspects 7th house')['status'] == 'parsed'
assert p('Saturn aspected by Mars')['atoms'] == [('aspects_planet', 2, 6)]
assert p('Mars aspects Moon')['atoms'] == [('aspects_planet', 2, 1)]
assert p('Rahu exalted')['status'] == 'unparsed'                                          # nodes: not guessed
q = p('Rahu exalted and Moon in 4th house'); assert q['status'] == 'partial', q            # the Rahu part is NOT silently dropped
# fit on a neutral chart: a planet aspects exactly 3 houses (Jupiter) in every view, so the fits over houses 1..12 sum to 3
inp = (1990, 1, 1, 6, 0, 0, 5.5, 28.6139, 77.209)
c = charts.natal(*inp, factors=(1,))['charts'][1]
pos = {k: v[0] * 30 + v[1] for k, v in c.items() if k != 'asc'}; sg = {k: v[0] for k, v in c.items() if k != 'asc'}
V = I.bundle(swe.julday(1990, 1, 1, 6 - 5.5), 28.6139, 77.209, pos)
tot = sum(I.fit(p(f'Jupiter aspects {h}th house'), V, sg) for h in range(1, 13)); assert abs(tot - 3) < 1e-3, tot
tot = sum(I.fit(p(f'Saturn aspects {h}th house'), V, sg) for h in range(1, 13)); assert abs(tot - 3) < 1e-3, tot
# dignity fit is 0 or 1 and matches the sign
for pl in range(7):
    ok = [s for s in ('exalted', 'debilitated', 'own', 'friend', 'enemy', 'neutral') if I.fit(N.parse(f'{["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"][pl]} {s if s in ("exalted","debilitated") else "in "+s+" sign" if s != "own" else "in own sign"}'), V, sg) == 1.0]
    assert set(ok) == D.states(pl, sg[pl]), (pl, ok, D.states(pl, sg[pl]))
print('dignity/aspect tests passed')
