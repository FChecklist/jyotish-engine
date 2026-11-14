"""Builds per-person feature caches for fine-tuning. For each person and each of the 8 life areas it stores, over the person's own life grid
(10-day steps, age 12 .. last event + 2y, max age 85), the z-scored technique scores (vim, kp, trans, chara, yog) and the rule-heat of 4 rule groups
(book, gautam, lk = Lal Kitab, mod = Parashari/KP/Jaimini/K.N.Rao modules), plus the same vector at each event date."""
import sys, json, pickle, os, statistics as st
sys.path.insert(0, '/home/claude/astro/suite')
import numpy as np
from suite_engines import *
TECH = list(W_TECH)                    # vim kp trans chara yog
GROUPS = ['book', 'gautam', 'lk', 'mod']
FEATS = TECH + GROUPS
MAP = {'wealth': 'career', 'health': 'setback'}
CACHE = '/home/claude/astro/tune/cache'; os.makedirs(CACHE, exist_ok=True)

def grp(r):
    if r['family'] == 'book': return 'book'
    if r['family'] == 'gautam': return 'gautam'
    return 'lk' if r['system'] == 'lalkitab' else 'mod'

def heat_vec(S, t):
    """dict dom -> [heat per group]"""
    h = {d: [0.0] * 4 for d in DOM}
    for r in S.active(t):
        if not r['outcome']: continue
        d = MAP.get(r['area'], r['area'])
        if d not in DOM: continue
        if (d == 'setback' and r['pol'] < 0) or (d != 'setback' and r['pol'] > 0):
            h[d][GROUPS.index(grp(r))] += r['w']
    return h

def build(person):
    """person: dict name, local(datetime), tz, lat, lon, events[(datetime, dom, label)]"""
    fn = f"{CACHE}/{person['name']}.pkl"
    if os.path.exists(fn): return pickle.load(open(fn, 'rb'))
    c = Chart(person['name'], person['local'], person['tz'], person['lat'], person['lon']); S = Suite(c)
    b = person['local'] - timedelta(hours=person['tz']); last = max(e[0] for e in person['events'])
    t0, t1 = b + timedelta(days=365.25 * 12), min(last + timedelta(days=730), b + timedelta(days=365.25 * 85))
    g = grid(c, t0, t1, 10)
    rows = [c.tech_scores(t) for t in g]
    Sx = {d: {k: (st.mean(r[d][k] for r in rows), st.pstdev([r[d][k] for r in rows]) or 1e-9) for k in TECH} for d in DOM}
    def vec(row, t):
        z = zscore(row, Sx); h = heat_vec(S, t); out = {}
        for d in DOM: out[d] = [z[d][k] for k in TECH] + h[d]
        return out
    G = {d: np.zeros((len(g), len(FEATS))) for d in DOM}
    for i, (t, row) in enumerate(zip(g, rows)):
        v = vec(row, t)
        for d in DOM: G[d][i] = v[d]
    ev = []
    for ed, dom, lab in person['events']:
        if ed < t0 or dom not in DOM: continue
        v = vec(c.tech_scores(ed), ed)
        ev.append(dict(dom=dom, date=str(ed.date()), lab=lab, x=np.array(v[dom])))
    # standardise rule-heat columns per area on the person's own grid so that scale is comparable
    out = dict(name=person['name'], grade=person.get('grade', '?'), G=G, ev=ev)
    pickle.dump(out, open(fn, 'wb'))
    return out

def pct(score_grid, score_ev):
    s = np.sort(score_grid)
    return 100 * (np.searchsorted(s, score_ev, 'left') + np.searchsorted(s, score_ev, 'right')) / 2 / len(s)

def evaluate(people, w):
    """w: weight vector over FEATS. returns list of (person, dom, percentile)"""
    w = np.asarray(w, float); out = []
    for p in people:
        sg = {d: p['G'][d] @ w for d in DOM}
        for e in p['ev']: out.append((p['name'], e['dom'], pct(sg[e['dom']], float(e['x'] @ w))))
    return out

def mean_pct(people, w):
    r = evaluate(people, w); return float(np.mean([x[2] for x in r])) if r else 50.0
