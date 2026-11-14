"""Report shape and determinism checks."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import report
r1 = report.build(1990, 6, 15, 14, 20, 0, 5.5, 28.6, 77.2, birth_time_grade='B', asof=(2026, 11, 14, 17))
r2 = report.build(1990, 6, 15, 14, 20, 0, 5.5, 28.6, 77.2, birth_time_grade='B', asof=(2026, 11, 14, 17))
js = json.dumps(r1, sort_keys=True)
assert js == json.dumps(r2, sort_keys=True), 'report not deterministic'
for k in ('schema_version', 'input', 'settings', 'chart', 'panchang', 'kp', 'timing', 'ashtakavarga', 'quality', 'events', 'dos', 'donts', 'precautions', 'remedies', 'calibration', 'transit'):
    assert k in r1, k
for k in ('events', 'dos', 'donts', 'precautions', 'remedies'):
    assert r1[k]['status'] == 'not_built' and r1[k]['items'] == [], k            # never invent content
assert r1['calibration']['status'] == 'none'
hi = r1['house_influence']['houses']; assert len(hi) == 12 and all(abs(sum(v['shares'].values()) - 1) < 2e-3 for v in hi.values())
assert all(v['main'] in v['shares'] and 1 <= len(v['shares']) <= 4 for v in hi.values())
assert len(r1['timing']['vimshottari']) == 81 and len(r1['chart']['divisional']) == 20
assert all(len(v) == 10 for v in r1['chart']['divisional'].values())
assert sum(r1['ashtakavarga']['bphs_plain']['sav']) == 337
assert r1['quality']['sensitivity_minutes_4']['D60']['+4min'] is not None
print('report tests passed; size bytes', len(js), '; D60 planets that flip with +4 min:', r1['quality']['sensitivity_minutes_4']['D60']['+4min'])
# rules wiring: items are tradition claims with null probability
import glob
_g = os.path.join(os.path.dirname(__file__), 'fixture_rules.jsonl')
open(_g, 'w').write('{"id":"t1","system":"parashari","engine_role":"event","life_area":"x","input":"Saturn in Cancer","outcome":"o","timing":"","remedy":"","source":"s","confidence":""}\n')
_r = report.build(1975, 8, 24, 5, 39, 4, 5.5, 25.1833, 75.8333, rules_glob=_g)
os.remove(_g)
assert _r['events']['status'] == 'built_unvalidated' and _r['events']['items'][0]['probability'] is None and _r['events']['items'][0]['label'] == 'tradition claim'
assert _r['calibration']['status'] == 'none'
print('report rules wiring ok')
