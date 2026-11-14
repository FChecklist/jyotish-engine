"""Transit quality from the natal Moon (rules DB system 'gochara', BK13). Plain code. See docs/GUIDANCE_RULES.md section A."""
from guidance_rules import *
def house_from(moon_sign0, sign0): return (sign0 - moon_sign0) % 12 + 1
def _exempt(p, q): return frozenset({p, q}) in EXEMPT
def assess(moon_sign0, signs, bav=None, sav=None):
    """signs: {planet 0..8: sign0}. bav: 7 rows (Sun..Saturn) x 12 signs, sav: 12. Returns {planet: dict}."""
    hs = {p: house_from(moon_sign0, s) for p, s in signs.items()}
    out = {}
    for p, h in hs.items():
        good = h in FAV[p]; rules = ['BK13_0001']; vedha = None; cancelled = False
        if good and h in VEDHA[p]:
            v = VEDHA[p][h]
            for q, hq in hs.items():
                if q != p and hq == v and not _exempt(p, q): vedha = q; break
        if not good:   # GR-G6 vipareeta vedha: bad house that is the vedha point of a good house, with another planet in that good house
            for g, v in VEDHA[p].items():
                if v == h and any(q != p and hq == g and not _exempt(p, q) for q, hq in hs.items()): cancelled = True; rules.append('BK13_0020')
        if h == 11: res = 'favourable'; rules.append('BK13_0005')
        elif good and vedha is None: res = 'favourable'; rules.append('BK13_0010-0017')
        elif good: res = 'neutral'; rules.append('BK13_0018')
        elif cancelled: res = 'neutral'
        elif p in BENEFIC: res = 'neutral'; rules.append('BK13_0003')
        else: res = 'very_adverse' if h in (8, 12) else 'adverse'; rules.append('BK13_0006' if h in (8, 12) else 'BK13_0004')
        if p == 6 and h == 1: res = 'very_adverse'; rules.append('BK13_0007')
        if bav is not None and p <= 6:   # GR-G7
            b = bav[p][signs[p]]; s = sav[signs[p]]
            if b > 4 and s > 30: res = 'favourable'; rules.append('BK13_0029')
            elif (not good) and b < 4 and s < 30 and res != 'very_adverse': res = 'adverse'; rules.append('BK13_0030')
        out[p] = {'planet': PL[p], 'sign': SIGNS[signs[p]], 'house_from_moon': h, 'result': res, 'vedha_by': PL[vedha] if vedha is not None else None, 'rules': rules}
    return out
def moorthi(moon_house_at_ingress, planet):
    name = MOORTHI[moon_house_at_ingress]; ben, mal = MOORTHI_RESULT[name]
    return {'moorthi': name, 'result': ben if planet in BENEFIC else mal, 'rules': ['BK13_0032-0035']}
def combust(lons):
    """lons {planet: sidereal longitude}. Returns list of planets 4,5 within orb of Sun (GR-G9)."""
    out = []
    for p, orb in COMBUST_ORB.items():
        d = abs((lons[p] - lons[0] + 180) % 360 - 180)
        if d < orb: out.append({'planet': PL[p], 'separation_deg': round(d, 2), 'rules': ['BK13_0038']})
    return out
