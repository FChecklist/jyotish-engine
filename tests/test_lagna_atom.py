import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import atoms_store as S, influence as I
a = S.atom({'t': 'lagna_sign', 'sign': ['Leo', 'Cancer']}); assert a == ('lagna_sign', (3, 4))
for bad in ({'t': 'lagna_sign', 'sign': ['Foo']}, {'t': 'lagna_sign', 'sign': []}):
    try: S.atom(bad); raise SystemExit('FAILED: accepted bad lagna atom')
    except S.Bad: pass
# a view whose lagna is 60% Leo, 40% Virgo (multi-sign house 1)
v = {'weight': 1.0, 'spans': {1: [(4, 18.0), (5, 12.0)]}, 'planet_house': {}}
assert abs(I._atom_val(('lagna_sign', (4,)), v, {}, {}) - 0.6) < 1e-9
assert abs(I._atom_val(('lagna_sign', (4, 5)), v, {}, {}) - 1.0) < 1e-9
assert I._atom_val(('lagna_sign', (0,)), v, {}, {}) == 0.0
v['lagna_spans'] = [(0, 30.0)]; assert I._atom_val(('lagna_sign', (0,)), v, {}, {}) == 1.0   # D9 view uses the D1 lagna
print('test_lagna_atom ok')
