import sys, json, random, statistics as st, bisect
sys.path.insert(0, '/home/claude/astro/engine')
from jyotish import *
from bt_data import P
STEP = 10
TECHS = list(W_TECH) + ['all']
res = []   # per event
for name, grade, loc, tz, lat, lon, evs in P:
    c = Chart(name, loc, tz, lat, lon)
    b = loc - timedelta(hours=tz)
    last = max(e[0] for e in evs)
    t0, t1 = b + timedelta(days=365.25 * 12), min(last + timedelta(days=730), b + timedelta(days=365.25 * 85))
    g = grid(c, t0, t1, STEP)
    rows = [c.tech_scores(t) for t in g]
    S = {}
    for d in DOM:
        S[d] = {}
        for k in W_TECH:
            xs = [r[d][k] for r in rows]; S[d][k] = (st.mean(xs), st.pstdev(xs) or 1e-9)
    Z = [zscore(r, S) for r in rows]
    srt = {d: {k: sorted(z[d][k] for z in Z) for k in TECHS} for d in DOM}
    for ed, dom, lab in evs:
        if ed < t0: continue
        z = zscore(c.tech_scores(ed), S)
        pct = {}
        for k in TECHS:
            v = z[dom][k]; s = srt[dom][k]
            pct[k] = 100 * (bisect.bisect_left(s, v) + bisect.bisect_right(s, v)) / 2 / len(s)
        # specificity: rank of own-domain combined z among all 8 domains at that date
        zs = sorted((z[d]['all'], d) for d in DOM)
        spec = 100 * (1 - [d for _, d in reversed(zs)].index(dom) / 7)
        res.append(dict(p=name, g=grade, dom=dom, lab=lab, date=str(ed.date()), pct=pct, spec=spec, n=len(g)))
    print(name, 'done', len(g), 'grid pts', flush=True)
json.dump(res, open('/home/claude/astro/engine/bt_results.json', 'w'), indent=1)
def summ(rs, tag):
    n = len(rs)
    print(f'--- {tag}: n={n}')
    for k in TECHS:
        xs = [r['pct'][k] for r in rs]; m = st.mean(xs); se = 28.9 / n ** .5
        top20 = sum(x >= 80 for x in xs) / n * 100
        print(f'  {k:6s} mean pct {m:5.1f} (z={(m-50)/se:+.1f})  in top20% windows: {top20:4.0f}% (chance 20%)')
    sp = [r['spec'] for r in rs]; print(f'  domain-specificity mean {st.mean(sp):.1f} (chance 50)')
summ(res, 'ALL events')
summ([r for r in res if r['dom'] != 'setback'], 'positive-area events only')
summ([r for r in res if r['dom'] == 'setback'], 'setbacks only')
for d in DOM:
    rs = [r for r in res if r['dom'] == d]
    if rs: print(d, len(rs), 'combined mean pct', round(st.mean(r['pct']['all'] for r in rs), 1))
summ([r for r in res if r['g'] == 'A'], 'grade A births only')
