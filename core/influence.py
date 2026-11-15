"""HOUSE-SIGN INFLUENCE: the central model of the engine (decision 2026-11-14, Rajat / Gautam).
Every house is touched by 2 or 3 zodiac signs. For each native we compute, per house, a share for every sign it touches, from several
VIEWS of the same chart: D1 whole-sign, D1 equal-from-lagna, D1 equal-from-middle, Sripati, Porphyry, KP Placidus (Krishnamurti ayanamsa), and D9.
The sign with the biggest share is the MAIN influence, the others MINOR. Rules are never judged true/false on one sign only:
every rule gets a FIT between 0 and 1 = weighted share of views (and, for 'lord of house N', of the signs in that house) in which the rule holds.
View weights and the minor-sign cutoff are HYPOTHESES (config below) to be tuned on validation data, not facts."""
import swisseph as swe
import houses as H
import dignity, yogas
SIGN_LORD = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SYSTEM_VIEWS = ('whole', 'equal_asc', 'equal_mid', 'sripati', 'porphyry', 'placidus')
DEFAULT_WEIGHTS = {'whole': 1, 'equal_asc': 1, 'equal_mid': 1, 'sripati': 1, 'porphyry': 1, 'placidus': 1, 'd9': 1}   # hypothesis: equal
MINOR_CUTOFF = 0.08      # a sign with under 8 percent share of a house is dropped from the report (about 2.4 deg of 30). Hypothesis.
def navamsha_sign(lon):
    return int(((lon % 360) * 9 % 360) // 30)      # Navamsha longitude = 9 x longitude (exact; avoids float error at navamsha borders)

def chart_views(lag_lon, pos_lon, weight, name, systems=('whole', 'equal_asc')):
    """House views for ANY chart (D9, other divisional charts) from its own lagna longitude and planet longitudes: the principle of the engine
    (every house touched by 2+ signs, main and minor) applies to every chart. 'whole' = one sign per house; 'equal_asc' = 30 deg houses from the chart's lagna degree.
    Weight is split equally between the systems. Sripati/Porphyry/KP need a real midheaven, which a divisional chart does not have, so they are not used here."""
    out = {}
    for sy in systems:
        start = (int(lag_lon // 30) * 30) if sy == 'whole' else lag_lon
        cus = [(start + 30 * i) % 360 for i in range(12)]
        sp = {i + 1: H.spans(cus[i], cus[(i + 1) % 12]) for i in range(12)}
        ph = {p: int(((L - start) % 360) // 30) + 1 for p, L in pos_lon.items()}
        out[name if sy == 'whole' else f'{name}_{sy}'] = {'weight': weight / len(systems), 'spans': sp, 'planet_house': ph}
    return out
def divisional_shares(charts, factors=None):
    """Main/minor house-sign shares for every divisional chart that has sign + degree for lagna and planets (core/charts.natal output).
    D9 is exact (checked against 9 x longitude). Other charts use the PyJHora degree inside the sign, which is NOT independently verified (status 'degree_unverified')."""
    res = {}
    for f, ch in charts.items():
        if factors and f not in factors: continue
        lag = ch['asc'][0] * 30 + ch['asc'][1]; pos = {p: ch[p][0] * 30 + ch[p][1] for p in range(9)}
        vs = chart_views(lag, pos, 1.0, f'D{f}'); tot = sum(v['weight'] for v in vs.values())
        for v in vs.values(): v['weight'] /= tot
        res[f'D{f}'] = {'status': 'sign_checked_degree_unverified' if f != 9 else 'exact', 'houses': house_sign_shares(vs, 0.01),
                        'planet_house_shares': {PN[p]: {str(h): round(x, 3) for h, x in sorted(d_.items())} for p, d_ in planet_house_shares(vs).items()}}
    return res
PN = {0: 'Sun', 1: 'Moon', 2: 'Mars', 3: 'Mercury', 4: 'Jupiter', 5: 'Venus', 6: 'Saturn', 7: 'Rahu', 8: 'Ketu'}
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
        # D9 obeys the same main/minor principle as D1: whole-sign view AND equal-from-D9-lagna-degree view (D9 longitude = 9 x longitude, exact for Navamsha). The total D9 weight is split in two.
        asc = H.build(jd_ut, lat, lon, 'whole', ayan)['asc']; d1l = [(int(asc // 30) % 12, 30.0)]
        for key, v in chart_views((asc * 9) % 360, {p: (L * 9) % 360 for p, L in positions.items()}, w['d9'], 'd9', ('whole', 'equal_asc')).items():
            v['lagna_spans'] = d1l; views[key] = v
    tot = sum(v['weight'] for v in views.values())
    for v in views.values(): v['weight'] /= tot
    return views

def house_sign_shares(views, cutoff=None):
    cutoff = MINOR_CUTOFF if cutoff is None else cutoff
    """{house: {sign_name: share}} sums to 1 per house; plus main/minor split."""
    out = {}
    for h in range(1, 13):
        sh = {}
        for v in views.values():
            width = sum(d for _, d in v['spans'][h])
            for s, d in v['spans'][h]: sh[s] = sh.get(s, 0) + v['weight'] * d / width
        keep = {s: x for s, x in sh.items() if x >= cutoff}; z = sum(keep.values())
        order = sorted(keep, key=lambda s: -keep[s])
        out[h] = {'shares': {SIGNS[s]: round(keep[s] / z, 3) for s in order}, 'main': SIGNS[order[0]], 'minor': [SIGNS[s] for s in order[1:]]}
    return out

def planet_house_shares(views):
    """{planet: {house: share}}: weighted share of views that put the planet in each house."""
    res = {}
    for v in views.values():
        for p, h in v['planet_house'].items(): res.setdefault(p, {}).setdefault(h, 0.0); res[p][h] += v['weight']
    return res

NAT_BEN = (4, 5, 3); NAT_MAL = (0, 2, 6, 7, 8)     # HYPOTHESIS (classical natural nature): Mercury counted benefic; Moon benefic if waxing (Moon-Sun elongation under 180), else malefic
def group_members(g, ctx):
    waxing = ((ctx['lon'][1] - ctx['lon'][0]) % 360) < 180
    m = set(NAT_BEN if g == 'benefic' else NAT_MAL)
    if (g == 'benefic') == waxing: m.add(1)
    return m
def _lord_signs(v, n): 
    sp = v['spans'][n]; w = sum(d for _, d in sp); return [(SIGN_LORD[s], d / w) for s, d in sp]
def _aspected(ph, h, by, ctx, skip=None):
    members = group_members(by[1], ctx) if by[0] == 'group' else set(by[1])
    return any(q != skip and q in members and dignity.aspects_planet(q, ph[q], h) for q in ph)
GROUPS = {'kendra': (1, 4, 7, 10), 'trikona': (1, 5, 9), 'dusthana': (6, 8, 12), 'upachaya': (3, 6, 10, 11)}
def _atom_val(a, v, sg, ctx):
    """Value 0..1 of one atom inside ONE house view. 'any' = OR (max), 'not' = 1 - value."""
    k = a[0]
    if k == 'planet_in_house': return 1.0 if v['planet_house'][a[1]] in a[2] else 0.0
    if k == 'planet_in_group': return 1.0 if v['planet_house'][a[1]] in GROUPS[a[2]] else 0.0
    if k == 'planet_in_sign': return 1.0 if sg[a[1]] == a[2] else 0.0
    if k == 'conj': return 1.0 if sg[a[1]] == sg[a[2]] else 0.0
    if k == 'dasha': return 1.0 if ctx[a[2]] == a[1] else 0.0
    if k == 'dasha_house_lord':
        width = sum(d for _, d in v['spans'][a[1]]); return sum(d / width for s, d in v['spans'][a[1]] if SIGN_LORD[s] in (ctx['maha'], ctx['antar']))
    if k == 'dignity': return 1.0 if a[2] in dignity.states(a[1], sg[a[1]]) else 0.0
    if k == 'aspects_house': return 1.0 if dignity.aspects_house(a[1], v['planet_house'][a[1]]) & set(a[2]) else 0.0
    if k == 'aspects_planet': return 1.0 if dignity.aspects_planet(a[1], v['planet_house'][a[1]], v['planet_house'][a[2]]) else 0.0
    if k == 'lord_in_house':
        width = sum(d for _, d in v['spans'][a[1]]); return sum(d / width for s, d in v['spans'][a[1]] if v['planet_house'][SIGN_LORD[s]] in a[2])
    if k == 'planet_from': return 1.0 if yogas.planet_from(a[1], a[2], sg, a[3]) else 0.0
    if k == 'planet_in_nak': return 1.0 if yogas.nak_of(ctx['lon'][a[1]]) in a[2] else 0.0
    if k == 'lagna_sign':
        sp = v.get('lagna_spans', v['spans'][1]); width = sum(d for _, d in sp); return sum(d / width for s, d in sp if s in a[1])
    if k == 'group_in_house': return 1.0 if any(v['planet_house'][q] in a[2] for q in group_members(a[1], ctx)) else 0.0
    if k == 'planet_with_group': return 1.0 if any(q != a[1] and v['planet_house'][q] == v['planet_house'][a[1]] for q in group_members(a[2], ctx)) else 0.0
    if k == 'planet_aspected_by': return 1.0 if _aspected(v['planet_house'], v['planet_house'][a[1]], a[2], ctx, a[1]) else 0.0
    if k == 'lord_with_group': return sum(w for l, w in _lord_signs(v, a[1]) if any(q != l and v['planet_house'][q] == v['planet_house'][l] for q in group_members(a[2], ctx)))
    if k == 'lord_aspected_by': return sum(w for l, w in _lord_signs(v, a[1]) if _aspected(v['planet_house'], v['planet_house'][l], a[2], ctx, l))
    if k == 'strength': return 1.0 if (ctx['strength'][a[1]] >= 1.0) == (a[2] == 'strong') else 0.0
    if k == 'retro': return 1.0 if a[1] in ctx['retro'] else 0.0
    if k == 'combust': return 1.0 if yogas.combust(a[1], ctx['lon'], ctx['retro']) else 0.0
    if k == 'yoga': return 1.0 if yogas.yoga(a[1], sg, v['planet_house']) else 0.0
    if k == 'any': return max(_atom_val(x, v, sg, ctx) for x in a[1])
    if k == 'not': return 1.0 - _atom_val(a[1], v, sg, ctx)
    raise ValueError(k)
NEED_LON = ('group_in_house', 'planet_with_group', 'planet_aspected_by', 'lord_with_group', 'lord_aspected_by')
def _needs(atoms):
    """What data an atom needs beyond the chart: 'maha' (running dasha), 'lon' (longitudes), 'retro' (birth retro flags)."""
    out = set()
    for a in atoms:
        k = a[0]
        if k.startswith('dasha'): out.add('maha')
        elif k == 'planet_in_nak' or k in NEED_LON: out.add('lon')
        elif k == 'strength': out.add('strength')
        elif k == 'retro': out.add('retro')
        elif k == 'combust': out |= {'lon', 'retro'}
        elif k == 'any': out |= _needs(a[1])
        elif k == 'not': out |= _needs((a[1],))
    return out
def fit(norm, views, sign_of_planet, ctx=None):
    """Weighted fit (0..1) of a parsed rule (core/rules_norm.parse, or validated AI atoms). None if not fully parsed or if a dasha is needed and no ctx is given.
    Each view is judged separately (so AND stays consistent inside one view), then views are averaged by weight.
    'N-th lord' counts every sign the N-th house touches, weighted by its share inside that view."""
    if norm['status'] != 'parsed': return None
    if _needs(norm['atoms']) - set(ctx or {}): return None            # missing data: never guess
    if norm.get('frame') == 'aries_fixed': return _fit_aries(norm, sign_of_planet, ctx)
    total = 0.0
    for v in views.values():
        pf = 1.0
        for a in norm['atoms']: pf *= _atom_val(a, v, sign_of_planet, ctx)
        total += v['weight'] * pf
    return round(total, 4)

def _aries_ok(a, sg, ctx):
    k = a[0]
    if k == 'planet_in_house': return sg[a[1]] + 1 in a[2]
    if k == 'planet_in_group': return sg[a[1]] + 1 in GROUPS[a[2]]
    if k == 'planet_in_sign': return sg[a[1]] == a[2]
    if k == 'conj': return sg[a[1]] == sg[a[2]]
    if k == 'lord_in_house': return sg[SIGN_LORD[a[1] - 1]] + 1 in a[2]
    if k == 'dasha': return ctx[a[2]] == a[1]
    if k == 'dasha_house_lord': return SIGN_LORD[a[1] - 1] in (ctx['maha'], ctx['antar'])
    if k == 'dignity': return a[2] in dignity.states(a[1], sg[a[1]])
    if k == 'aspects_house': return bool(dignity.aspects_house(a[1], sg[a[1]] + 1) & set(a[2]))
    if k == 'aspects_planet': return dignity.aspects_planet(a[1], sg[a[1]] + 1, sg[a[2]] + 1)
    if k == 'planet_from': return yogas.planet_from(a[1], a[2], sg, a[3])
    if k == 'planet_in_nak': return yogas.nak_of(ctx['lon'][a[1]]) in a[2]
    if k == 'lagna_sign': return 0 in a[1]          # Lal Kitab fixed frame: house 1 is Aries
    if k == 'group_in_house': return any(sg[q] + 1 in a[2] for q in group_members(a[1], ctx))
    if k == 'planet_with_group': return any(q != a[1] and sg[q] == sg[a[1]] for q in group_members(a[2], ctx))
    if k == 'planet_aspected_by': return _aspected({p: sg[p] + 1 for p in sg}, sg[a[1]] + 1, a[2], ctx, a[1])
    if k == 'lord_with_group': l = SIGN_LORD[a[1] - 1]; return any(q != l and sg[q] == sg[l] for q in group_members(a[2], ctx))
    if k == 'lord_aspected_by': l = SIGN_LORD[a[1] - 1]; return _aspected({p: sg[p] + 1 for p in sg}, sg[l] + 1, a[2], ctx, l)
    if k == 'strength': return (ctx['strength'][a[1]] >= 1.0) == (a[2] == 'strong')
    if k == 'retro': return a[1] in ctx['retro']
    if k == 'combust': return yogas.combust(a[1], ctx['lon'], ctx['retro'])
    if k == 'yoga': return yogas.yoga(a[1], sg, {p: sg[p] + 1 for p in sg})
    if k == 'any': return any(_aries_ok(x, sg, ctx) for x in a[1])
    if k == 'not': return not _aries_ok(a[1], sg, ctx)
    raise ValueError(k)
def _fit_aries(norm, sg, ctx=None):
    """Lal Kitab frame (decision 2026-11-14, OPEN QUESTION): house number = sign number counted from Aries. One view only, so fit is 0 or 1."""
    return 1.0 if all(_aries_ok(a, sg, ctx) for a in norm['atoms']) else 0.0
