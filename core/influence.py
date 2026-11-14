"""HOUSE-SIGN INFLUENCE: the central model of the engine (decision 2026-11-14, Rajat / Gautam).
Every house is touched by 2 or 3 zodiac signs. For each native we compute, per house, a share for every sign it touches, from several
VIEWS of the same chart: D1 whole-sign, D1 equal-from-lagna, D1 equal-from-middle, Sripati, Porphyry, KP Placidus (Krishnamurti ayanamsa), and D9.
The sign with the biggest share is the MAIN influence, the others MINOR. Rules are never judged true/false on one sign only:
every rule gets a FIT between 0 and 1 = weighted share of views (and, for 'lord of house N', of the signs in that house) in which the rule holds.
View weights and the minor-sign cutoff are HYPOTHESES (config below) to be tuned on validation data, not facts."""
import swisseph as swe
import houses as H
SIGN_LORD = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SYSTEM_VIEWS = ('whole', 'equal_asc', 'equal_mid', 'sripati', 'porphyry', 'placidus')
DEFAULT_WEIGHTS = {'whole': 1, 'equal_asc': 1, 'equal_mid': 1, 'sripati': 1, 'porphyry': 1, 'placidus': 1, 'd9': 1}   # hypothesis: equal
MINOR_CUTOFF = 0.08      # a sign with under 8 percent share of a house is dropped from the report (about 2.4 deg of 30). Hypothesis.
def navamsha_sign(lon):
    s = int(lon % 360 // 30); n = int((lon % 30) // (30 / 9)); return ([0, 9, 6, 3][s % 4] + n) % 12

def bundle(jd_ut, lat, lon, positions, ayan='lahiri', weights=None):
    """positions: {planet_id 0..8: sidereal longitude (same ayanamsa as `ayan`)}."""
    w = dict(DEFAULT_WEIGHTS); w.update(weights or {})
    views = {}
    for sy in SYSTEM_VIEWS:
        if w[sy] <= 0: continue
        ch = H.build(jd_ut, lat, lon, sy, 'kp' if sy == 'placidus' else ayan)
        if sy == 'placidus':        # KP: planets sit where KP puts them; positions need the KP ayanamsa shift
            shift = H.ayanamsa_value(jd_ut, 'lahiri') - H.ayanamsa_value(jd_ut, 'kp') if ayan == 'lahiri' else 0.0
            pos = {p: (L + shift) % 360 for p, L in positions.items()}
        else: pos = positions
        views[sy] = {'weight': w[sy], 'spans': {h['h']: h['spans'] for h in ch['houses']}, 'planet_house': {p: H.house_of(L, ch) for p, L in pos.items()}}
    if w['d9'] > 0:
        asc = H.build(jd_ut, lat, lon, 'whole', ayan)['asc']; d9l = navamsha_sign(asc)
        views['d9'] = {'weight': w['d9'], 'spans': {h: [((d9l + h - 1) % 12, 30.0)] for h in range(1, 13)},
                       'planet_house': {p: (navamsha_sign(L) - d9l) % 12 + 1 for p, L in positions.items()}}
    tot = sum(v['weight'] for v in views.values())
    for v in views.values(): v['weight'] /= tot
    return views

def house_sign_shares(views):
    """{house: {sign_name: share}} sums to 1 per house; plus main/minor split."""
    out = {}
    for h in range(1, 13):
        sh = {}
        for v in views.values():
            width = sum(d for _, d in v['spans'][h])
            for s, d in v['spans'][h]: sh[s] = sh.get(s, 0) + v['weight'] * d / width
        keep = {s: x for s, x in sh.items() if x >= MINOR_CUTOFF}; z = sum(keep.values())
        order = sorted(keep, key=lambda s: -keep[s])
        out[h] = {'shares': {SIGNS[s]: round(keep[s] / z, 3) for s in order}, 'main': SIGNS[order[0]], 'minor': [SIGNS[s] for s in order[1:]]}
    return out

def planet_house_shares(views):
    """{planet: {house: share}}: weighted share of views that put the planet in each house."""
    res = {}
    for v in views.values():
        for p, h in v['planet_house'].items(): res.setdefault(p, {}).setdefault(h, 0.0); res[p][h] += v['weight']
    return res

def fit(norm, views, sign_of_planet):
    """Weighted fit (0..1) of a parsed rule (core/rules_norm.parse). None if the rule is not fully parsed.
    Each view is judged separately (so AND stays consistent inside one view), then views are averaged by weight.
    'N-th lord' counts every sign the N-th house touches, weighted by its share inside that view."""
    if norm['status'] != 'parsed': return None
    GROUPS = {'kendra': (1, 4, 7, 10), 'trikona': (1, 5, 9), 'dusthana': (6, 8, 12), 'upachaya': (3, 6, 10, 11)}
    total = 0.0
    for v in views.values():
        pf = 1.0
        for a in norm['atoms']:
            if a[0] == 'planet_in_house': pf *= 1.0 if v['planet_house'][a[1]] in a[2] else 0.0
            elif a[0] == 'planet_in_group': pf *= 1.0 if v['planet_house'][a[1]] in GROUPS[a[2]] else 0.0
            elif a[0] == 'planet_in_sign': pf *= 1.0 if sign_of_planet[a[1]] == a[2] else 0.0
            elif a[0] == 'conj': pf *= 1.0 if sign_of_planet[a[1]] == sign_of_planet[a[2]] else 0.0
            elif a[0] == 'lord_in_house':
                width = sum(d for _, d in v['spans'][a[1]]); x = 0.0
                for s, d in v['spans'][a[1]]:
                    if v['planet_house'][SIGN_LORD[s]] in a[2]: x += d / width
                pf *= x
        total += v['weight'] * pf
    return round(total, 4)
