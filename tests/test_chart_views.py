import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import influence as I
# lagna at 100.0 deg (Cancer 10 deg); planet Sun at 125 (Cancer 25), Moon at 135 (Leo 15)
vs = I.chart_views(100.0, {0: 125.0, 1: 135.0}, 1.0, 'X')
assert set(vs) == {'X', 'X_equal_asc'} and abs(sum(v['weight'] for v in vs.values()) - 1.0) < 1e-9
assert vs['X']['spans'][1] == [(3, 30.0)]                                   # whole sign: house 1 = Cancer only
assert vs['X_equal_asc']['spans'][1] == [(3, 20.0), (4, 10.0)]              # equal from 10 deg Cancer: 20 Cancer + 10 Leo (main + minor)
assert all(len(v['spans'][h]) == 2 for v in [vs['X_equal_asc']] for h in range(1, 13))
assert vs['X']['planet_house'] == {0: 2, 1: 2} and vs['X_equal_asc']['planet_house'] == {0: 1, 1: 2}   # Sun Cancer 5 deg-in vs 1st house from the degree
# D9 exactness: Navamsha sign == sign of 9 x longitude
for L in (0.1, 29.9, 30.0, 45.5, 123.3, 200.0, 359.9): assert I.navamsha_sign(L) == int(((L * 9) % 360) // 30), L
ch = {'asc': (3, 10.0), **{p: (3, 25.0) for p in range(9)}}
r = I.divisional_shares({9: ch})
assert r['D9']['status'] == 'exact' and abs(sum(r['D9']['houses'][1]['shares'].values()) - 1) < 1e-9
assert r['D9']['houses'][1]['main'] == 'Cancer' and r['D9']['houses'][1]['minor'] == ['Leo'] and r['D9']['houses'][1]['shares']['Cancer'] > 0.8
print('test_chart_views ok')
