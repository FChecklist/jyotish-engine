import sys, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import guidance as G
mk = lambda role, inp, out, rem='': dict(id=inp, system='parashari', engine_role=role, life_area='x', input=inp, outcome=out, timing='', remedy=rem, source='s', confidence='', fit=1.0, label='tradition claim')
rep = {'timing': {'vimshottari': [{'maha': 'Venus', 'antar': 'Moon', 'start_local': [2026, 3, 26, 0], 'years': 1}]},
       'remedies': {'items': [mk('remedy', 'r1', 'o', 'feed cows'), mk('remedy', 'r2', 'o', 'invest in shares')]},
       'donts': {'items': [mk('donot', 'd1', 'lying')]},
       'events': {'items': [mk('event', 'e1', 'loss of money and quarrel'), mk('event', 'e2', 'Destroys enemies, fearless'), mk('event', 'e3', 'death in family'), mk('event', 'e4', 'short life and loss of wealth'), mk('event', 'e5', 'early danger to father')]}}
g = G.guidance(rep, datetime.datetime(2026, 11, 14))
assert [x['rule_id'] for x in g['dos']] == ['r1'] and [x['rule_id'] for x in g['precautions']] == ['e1'], g   # positives, death, investment all stay out
assert g['dropped_by_safety_filter'] == 4 and g['window']['antar'] == 'Moon'
assert all(x['probability'] is None and x['label'] == 'tradition claim' for k in ('dos', 'donts', 'precautions') for x in g[k])
print('guidance tests passed')
