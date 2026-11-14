"""Jyotish engine for ANY birth data. Four engines:
  1 predict_events   - which life areas are active when (windows, with technique agreement + natal promise)
  2 timing           - ranked windows / month-by-month heat per area
  3 dos_donts        - practical do / don't for a date, from running dashas + transits
  4 remedies         - optional, low-cost remedies (Lal Kitab / Gautam / traditional), never replace medical/legal/financial action
Techniques scored separately so each can be tested alone (ablation):
  vim   Parashari Vimshottari dasha (MD/AD/PD lords vs area houses)
  kp    KP significators of the dasha lords (houses 2-6-10-11 etc.)
  yog   Yogini dasha lords vs area houses
  chara Jaimini chara dasha signs vs area houses (rashi drishti)
  trans Double transit (Jupiter+Saturn) on area houses, Moon-gochar, node axis
All scores are z-normalised against the same chart's own life, so they rank windows; they are not probabilities.
"""
import sys, glob, json, re, datetime as dt
from datetime import timedelta
sys.path.insert(0, '/home/claude/astro')
import swisseph as swe
from ac import *
LAH = lambda: swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
LAH()
D = dt.datetime

def jd_utc(local, tz):
    u = local - timedelta(hours=tz)
    return swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)

def sign_of(x): return int((x % 360) // 30)
def in_arc(x, a, b):
    x %= 360; a %= 360; b %= 360
    return (a <= x < b) if a < b else (x >= a or x < b)
def house_of(x, cusps):
    for i in range(12):
        if in_arc(x, cusps[i], cusps[(i + 1) % 12]): return i + 1

def sub_lord(lon):
    L = 360 / 27; i = int(lon // L); f = (lon % L) / L
    start = VO[i % 9]; acc = 0
    for k in range(9):
        l = VO[(VO.index(start) + k) % 9]; acc += VY[l] / 120
        if f < acc: return l
    return start

# ---------- life areas: (parashari houses, primary first), KP houses, karakas, KP denial houses
DOM = {
 'career':    dict(h=[10, 6, 2, 11], kp=[2, 6, 10, 11], kar=['Sun', 'Saturn', 'Mercury'], deny=[5, 8, 12], pos=True),
 'status':    dict(h=[10, 1, 11, 9, 5], kp=[1, 10, 11], kar=['Sun', 'Jupiter'], deny=[8, 12], pos=True),
 'marriage':  dict(h=[7, 2, 11], kp=[2, 7, 11], kar=['Venus', 'Jupiter'], deny=[1, 6, 10], pos=True),
 'children':  dict(h=[5, 2, 11, 9], kp=[2, 5, 11], kar=['Jupiter'], deny=[1, 4, 10], pos=True),
 'property':  dict(h=[4, 11, 12], kp=[4, 11, 12], kar=['Mars', 'Venus'], deny=[3, 10], pos=True),
 'education': dict(h=[4, 5, 9, 11], kp=[4, 9, 11], kar=['Mercury', 'Jupiter'], deny=[8, 12], pos=True),
 'foreign':   dict(h=[12, 9, 3, 7], kp=[3, 9, 12], kar=['Rahu', 'Saturn'], deny=[2, 4, 11], pos=True),
 'setback':   dict(h=[8, 12, 6], kp=[6, 8, 12], kar=['Saturn', 'Rahu', 'Mars'], deny=[], pos=False),
}
W_TECH = dict(vim=.30, kp=.25, trans=.30, chara=.075, yog=.075)   # a-priori weights, fixed before any backtest

class Chart:
    def __init__(s, name, local, tz, lat, lon, gender=None):
        LAH()
        s.name, s.local, s.tz, s.lat, s.lon, s.gender = name, local, tz, lat, lon, gender
        s.jd = jd_utc(local, tz)
        s.birth = local - timedelta(hours=tz) + IST     # ac.py's dasha helpers expect IST-based datetimes
        s.P = planets(s.jd); s.asc = asc(s.jd, lat, lon); s.lag = sign_of(s.asc)
        s.hp = {p: (v['sign'] - s.lag) % 12 + 1 for p, v in s.P.items()}
        s.lord = {h: SLORD[(s.lag + h - 1) % 12] for h in range(1, 13)}
        s.owns = {p: [h for h in range(1, 13) if s.lord[h] == p] for p in s.P}
        s.star = {p: VO[v['nak'] % 9] for p, v in s.P.items()}
        s.mds, _ = vim_mds(s.P['Moon']['lon'], s.birth)
        s.ymds = yog_mds(s.P['Moon']['lon'], s.birth)
        s.cmds = chara_mds(s.lag, s.P, s.birth)
        s._kp()
        s._tc = {}
        s.promise = {d: s._promise(d) for d in DOM}

    # ----- KP
    def _kp(s):
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0); ayK = swe.get_ayanamsa_ut(s.jd)
        s.kcusp, ak = swe.houses_ex(s.jd, s.lat, s.lon, b'P', swe.FLG_SIDEREAL)
        LAH(); ayL = swe.get_ayanamsa_ut(s.jd)
        s.kpl = {p: (v['lon'] + ayL - ayK) % 360 for p, v in s.P.items()}
        s.khp = {p: house_of(x, s.kcusp) for p, x in s.kpl.items()}
        s.klord = {h: SLORD[sign_of(s.kcusp[h - 1])] for h in range(1, 13)}
        s.kowns = {p: [h for h in range(1, 13) if s.klord[h] == p] for p in s.P}
        s.ksub = {h: sub_lord(s.kcusp[h - 1]) for h in range(1, 13)}
        s.ksig = {}
        for p in s.P:
            st = sub_lord  # noqa
            starl = VO[int(s.kpl[p] // (360 / 27)) % 9]
            sg = {s.khp[p]} | set(s.kowns[p]) | ({s.khp[starl]} | set(s.kowns[starl]) if starl in s.P else set())
            if p in ('Rahu', 'Ketu'):
                dl = SLORD[sign_of(s.kpl[p])]; sg |= set(s.kowns[dl]) | {s.khp[dl]}
            s.ksig[p] = sg

    # ----- natal promise per area (-1..+1): lord dignity/placement, benefic support, KP cusp sub-lord
    def _promise(s, d):
        spec = DOM[d]; sc = []
        for i, h in enumerate(spec['h'][:3]):
            lh = s.lord[h]; sg = s.P[lh]['sign']; v = 0
            if sg == EXALT.get(lh, -1) or sg in OWN.get(lh, []): v += 1
            elif sg == DEBIL.get(lh, -1): v -= 1
            hh = s.hp[lh]
            v += 0.5 if hh in (1, 4, 5, 7, 9, 10, 11, 2) else (-0.5 if hh in (6, 8, 12) else 0)
            occ = [p for p in s.P if s.hp[p] == h]
            v += 0.4 * sum(1 for p in occ if p in ('Jupiter', 'Venus', 'Mercury', 'Moon'))
            v -= 0.3 * sum(1 for p in occ if p in ('Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun')) if spec['pos'] else 0
            sc.append(v * (1 if i == 0 else .6))
        nat = sum(sc) / 2.2
        sl = s.ksub[spec['kp'][0] if d != 'career' else 10]
        kpv = len(s.ksig[sl] & set(spec['kp'])) / len(spec['kp']) - (0.5 if s.ksig[sl] & set(spec['deny']) and spec['pos'] else 0)
        return max(-1, min(1, 0.6 * nat + 0.4 * (2 * kpv - 1)))

    # ----- planet relation to an area
    def rel(s, X, d):
        spec = DOM[d]; r = 0
        for i, h in enumerate(spec['h']):
            w = 1.0 if i == 0 else .7
            if h in s.owns[X]: r += w
            if s.hp[X] == h: r += .7 * w
            sl = s.star[X]
            if sl != X and (h in s.owns[sl] or s.hp[sl] == h): r += .4 * w
            if X in ('Rahu', 'Ketu'):
                dl = SLORD[s.P[X]['sign']]
                if h in s.owns[dl]: r += .6 * w
        if X in spec['kar']: r += .5
        return min(r, 2.0) / 2.0

    def kprel(s, X, d):
        spec = DOM[d]; sg = s.ksig[X]
        v = len(sg & set(spec['kp'])) / len(spec['kp'])
        if spec['pos'] and sg & set(spec['deny']): v -= 0.25
        return max(0, v)

    # ----- dasha-based scores at time t (t is a UTC-naive datetime shifted to IST frame like ac.py: use birth-frame)
    def _frame(s, t): return t + IST    # t given in UTC-naive; ac helpers use IST-frame
    def dasha(s, t):
        T = s._frame(t); v = vim_at(s.mds, T, 3) or []; y = yog_at(s.ymds, T) or []; c = chara_at(s.cmds, T) or []
        return dict(vim=[x[0] for x in v], vim_dates=v, yog=[x[0] for x in y], chara=c)

    def tpos(s, t):
        k = t.date()
        if k not in s._tc:
            s._tc[k] = planets(swe.julday(t.year, t.month, t.day, 12))
        return s._tc[k]

    def tech_scores(s, t, doms=None):
        """raw 0..1 scores per technique for each area at UTC-naive time t"""
        da = s.dasha(t); T = s.tpos(t); out = {}
        yl = {'Mangala': 'Moon', 'Pingala': 'Sun', 'Dhanya': 'Jupiter', 'Bhramari': 'Mars', 'Bhadrika': 'Mercury', 'Ulka': 'Saturn', 'Siddha': 'Venus', 'Sankata': 'Rahu'}
        js, ss = T['Jupiter']['sign'], T['Saturn']['sign']
        ms = s.P['Moon']['sign']
        for d in (doms or DOM):
            spec = DOM[d]; hs = spec['h']; wsum = sum(1.0 if i == 0 else .7 for i in range(len(hs)))
            wts = [1.0 if i == 0 else .7 for i in range(len(hs))]
            v = da['vim']; wv = (3, 3, 1.5)
            vim = sum(w * s.rel(x, d) for w, x in zip(wv, v)) / sum(wv[:len(v)] or [1])
            kp = sum(w * s.kprel(x, d) for w, x in zip((2, 3, 2), v)) / sum((2, 3, 2)[:len(v)] or [1])
            yg = [yl[x] for x in da['yog']] if da['yog'] else []
            yog = sum(w * s.rel(x, d) for w, x in zip((3, 3), yg)) / (sum((3, 3)[:len(yg)]) or 1)
            ch = 0
            if da['chara']:
                for (sg, a, b), w in zip(da['chara'], (1, 1)):
                    best = 0
                    for h, wh in zip(hs, wts):
                        H = (s.lag + h - 1) % 12; lsg = s.P[s.lord[h]]['sign']
                        c = 1.0 if sg == H else (.7 if H in jaim_aspects(sg) else 0)
                        c = max(c, .5 if (sg == lsg or lsg in jaim_aspects(sg)) else 0)
                        best += wh * c
                    ch += best / wsum
                ch /= 2
            # transit: double transit from lagna and from Moon, node axis, gochar
            def dbl(base):
                tot = 0
                for h, wh in zip(hs, wts):
                    H = (base + h - 1) % 12
                    J = 1.0 if (js == H or H in ((js + 4) % 12, (js + 6) % 12, (js + 8) % 12)) else 0
                    S = 1.0 if (ss == H or H in ((ss + 2) % 12, (ss + 6) % 12, (ss + 9) % 12)) else 0
                    tot += wh * (.35 * (J + S) / 2 * 2 * .5 + .65 * J * S)
                return tot / wsum
            nodes = 0
            for h, wh in zip(hs[:2], wts[:2]):
                H = (s.lag + h - 1) % 12
                if T['Rahu']['sign'] == H or T['Ketu']['sign'] == H: nodes += wh * .5
            hj, hsat = (js - ms) % 12 + 1, (ss - ms) % 12 + 1
            if spec['pos']:
                gj = 1.0 if hj in (2, 5, 7, 9, 11) else 0; gs = 1.0 if hsat in (3, 6, 11) else 0
                g = (gj + gs) / 2
            else:
                g = (1.0 if hsat in (12, 1, 2, 8, 4) else 0) * .7 + (.3 if hj not in (2, 5, 7, 9, 11) else 0)
            tr = .55 * dbl(s.lag) + .2 * dbl(ms) + .15 * g + .1 * min(nodes, 1)
            out[d] = dict(vim=vim, kp=kp, yog=yog, chara=ch, trans=tr)
        return out

def grid(c, start, end, step=10):
    t = start; out = []
    while t <= end:
        out.append(t); t += timedelta(days=step)
    return out

def life_stats(c, doms=None, step=10, a0=12, a1=80):
    """mean/std of each technique per area over the chart's own life grid (for z-normalisation)"""
    b = c.local - timedelta(hours=c.tz)
    g = grid(c, b + timedelta(days=365.25 * a0), b + timedelta(days=365.25 * a1), step)
    rows = [c.tech_scores(t, doms) for t in g]
    import statistics as st
    S = {}
    for d in (doms or DOM):
        S[d] = {}
        for k in W_TECH:
            xs = [r[d][k] for r in rows]; m = st.mean(xs); sd = st.pstdev(xs) or 1e-9
            S[d][k] = (m, sd)
    return S, g, rows

def zscore(row, S, w=None):
    w = w or W_TECH; z = {}
    for d, tv in row.items():
        z[d] = {k: (tv[k] - S[d][k][0]) / S[d][k][1] for k in W_TECH}
        z[d]['all'] = sum(w[k] * z[d][k] for k in W_TECH)
    return z
