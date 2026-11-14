"""Per-technique validation: does the technique fire more at real events of its area than at random times of the same person's life?
z uses each person's own base fire-rate (Poisson-binomial normal approx); BH-FDR across all techniques. Writes validation.json"""
import sys, json, math, numpy as np
sys.path.insert(0, '/home/claude/astro/tech')
from engine import *
import people_loader as L
from collections import defaultdict
specs = load_specs(); S = {s['id']: dict(exp=0.0, var=0.0, hits=0, n=0, base=[]) for s in specs}
areas = sorted(set(s['area'] for s in specs))
def firing(c, t, area):
    x = Ctx(c, t, area); return {s['id']: run_spec(s, x)[0] for s in specs if s['area'] == area}
for p in L.load_all():
    c = Chart(p['name'], p['local'], p['tz'], p['lat'], p['lon']); b = p['local'] - timedelta(hours=p['tz']); last = max(e[0] for e in p['events'])
    t0, t1 = b + timedelta(days=365.25 * 12), min(last + timedelta(days=730), b + timedelta(days=365.25 * 85)); g = grid(c, t0, t1, 10)
    evs = [(ed, dom) for ed, dom, lab in p['events'] if ed >= t0 and dom in areas]
    for area in set(d for _, d in evs):
        cnt = defaultdict(int)
        for t in g:
            for k, v in firing(c, t, area).items(): cnt[k] += v
        for ed, dom in evs:
            if dom != area: continue
            f = firing(c, ed, area)
            for k, v in f.items():
                q = cnt[k] / len(g); r = S[k]; r['exp'] += q; r['var'] += q * (1 - q); r['hits'] += int(v); r['n'] += 1; r['base'].append(q)
out = []
for k, r in S.items():
    if r['n'] < 5: continue
    z = (r['hits'] - r['exp']) / math.sqrt(r['var']) if r['var'] > 0 else 0.0
    pv = 0.5 * math.erfc(abs(z) / math.sqrt(2)) * 2
    out.append(dict(id=k, n_events=r['n'], hits=r['hits'], expected_by_chance=round(r['exp'], 1), base_rate=round(float(np.mean(r['base'])), 3), lift=round(r['hits'] / r['exp'], 2) if r['exp'] else None, z=round(z, 2), p=round(pv, 4)))
out.sort(key=lambda r: r['p']); m = len(out)
for i, r in enumerate(out): r['bh_q'] = round(min(1, r['p'] * m / (i + 1)), 3)
json.dump(out, open('/home/claude/astro/tech/validation.json', 'w'), indent=1)
print(f"{'technique':34s} n  hits exp   base  lift   z     p    q")
for r in out: print(f"{r['id']:34s}{r['n_events']:3d} {r['hits']:4d} {r['expected_by_chance']:5.1f} {r['base_rate']:.2f} {r['lift']}  {r['z']:5.2f} {r['p']:.3f} {r['bh_q']:.2f}")
