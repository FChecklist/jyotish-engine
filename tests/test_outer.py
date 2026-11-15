import sys, os, datetime; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import outer as O
p = O.positions(datetime.datetime(1975, 5, 1, 12, 0, 0), 5.5)
assert set(p) == {'Uranus', 'Neptune', 'Pluto'} and all(0 <= v['lon'] < 360 for v in p.values())
d = O.describe({'Pluto': {'alias': 'Yama', 'lon': 100.0, 'retro': False}}, 0, {'Sun': 105.0, 'Moon': 281.0, 'Mars': 130.0})
c = d['Pluto']['contacts']; assert d['Pluto']['sign'] == 'Cancer' and d['Pluto']['house'] == 4
assert [(x['planet'], x['kind']) for x in c] == [('Moon', 'opposition (7th aspect)'), ('Sun', 'conjunction')]
assert d['Pluto']['in_tentative_house'] is False
d = O.describe({'Pluto': {'alias': 'Yama', 'lon': 220.0, 'retro': False}}, 0, {}); assert d['Pluto']['house'] == 8 and d['Pluto']['in_tentative_house']
print('test_outer ok')
