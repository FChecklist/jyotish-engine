import sys, os, datetime, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core')); sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tune'))
import swisseph as swe, report, daily, gochara as G, shortterm, guide, diary_score
from guidance_rules import *
# tables
assert sorted(NAK_CLASS) == list(range(1, 28)) and len(NAKS) == 27                           # every nakshatra has exactly one class
assert len(BAD_YOGA) == 9 and VISHTI == (8, 15, 22, 29, 36, 43, 50, 57)
# tara: count from birth star, mod 9
assert daily.tara_of(1, 3)[0] == 3 and daily.tara_of(1, 10)[0] == 1 and daily.tara_of(1, 19)[0] == 1 and daily.tara_of(5, 5)[0] == 1 and daily.tara_of(10, 9)[0] == 9   # day nak 9 vs birth 10: count 27 -> 9
assert [daily.tara_of(1, n)[1][1] for n in (2, 3, 4)] == ['good', 'bad', 'good']
# Rahu Kaal on a 06:00-18:00 day: Sat 09:00-10:30, Mon 07:30-09:00, Fri 10:30-12:00, Sun 16:30-18:00 ; Abhijit 11:36-12:24
for wd, (a, b) in {5: (9, 10.5), 0: (7.5, 9), 4: (10.5, 12), 6: (16.5, 18), 2: (12, 13.5), 3: (13.5, 15), 1: (15, 16.5)}.items():
    r = daily.rahu_window(wd, 6, 18); assert abs(r[0] - a) < 1e-9 and abs(r[1] - b) < 1e-9, wd
a, b = daily.abhijit_window(6, 18); assert abs(a - 11.6) < 1e-9 and abs(b - 12.4) < 1e-9
# gochara hand cases (rules DB BK13): moon in sign 0
sg = lambda **k: {p: 0 for p in range(9)} | {int(a[1:]): v for a, v in k.items()}
r = G.assess(0, sg(p0=2, p6=2))                  # Sun and Saturn in 3rd, no vedha between Sun and Saturn
assert r[0]['result'] == 'favourable' and r[6]['result'] == 'favourable' and r[0]['vedha_by'] is None
r = G.assess(0, sg(p6=2, p4=11))                 # BK13_0019: Saturn 3rd (good) blocked by another planet in 12th
assert r[6]['result'] == 'neutral' and r[6]['vedha_by'] == 'Jupiter', r[6]
r = G.assess(0, sg(p6=11, p4=2))                 # BK13_0021 vipareeta: Saturn 12th cancelled by another planet in 3rd
assert r[6]['result'] == 'neutral', r[6]
r = G.assess(0, sg(p6=0)); assert r[6]['result'] == 'very_adverse'                       # BK13_0007
r = G.assess(0, sg(p2=7)); assert r[2]['result'] == 'very_adverse'                       # malefic in 8th BK13_0006
r = G.assess(0, sg(p4=10)); assert r[4]['result'] == 'favourable'                        # 11th always good BK13_0005
assert G.moorthi(6, 0)['result'] == 'adverse' and G.moorthi(6, 4)['result'] == 'good' and G.moorthi(4, 4)['moorthi'] == 'iron'
# vedha table equals the DB text when the DB is present
dbp = '/home/claude/jyotish-code/rules'
if os.path.isdir(dbp):
    import apply_rules, re
    rows = {r['id']: r for r in apply_rules.load(dbp + '/books_master_v8.part*.jsonl') if r['system'] == 'gochara'}
    for i, p in (('BK13_0022', 0), ('BK13_0025', 3), ('BK13_0027', 5), ('BK13_0023', 1)):
        houses = [int(x) for x in re.findall(r'\d+', rows[i]['input'].split('from')[0])]
        vs = [int(x) for x in re.search(r'in ([\d,]+) respectively', rows[i]['outcome']).group(1).split(',')]
        assert [VEDHA[p][h] for h in houses] == vs[:len(houses)], (i, houses, vs)
    print('vedha table matches DB text')
# ingress finder vs independent Swiss Ephemeris (sidereal Lahiri): Sun longitude at found moment is a multiple of 30 deg
swe.set_sid_mode(swe.SIDM_LAHIRI)
tz, lat, lon = 5.5, 28.6139, 77.209
(s, ss), (e, es) = shortterm.sun_window(datetime.date(2026, 11, 14), tz, lat, lon)
for dt in (s, e):
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60 - tz); x = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)[0][0]
    assert min(x % 30, 30 - x % 30) < 0.02, (dt, x)
assert (e - s).days in (29, 30, 31) and s.date() <= datetime.date(2026, 11, 14) < e.date()
# date-based periods (Rajat 2026-11-15): start on the sankranti date, end the day before the next one
for day, a, b in ((datetime.date(2026, 4, 14), (2026, 4, 14), (2026, 5, 15)), (datetime.date(2026, 5, 14), (2026, 4, 14), (2026, 5, 15)), (datetime.date(2026, 5, 15), (2026, 5, 15), (2026, 6, 15)), (datetime.date(2026, 11, 16), (2026, 11, 16), (2026, 12, 16))):
    (s2, _), (e2, _) = shortterm.sun_window(day, tz, lat, lon); assert (s2.date(), e2.date()) == (datetime.date(*a), datetime.date(*b)), (day, s2, e2)
# end to end on a neutral chart: exactly <=3 and <=3, no reasons or probabilities in the user view
rep = report.build(1990, 1, 1, 6, 0, 0, 5.5, 28.6139, 77.209)
g = guide.person_guidance(rep, datetime.date(2026, 11, 14), tz, lat, lon)
u = g['user']
for layer in ('daily', 'month'):
    assert len(u[layer]['do']) <= 3 and len(u[layer]['dont']) <= 3 and len(u[layer]['do']) + len(u[layer]['dont']) >= 3, u[layer]
blob = str(u).lower()
for bad in ('probab', 'because', 'tradition', 'bk13', 'rule', '%', 'predict'): assert bad not in blob, bad
assert any('between' in t and 'Rahu' not in t for t in u['daily']['dont']) or any('between' in t for t in u['daily']['dont'])
assert g['engine']['daily_chosen']['dont'][0]['why'] and 'probability' in g['engine']['label']
# no do-vs-dont self contradiction on starting
txt = ' '.join(u['daily']['do']); assert not ('Start' in txt and any('Do not begin new' in t or 'Avoid starting anything new' in t for t in u['daily']['dont'])), u['daily']
# diary scoring: strong link is detected, no link is not
rnd = random.Random(1); days = [(f'd{i}', 'A') for i in range(120)]
grades = {k: rnd.choice([-2, -1, 0, 1, 2]) for k in days}
linked = [(d, p, min(5, max(1, 3 + grades[(d, p)] + rnd.choice([0, 0, 1, -1])))) for d, p in days]
random_ = [(d, p, rnd.randint(1, 5)) for d, p in days]
assert diary_score.score(linked, grades)['p_one_sided'] < 0.01 and diary_score.score(random_, grades)['p_one_sided'] > 0.05
print('daily/short-term tests passed')
