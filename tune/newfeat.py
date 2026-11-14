"""New techniques, rules fixed BEFORE testing (pre-registered): sade, ashv, charak, divD, tajaka. Lal Kitab annual chart NOT implemented (needs the Varshphal table)."""
import sys, pickle, os, math
sys.path.insert(0, '/home/claude/astro'); sys.path.insert(0, '/home/claude/astro/engine')
import numpy as np, swisseph as swe
from datetime import timedelta
from jyotish import *
from ac import SLORD, jaim_aspects, planets, asc
NEW = ['sade', 'ashv', 'charak', 'divD', 'tajaka']
POSD = lambda d: DOM[d]['pos']
# ---- Parashari BAV tables (benefic positions counted from contributor)
_T = {
'Sun':    {'Sun':[1,2,4,7,8,9,10,11],'Moon':[3,6,10,11],'Mars':[1,2,4,7,8,9,10,11],'Mercury':[3,5,6,9,10,11,12],'Jupiter':[5,6,9,11],'Venus':[6,7,12],'Saturn':[1,2,4,7,8,9,10,11],'Lagna':[3,4,6,10,11,12]},
'Moon':   {'Sun':[3,6,7,8,10,11],'Moon':[1,3,6,7,10,11],'Mars':[2,3,5,6,9,10,11],'Mercury':[1,3,4,5,7,8,10,11],'Jupiter':[1,4,7,8,10,11,12],'Venus':[3,4,5,7,9,10,11],'Saturn':[3,5,6,11],'Lagna':[3,6,10,11]},
'Mars':   {'Sun':[3,5,6,10,11],'Moon':[3,6,11],'Mars':[1,2,4,7,8,10,11],'Mercury':[3,5,6,11],'Jupiter':[6,10,11,12],'Venus':[6,8,11,12],'Saturn':[1,4,7,8,9,10,11],'Lagna':[1,3,6,10,11]},
'Mercury':{'Sun':[5,6,9,11,12],'Moon':[2,4,6,8,10,11],'Mars':[1,2,4,7,8,9,10,11],'Mercury':[1,3,5,6,9,10,11,12],'Jupiter':[6,8,11,12],'Venus':[1,2,3,4,5,8,9,11],'Saturn':[1,2,4,7,8,9,10,11],'Lagna':[1,2,4,6,8,10,11]},
'Jupiter':{'Sun':[1,2,3,4,7,8,9,10,11],'Moon':[2,5,7,9,11],'Mars':[1,2,4,7,8,10,11],'Mercury':[1,2,4,5,6,9,10,11],'Jupiter':[1,2,3,4,7,8,10,11],'Venus':[2,5,6,9,10,11],'Saturn':[3,5,6,12],'Lagna':[1,2,4,5,6,7,9,10,11]},
'Venus':  {'Sun':[8,11,12],'Moon':[1,2,3,4,5,8,9,11,12],'Mars':[3,5,6,9,11,12],'Mercury':[3,5,6,9,11],'Jupiter':[5,8,9,10,11],'Venus':[1,2,3,4,5,8,9,10,11],'Saturn':[3,4,5,8,9,10,11],'Lagna':[1,2,3,4,5,8,9,11]},
'Saturn': {'Sun':[1,2,4,7,8,10,11],'Moon':[3,6,11],'Mars':[3,5,6,10,11,12],'Mercury':[6,8,9,10,11,12],'Jupiter':[5,6,11,12],'Venus':[6,11,12],'Saturn':[3,5,6,11],'Lagna':[1,3,4,6,10,11]},
}
_TOT = {'Sun':48,'Moon':49,'Mars':39,'Mercury':54,'Jupiter':56,'Venus':52,'Saturn':39}
for k in _T: assert sum(len(v) for v in _T[k].values()) == _TOT[k], k   # checksum vs classical totals
def bav(c):
    base = {p: c.P[p]['sign'] for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']}; base['Lagna'] = c.lag
    return {X: [sum(1 for cc, tb in _T[X].items() if ((s - base[cc]) % 12 + 1) in tb) for s in range(12)] for X in _T}
def div_sign(lon, n):
    if n == 9: return int(lon // (30 / 9)) % 12
    s = int(lon // 30); k = int((lon % 30) // 3)          # D10
    return (s + k) % 12 if s % 2 == 0 else (s + 8 + k) % 12
KAR = {'career': 1, 'status': 0, 'marriage': 6, 'children': 4, 'setback': 5, 'foreign': None}  # index in AK,AmK,BK,MK,PK,GK,DK
DCH = {'marriage': 9, 'children': 9, 'setback': 9, 'foreign': 9, 'career': 10, 'status': 10}
def solar_returns(c, n_years=95):
    sun0 = c.P['Sun']['lon']; out = []
    for n in range(n_years):
        jd = c.jd + n * 365.2422
        for _ in range(8):
            r, _f = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
            d = ((sun0 - r[0] + 180) % 360) - 180; jd += d / r[3]
        out.append(jd)
    return out
class New:
    def __init__(s, c):
        s.c = c; s.B = bav(c)
        ks = sorted(['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'], key=lambda p: -c.P[p]['deg']); s.ks = ks
        s.rets = solar_returns(c); s._yc = {}
    def tajaka_year(s, n):
        if n in s._yc: return s._yc[n]
        c = s.c; jd = s.rets[n]; P = planets(jd); lr = int(asc(jd, c.lat, c.lon) // 30)
        mun = (c.lag + n) % 12; mh = (mun - lr) % 12 + 1; lord = SLORD[mun]; hm = (P[lord]['sign'] - lr) % 12 + 1
        s._yc[n] = (lr, mun, mh, lord, hm); return s._yc[n]
    def vec(s, t, doms=None):
        c = s.c; T = c.tpos(t); da = c.dasha(t); out = {}
        ss = T['Saturn']['sign']; ms = c.P['Moon']['sign']; hsat = (ss - ms) % 12 + 1
        ssv = {1: 1.0, 12: .7, 2: .7, 4: .5, 8: .5}.get(hsat, 0.0)
        bj = s.B['Jupiter'][T['Jupiter']['sign']] / 8; bs = s.B['Saturn'][ss] / 8; ash = (bj + bs) / 2
        jd = swe.julday(t.year, t.month, t.day, 12)
        n = max(0, min(len(s.rets) - 2, sum(1 for r in s.rets if r <= jd) - 1)); lr, mun, mh, lord, hm = s.tajaka_year(n)
        for d in (doms or DOM):
            spec = DOM[d]; hs = spec['h']; pos = spec['pos']
            sade = ssv if not pos else -ssv
            ashv = ash if pos else 1 - ash
            # char dasha on Jaimini karaka
            kp = spec['kar'][0] if KAR.get(d) is None else s.ks[KAR[d]]
            ksg = c.P[kp]['sign']; ch = 0.0
            if da['chara']:
                for (sg, a, b) in da['chara']:
                    ch += (1.0 if (sg == ksg or ksg in jaim_aspects(sg)) else 0.0) / 2
            # divisional chart dasha-lord strength
            nD = DCH.get(d, 9); lagD = div_sign(c.asc, nD) if nD == 10 else div_sign(c.asc, 9)
            wsum = sum(1.0 if i == 0 else .7 for i in range(len(hs))); dv = 0.0; wv = (3, 3, 1.5)
            for w, X in zip(wv, da['vim']):
                sX = div_sign(c.P[X]['lon'], nD); hX = (sX - lagD) % 12 + 1; r = 0
                for i, h in enumerate(hs):
                    wh = 1.0 if i == 0 else .7
                    if SLORD[(lagD + h - 1) % 12] == X: r += wh
                    if hX == h: r += .7 * wh
                if X in spec['kar']: r += .5
                dv += w * min(r, 2.0) / 2.0
            dv /= sum(wv[:len(da['vim'])] or [1])
            if pos:
                hit = sum((1.0 if i == 0 else .7) for i, h in enumerate(hs) if h == mh) / wsum
                own = 1.0 if (hm in hs or any(SLORD[(lr + h - 1) % 12] == lord for h in hs)) else 0.0
                good = 1.0 if (mh in (1,2,3,5,9,10,11) and hm not in (6,8,12)) else 0.0
                tj = .4 * hit + .3 * own + .3 * good
            else:
                tj = .5 * (mh in (6,8,12)) + .5 * (hm in (6,8,12))
            out[d] = np.array([sade, ashv, ch, dv, tj], float)
        return out
def build_new(p):
    fn = f"/home/claude/astro/tune/ncache/{p['name']}.pkl"
    if os.path.exists(fn): return pickle.load(open(fn, 'rb'))
    c = Chart(p['name'], p['local'], p['tz'], p['lat'], p['lon']); N = New(c)
    b = p['local'] - timedelta(hours=p['tz']); last = max(e[0] for e in p['events'])
    t0, t1 = b + timedelta(days=365.25 * 12), min(last + timedelta(days=730), b + timedelta(days=365.25 * 85))
    g = grid(c, t0, t1, 10); G = {d: np.zeros((len(g), len(NEW))) for d in DOM}
    for i, t in enumerate(g):
        v = N.vec(t)
        for d in DOM: G[d][i] = v[d]
    ev = []
    for ed, dom, lab in p['events']:
        if ed < t0 or dom not in DOM: continue
        ev.append(dict(dom=dom, date=str(ed.date()), x=N.vec(ed, [dom])[dom]))
    out = dict(name=p['name'], G=G, ev=ev); pickle.dump(out, open(fn, 'wb')); return out
if __name__ == '__main__':
    from multiprocessing import Pool
    import people_loader as L
    ps = L.load_all()
    with Pool(4) as pool: r = pool.map(build_new, ps)
    print('built', len(r))
