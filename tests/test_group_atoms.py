import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import atoms_store as S, influence as I
a = S.atom({'t': 'group_in_house', 'g': 'malefic', 'h': [5]}); assert a == ('group_in_house', 'malefic', (5,))
for bad in ({'t': 'group_in_house', 'g': 'x', 'h': [5]}, {'t': 'planet_aspected_by', 'p': 'Moon', 'by': []}, {'t': 'planet_aspected_by', 'p': 'Moon', 'by': ['Moon']}, {'t': 'lord_with_group', 'n': 13, 'g': 'benefic'}):
    try: S.atom(bad); raise SystemExit('FAILED accepted ' + str(bad))
    except S.Bad: pass
ctx = {'lon': {0: 10.0, 1: 100.0}}            # Moon 90 deg ahead of Sun: waxing
assert I.group_members('benefic', ctx) == {1, 3, 4, 5} and I.group_members('malefic', ctx) == {0, 2, 6, 7, 8}
ctx = {'lon': {0: 10.0, 1: 250.0}}            # 240: waning
assert 1 in I.group_members('malefic', ctx) and 1 not in I.group_members('benefic', ctx)
# chart (one whole view): Sun h1, Moon h7, Mars h4, Merc h1, Jup h5, Ven h2, Sat h10, Rahu h3, Ketu h9. Sun-Moon 240 => Moon waning
ph = {0: 1, 1: 7, 2: 4, 3: 1, 4: 5, 5: 2, 6: 10, 7: 3, 8: 9}
sp = {h: [((h + 3) % 12, 30.0)] for h in range(1, 13)}                  # house h -> sign (h+3)%12
v = {'weight': 1.0, 'spans': sp, 'planet_house': ph}
c = {'lon': {0: 10.0, 1: 250.0}}
assert I._atom_val(('group_in_house', 'malefic', (4,)), v, {}, c) == 1.0      # Mars h4
assert I._atom_val(('group_in_house', 'benefic', (5,)), v, {}, c) == 1.0      # Jupiter h5
assert I._atom_val(('planet_with_group', 3, 'malefic'), v, {}, c) == 1.0      # Mercury with Sun
assert I._atom_val(('planet_with_group', 5, 'malefic'), v, {}, c) == 0.0      # Venus alone
assert I._atom_val(('planet_aspected_by', 1, ('planets', (3,))), v, {}, c) == 1.0   # Moon h7 aspected by Mercury h1 (7th)
assert I._atom_val(('planet_aspected_by', 1, ('group', 'benefic')), v, {}, c) == 1.0
assert I._atom_val(('planet_aspected_by', 5, ('planets', (0,))), v, {}, c) == 0.0
assert I._needs([S.atom({'t': 'planet_aspected_by', 'p': 'Moon', 'by': 'malefic'})]) == {'lon'}
print('test_group_atoms ok')
