import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import atoms_store as S, influence as I, strength as ST
# validator
assert S.atom({'t': 'strength', 'p': 'Venus', 's': 'strong'}) == ('strength', 5, 'strong')
for bad in ({'t': 'strength', 'p': 'Rahu', 's': 'strong'}, {'t': 'strength', 'p': 'Sun', 's': 'average'}):
    try: S.atom(bad); raise SystemExit('should have failed')
    except S.Bad: pass
# evaluation: strong iff ratio >= 1; needs ctx 'strength'
v = {'planet_house': {p: 1 for p in range(9)}}; sg = {p: 0 for p in range(9)}
assert I._atom_val(('strength', 5, 'strong'), v, sg, {'strength': {5: 1.0}}) == 1.0
assert I._atom_val(('strength', 5, 'strong'), v, sg, {'strength': {5: 0.99}}) == 0.0
assert I._atom_val(('strength', 5, 'weak'), v, sg, {'strength': {5: 0.99}}) == 1.0
assert I._needs((('strength', 5, 'weak'),)) == {'strength'}
# real Shadbala on a synthetic chart (Delhi 1990-01-01 06:30)
sb = ST.shadbala(1990, 1, 1, 6, 30, 0, 5.5, 28.6139, 77.209); r = ST.ratios(sb)
assert set(r) == set(range(7)) and all(0.3 < x < 3 for x in r.values()), r
assert all(abs(sb['rupa'][p] - sb['total_virupa'][p] / 60) < 0.02 for p in range(7))
print('test_strength ok', {k: round(x, 2) for k, x in r.items()})
