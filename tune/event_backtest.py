"""Backtest the daily and monthly signals on a person's dated life events. Private data path is an argument; nothing personal is stored in git.
For each event date: daily score (guide logic) and gochara score, versus random other days within +-400 days of the same person.
Result = permutation p: how often a random day per event scores as high on average. Chance = p near 0.5 or higher."""
import sys, os, json, datetime, random, statistics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import report, daily, gochara as G, shortterm
TZ, LAT, LON = 5.5, 28.6139, 77.209
def gscore(natal, date):
    tr = shortterm._at(datetime.datetime(date.year, date.month, date.day, 12), TZ, LAT, LON); gm = G.assess(natal['moon_sign0'], tr['sign'], natal['bav'], natal['sav'])
    return sum({'favourable': 1, 'neutral': 0, 'adverse': -1, 'very_adverse': -2}[gm[p]['result']] * (2 if p in (4, 6) else 1) for p in (0, 2, 3, 4, 5, 6, 7, 8))
def metrics(natal, date):
    _, f = daily.day_items(natal, date, TZ, LAT, LON)
    return {'net': f['net'], 'chandra': int(f['chandra_house'] in CHANDRA_GOOD), 'tara_good': int(TARA_Q[f['tara']] == 'good'), 'tara_bad': int(TARA_Q[f['tara']] == 'bad'), 'gochara': gscore(natal, date)}
from guidance_rules import CHANDRA_GOOD, TARA
TARA_Q = {v[0]: v[1] for v in TARA.values()}
def run(family_json, who, n_null=120, draws=5000, seed=7, skip_types=('birth',), min_day=0):
    d = json.load(open(family_json)); p = d['people'][who]
    dt = datetime.datetime.strptime(p['birth'], '%Y-%m-%d %H:%M:%S')
    natal = daily.natal_of(report.build(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, 5.5, p['lat'], p['lon']))
    ev = []
    for e in d['breadcrumbs_rajat']:
        if e['precision'] != 'd' or 'born' in e['label'].lower(): continue
        ev.append((datetime.datetime.strptime(e['date'], '%d %b %Y').date(), e))
    rnd = random.Random(seed); obs = []; nul = []
    for date, e in ev:
        obs.append(metrics(natal, date)); pool = []
        while len(pool) < n_null:
            o = rnd.randint(-400, 400)
            if abs(o) > 3: pool.append(metrics(natal, date + datetime.timedelta(days=o)))
        nul.append(pool)
    out = {'n_events': len(ev)}
    for k in ('net', 'chandra', 'tara_good', 'tara_bad', 'gochara'):
        o = statistics.mean(x[k] for x in obs); ge = 0
        for _ in range(draws):
            s = statistics.mean(rnd.choice(pool)[k] for pool in nul); ge += s >= o
        out[k] = {'observed_mean': round(o, 3), 'null_mean': round(statistics.mean(x[k] for pool in nul for x in pool), 3), 'p_one_sided_higher': round((ge + 1) / (draws + 1), 4)}
    return out
if __name__ == '__main__':
    print(json.dumps(run(sys.argv[1], sys.argv[2]), indent=1))
