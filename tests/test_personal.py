"""Tests for core/personal.py (person-specific daily guidance). Uses only fictitious public sample births, never family data.
Run: python test_personal.py  (exit 0 = pass)."""
import sys, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import swisseph as swe, report, personal as P, dignity as DG
from guidance_rules import *

# --- condition(): dignity + house, hand cases (CALCULATION_LEDGER tables)
assert P.condition(0, 0, 1)[0] == 2.5            # Sun exalted in Aries, 1st house: +2 +0.5
assert P.condition(0, 6, 8)[0] == -3.0           # Sun debilitated in Libra, 8th house: -2 -1
assert P.condition(4, 8, 5)[0] == 2.0            # Jupiter own sign (Sagittarius) 5th: +1.5 +0.5
assert P.condition(7, 3, 12)[0] == -1.0          # Rahu: no dignity rule, 12th house only
assert P.dig_word(0, 0) == 'exalted' and P.dig_word(7, 3) == 'no dignity rule'

# --- Vimshottari pratyantar: synthetic rows (Jupiter maha / Saturn antar), partition must tile the antar exactly and start with the antar lord
rows = [{'maha': 'Jupiter', 'antar': 'Jupiter', 'start_local': [2000, 1, 1, 0.0], 'years': 2.1333},
        {'maha': 'Jupiter', 'antar': 'Saturn', 'start_local': [2002, 2, 1, 0.0], 'years': 2.5333},
        {'maha': 'Jupiter', 'antar': 'Mercury', 'start_local': [2004, 9, 1, 0.0], 'years': 2.2667}]
rep = {'timing': {'vimshottari': rows}}
first = P.running_dasha(rep, datetime.datetime(2002, 2, 2, 12)); assert first['antar'] == 4 + 2 and first['praty'] == 6 and first['maha'] == 4   # Saturn antar (id 6), first pratyantar = Saturn
seen = set(); t = datetime.datetime(2002, 2, 1)
while t < datetime.datetime(2004, 9, 1):
    r = P.running_dasha(rep, t); assert r['antar'] == 6; seen.add(r['praty']); t += datetime.timedelta(days=7)
assert seen == set(range(9)), seen                 # all nine pratyantars occur inside one antardasha
# order: after Saturn comes Mercury, Ketu, Venus ... (Vimshottari cycle)
assert P.ORD[(P.ORD.index(6) + 1) % 9] == 3

# --- Muntha (BK9_0306): sign = (natal lagna + completed years) mod 12
def muntha(lagna, years): return (lagna + years) % 12
assert muntha(3, 9) == 0 and muntha(11, 1) == 0 and muntha(5, 12) == 5

# --- solar return: Sun back on its natal sidereal longitude within a minute of arc, and not after asof
swe.set_sid_mode(swe.SIDM_LAHIRI); natal_lon = swe.calc_ut(swe.julday(1990, 6, 15, 12 - 5.5), swe.SUN, swe.FLG_SIDEREAL)[0][0]
ret = P.solar_return(natal_lon, (6, 15), datetime.datetime(2026, 11, 15, 12), 5.5)
jd = swe.julday(ret.year, ret.month, ret.day, ret.hour + ret.minute / 60 + ret.second / 3600 - 5.5); swe.set_sid_mode(swe.SIDM_LAHIRI)
assert abs(((swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0] - natal_lon + 180) % 360) - 180) < 0.01 and ret.year == 2026 and ret <= datetime.datetime(2026, 11, 15, 12)
nl2 = swe.calc_ut(swe.julday(1990, 12, 25, 12 - 5.5), swe.SUN, swe.FLG_SIDEREAL)[0][0]
ret2 = P.solar_return(nl2, (12, 25), datetime.datetime(2026, 11, 15, 12), 5.5); assert ret2.year == 2025   # birthday later in the year -> last return is last year

# --- ranking: strong vs mild, no padding, opposite signs do not cancel into a fake line, personal reasons before 'everybody' reasons
S = P.Sig()
S.add(3, 2.0, 'transit', 'F-A', 'a', ['R1'], True, 'brief a'); S.add(3, 0.5, 'dasha', 'F-B', 'b', ['R2'], True, 'brief b')
S.add(7, -1.5, 'dasha', 'F-C', 'c', ['R3'], True, 'brief c')
S.add(10, 0.1, 'transit', 'F-D', 'd', [], True, 'tiny')
S.add('init', 1.5, 'panchang', 'F-E', 'e', ['R4'], False, 'everybody'); S.add('init', 0.6, 'birth-vs-today', 'F-F', 'f', ['R5'], True, 'personal')
areas = P.rank(S); ch = P.choose(areas, None)
assert [x['area'] for x in ch['do']] == ['init', 3] or [x['area'] for x in ch['do']] == [3, 'init']
assert [x['area'] for x in ch['dont']] == [7] and len(ch['dont']) == 1           # only one real caution: nothing padded to 3
assert all(x['area'] != 10 for x in ch['do'])                                     # |net| 0.1 is below the mild floor
init = [x for x in ch['do'] if x['area'] == 'init'][0]; assert init['because'][0] == 'personal' and 'everybody' in init['because']   # personal reason listed first
assert [x for x in ch['do'] if x['area'] == 3][0]['strength'] == 'clear'

# --- end to end on two fictitious births: runs, every line has area/reasons/rule ids, results differ between people, signals reference only computed facts
asof = datetime.date(2026, 11, 15)
res = {}
for name, b in (('A', datetime.datetime(1990, 6, 15, 14, 20)), ('B', datetime.datetime(1985, 3, 2, 6, 45))):
    r = report.build(b.year, b.month, b.day, b.hour, b.minute, 0, 5.5, 28.6, 77.2, asof=(asof.year, asof.month, asof.day, 12))
    res[name] = P.person_result(name, r, b, asof)
    v = res[name]['facts']['varsha']; assert v['muntha_sign'] == (r['chart']['divisional']['D1']['Lagna']['sign0'] + (v['completed_years'])) % 12 and v['completed_years'] == int(v['return_local'][:4]) - b.year   # real Muntha formula BK9_0306 on the real chart
    assert (v['muntha_house'] == (v['muntha_sign'] - v['annual_lagna']) % 12 + 1)
for name, x in res.items():
    assert x['n_signals'] > 20 and x['facts']['dasha'] and x['facts']['varsha']['muntha_house'] in range(1, 13), name
    assert 1 <= len(x['chosen']['do']) <= 3 and len(x['chosen']['dont']) <= 3
    for it in x['chosen']['do'] + x['chosen']['dont']:
        assert it['because'] and it['factors'] and it['strength'] in ('clear', 'mild')
    for s_ in x['signals']: assert s_['tag'].startswith('F-') and s_['why'] and isinstance(s_['rules'], list)
    assert len(x['limits']) >= 6
a_ = [i['text'] + str(i['because']) for i in res['A']['chosen']['do'] + res['A']['chosen']['dont']]; b_ = [i['text'] + str(i['because']) for i in res['B']['chosen']['do'] + res['B']['chosen']['dont']]
assert a_ != b_ and res['A']['facts']['dasha'] != res['B']['facts']['dasha']      # person-specific, not one list for everybody
print('test_personal ok')
