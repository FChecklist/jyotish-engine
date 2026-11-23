"""Owner colour rules of 23 Nov 2026 (OWNER-2026-11-23-A) with D1 Final (D1 + KP + Bhav Chalit) and D9 validation.
Plain if/then code, no AI. Rules: data/owner_colour_rules.csv. Owner text verbatim: docs/OWNER_RULES_2026-11-23.md. Spec: docs/OWNER_COLOUR_RULES.md.
A tradition claim, not a measured fact. SUPERSEDES the 21 Nov table (core/planet_negatives.py) where they differ.

Flow (all inputs are sidereal longitudes from the calculator; nothing here recalculates a chart except the house cusps):
1. Three sign maps (views). D1 = sign of the longitude. Bhav Chalit (BC) = equal houses, house h spans lagna + 30(h-1) +/- 15.
   KP = sidereal Placidus houses. In KP and BC the planet's EFFECTIVE sign = lagna sign + (house - 1).
2. In each view a rule fires on a zodiac (sign) when its planet SITS in a trigger sign (weight PLACEMENT_HIT_WEIGHT = 1.0) or ASPECTS a trigger sign
   (weight ASPECT_HIT_WEIGHT = 0.5, ASSUMPTION, owner has not confirmed). Aspects are counted forward by house number: n-th = (sign + n - 1).
3. D1 Final weight of (zodiac, rule) = 0.5 x D1 + 0.25 x KP + 0.25 x BC.
4. Colour advice per zodiac = union of use colours minus union of avoid colours (of every rule that fires there). If nothing pure remains, or two or more
   rules fire on the zodiac, blends are proposed too (BLENDS); a blend that lands on an avoid colour is rejected.
5. D9: the same rules are re-run on D9 signs. A colour that is an avoid colour of a D9 rule firing on the same zodiac is anti and is removed;
   when anything is anti, a mix is proposed whose result is acceptable in D1 Final and in D9 together."""
import csv
import json
import math
import numbers
import os
from zodiac import SIGNS, sign_of
from planet_negatives import canonical_planet, sign_index

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'owner_colour_rules.csv')
COLUMNS = ['rule_no', 'planet', 'trigger_signs', 'use_colours', 'avoid_colours', 'source', 'note']
SOURCE = 'OWNER-2026-11-23-A'

PLACEMENT_HIT_WEIGHT = 1.0   # owner: "the 100% main effect is when that planet is sitting in that zodiac"
ASPECT_HIT_WEIGHT = 0.5      # ASSUMPTION, owner has not confirmed: "the effect reduces if its not directly in that zodiac" gives no number
VIEW_WEIGHTS = {'D1': 0.5, 'KP': 0.25, 'BC': 0.25}   # owner: "D1 Final - 50% is D1, 25% is KP and 25% is Bhav Chalit"
assert abs(sum(VIEW_WEIGHTS.values()) - 1.0) < 1e-12

# House numbers each planet looks at, counted from the planet's own house (1 = where it sits). Owner's list, 23 Nov 2026.
ASPECTS = {'Sun': (1, 7), 'Moon': (1, 7), 'Mercury': (1, 7), 'Venus': (1, 7), 'Mars': (1, 4, 7, 8), 'Jupiter': (1, 5, 7, 9), 'Saturn': (1, 3, 7, 10),
           'Rahu': (1, 7), 'Ketu': (1, 7), 'Uranus': (1, 7), 'Neptune': (1, 7), 'Pluto': (1, 7)}
COLOURS = ('blue', 'red', 'yellow', 'green', 'black', 'grey', 'purple', 'white', 'orange', 'brown', 'silver', 'golden')
# Colour mixing used to reach a specific colour (brief of 23 Nov 2026). (component, component, result).
BLEND_LIST = (('blue', 'yellow', 'green'), ('red', 'yellow', 'orange'), ('red', 'blue', 'purple'), ('black', 'white', 'grey'), ('red', 'green', 'brown'))
BLENDS = {frozenset((a, b)): r for a, b, r in BLEND_LIST}


# ---------------------------------------------------------------- rules table
def load_rules(path=None):
    """Read and validate data/owner_colour_rules.csv. Returns a list of rule dicts sorted by rule_no. Raises ValueError on a bad row."""
    with open(path or DATA_PATH, newline='', encoding='utf-8') as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != COLUMNS:
            raise ValueError('owner_colour_rules columns are %r, expected %r' % (rd.fieldnames, COLUMNS))
        rows = list(rd)
    out, seen = [], set()
    for i, r in enumerate(rows, start=2):  # line 1 is the header
        if None in r or any(r.get(c) is None for c in COLUMNS):
            raise ValueError('line %d: row must have exactly %d cells' % (i, len(COLUMNS)))
        try:
            r['rule_no'] = int(r['rule_no'])
        except ValueError:
            raise ValueError('line %d: bad rule_no %r' % (i, r['rule_no']))
        for c in ('trigger_signs', 'use_colours', 'avoid_colours'):
            r[c] = json.loads(r[c])
        if r['rule_no'] in seen:
            raise ValueError('line %d: duplicate rule_no %d' % (i, r['rule_no']))
        seen.add(r['rule_no'])
        if r['planet'] != canonical_planet(r['planet']) or r['planet'] not in ASPECTS:
            raise ValueError('line %d: planet %r is not a canonical planet name' % (i, r['planet']))
        if not r['trigger_signs'] or any(s not in SIGNS for s in r['trigger_signs']) or len(set(r['trigger_signs'])) != len(r['trigger_signs']):
            raise ValueError('line %d: bad trigger_signs %r' % (i, r['trigger_signs']))
        for c in ('use_colours', 'avoid_colours'):
            if not r[c] or any(x not in COLOURS for x in r[c]) or len(set(r[c])) != len(r[c]):
                raise ValueError('line %d: bad %s %r' % (i, c, r[c]))
        if set(r['use_colours']) & set(r['avoid_colours']):
            raise ValueError('line %d: a colour is both used and avoided: %r' % (i, sorted(set(r['use_colours']) & set(r['avoid_colours']))))
        out.append(r)
    return sorted(out, key=lambda r: r['rule_no'])


# ---------------------------------------------------------------- longitudes -> sign maps (views)
def _lon(x):
    if isinstance(x, bool) or not isinstance(x, numbers.Real) or not math.isfinite(x):
        raise ValueError('bad longitude %r' % (x,))
    return float(x) % 360


def navamsha_sign(lon):
    """D9 sign index (same formula as core/influence.navamsha_sign: navamsha longitude = 9 x longitude, exact)."""
    return int((_lon(lon) * 9 % 360) // 30)


def bhav_chalit_house(lon, lagna_lon):
    """Equal-house Bhav Chalit: house h spans lagna + 30(h-1) - 15 up to lagna + 30(h-1) + 15 (start inclusive). Returns 1..12."""
    return int(((_lon(lon) - _lon(lagna_lon) + 15) % 360) // 30) + 1


def kp_house(lon, cusps):
    """Placidus (KP) house 1..12 of a longitude. cusps = 12 house-start longitudes in order (cusp 1 first). Start inclusive."""
    cusps = [_lon(c) for c in cusps]
    if len(cusps) != 12:
        raise ValueError('need 12 cusps, got %d' % len(cusps))
    widths = [(cusps[(i + 1) % 12] - cusps[i]) % 360 for i in range(12)]
    if any(w == 0 for w in widths) or abs(sum(widths) - 360) > 1e-6:
        raise ValueError('cusps must run once round the circle in order')
    x = _lon(lon)
    for i in range(12):
        if (x - cusps[i]) % 360 < widths[i] - 1e-9:
            return i + 1
    return 12


def kp_cusps(jd_ut, lat, lon, ayanamsa='lahiri'):
    """Sidereal Placidus house starts (KP). Uses core/houses.py (Swiss Ephemeris), the same calculator as the rest of the engine; ayanamsa is a parameter
    ('lahiri' default, 'kp', 'raman', 'fagan_bradley'). Placidus is undefined inside the polar circles: raises ValueError, never falls back."""
    if ayanamsa == 'tropical':
        raise ValueError('KP houses here are sidereal; pass an ayanamsa, not tropical')
    import houses as H     # lazy: the rule logic above needs no ephemeris
    return [h['start'] for h in H.build(jd_ut, lat, lon, 'placidus', ayanamsa)['houses']]


def effective_sign(lagna_sign, house):
    """Planet's sign in KP / Bhav Chalit = lagna sign + (house - 1)."""
    return (lagna_sign + house - 1) % 12


def build_views(lagna_lon, longitudes, kp_cusp_list):
    """longitudes: {planet name: sidereal longitude}. Returns {'views': {'D1','KP','BC'} -> {planet: sign index}, 'houses': {'D1','KP','BC'} -> {planet: house},
    'd9': {planet: sign index}, 'moved': [planets whose house in KP or BC differs from D1]}. Planet aliases (Indra, Varun, Yum) are accepted."""
    lag = _lon(lagna_lon)
    lagna_sign = sign_of(lag)
    if abs((_lon(kp_cusp_list[0]) - lag + 180) % 360 - 180) > 1e-6:
        raise ValueError('KP cusp 1 must equal the lagna longitude')
    views = {'D1': {}, 'KP': {}, 'BC': {}}
    houses = {'D1': {}, 'KP': {}, 'BC': {}}
    d9 = {}
    for name, x in longitudes.items():
        p = canonical_planet(name)
        if p not in ASPECTS:
            raise ValueError('no rule for planet %r' % (name,))
        if p in d9:
            raise ValueError('planet %r given twice (aliases count as the same planet)' % p)
        x = _lon(x)
        s = sign_of(x)
        houses['D1'][p] = (s - lagna_sign) % 12 + 1
        houses['KP'][p] = kp_house(x, kp_cusp_list)
        houses['BC'][p] = bhav_chalit_house(x, lag)
        views['D1'][p] = s
        views['KP'][p] = effective_sign(lagna_sign, houses['KP'][p])
        views['BC'][p] = effective_sign(lagna_sign, houses['BC'][p])
        d9[p] = navamsha_sign(x)
    moved = sorted(p for p in houses['D1'] if houses['KP'][p] != houses['D1'][p] or houses['BC'][p] != houses['D1'][p])
    return {'views': views, 'houses': houses, 'd9': d9, 'moved': moved}


# ---------------------------------------------------------------- rule hits
def hits_in_view(signs, rules):
    """signs: {planet: sign (name or index)}. Returns a list of hits {rule_no, planet, zodiac, kind, aspect_number, from_sign, weight}.
    kind 'placement' (planet sits in a trigger sign, weight PLACEMENT_HIT_WEIGHT) or 'aspect' (n-th house from it is a trigger sign, weight ASPECT_HIT_WEIGHT)."""
    out = []
    for name, sg in signs.items():
        p = canonical_planet(name)
        if p not in ASPECTS:
            raise ValueError('no rule for planet %r' % (name,))
        s0 = sign_index(sg)
        for r in rules:
            if r['planet'] != p:
                continue
            for n in ASPECTS[p]:
                z = SIGNS[(s0 + n - 1) % 12]
                if z in r['trigger_signs']:
                    out.append({'rule_no': r['rule_no'], 'planet': p, 'zodiac': z, 'kind': 'placement' if n == 1 else 'aspect',
                                'aspect_number': None if n == 1 else n, 'from_sign': SIGNS[s0],
                                'weight': PLACEMENT_HIT_WEIGHT if n == 1 else ASPECT_HIT_WEIGHT})
    return sorted(out, key=lambda h: (SIGNS.index(h['zodiac']), h['rule_no'], h['aspect_number'] or 0))


def d1_final(views, rules):
    """Combine the three views. views = {'D1': signs, 'KP': signs, 'BC': signs} (all three required).
    Returns {zodiac: [ {rule_no, planet, weight (D1 Final), by_view {D1, KP, BC}, detail {view: [hit, ...]}} ]} for zodiacs whose final weight > 0."""
    if set(views) != set(VIEW_WEIGHTS):
        raise ValueError('views must be exactly %s, got %s' % (sorted(VIEW_WEIGHTS), sorted(views)))
    per = {}
    for v in VIEW_WEIGHTS:
        for h in hits_in_view(views[v], rules):
            e = per.setdefault((h['zodiac'], h['rule_no']), {'rule_no': h['rule_no'], 'planet': h['planet'], 'by_view': {x: 0.0 for x in VIEW_WEIGHTS},
                                                            'detail': {x: [] for x in VIEW_WEIGHTS}})
            e['by_view'][v] += h['weight']
            e['detail'][v].append({k: h[k] for k in ('kind', 'aspect_number', 'from_sign', 'weight')})
    out = {}
    for (z, _), e in per.items():
        e['weight'] = sum(VIEW_WEIGHTS[v] * e['by_view'][v] for v in VIEW_WEIGHTS)
        if e['weight'] > 0:
            out.setdefault(z, []).append(e)
    return {z: sorted(es, key=lambda e: e['rule_no']) for z, es in sorted(out.items(), key=lambda kv: SIGNS.index(kv[0]))}


# ---------------------------------------------------------------- colour advice
def _union(rules_hit, key):
    out = []
    for r in rules_hit:
        for c in r[key]:
            if c not in out:
                out.append(c)
    return out


def blend_options(pool, avoid, must_use_one_of=None):
    """Blends whose two components are both in `pool` and whose RESULT is not in `avoid`. A blend that lands on an avoid colour is rejected.
    must_use_one_of: if given, at least one component must come from it. `uses_avoided_component` marks blends that need an avoided colour as an ingredient
    (only the result is checked, the owner has not said whether an avoided colour may be an ingredient)."""
    out = []
    for a, b, res in BLEND_LIST:
        if a in pool and b in pool and res not in avoid and (must_use_one_of is None or a in must_use_one_of or b in must_use_one_of):
            out.append({'components': [a, b], 'result': res, 'uses_avoided_component': bool({a, b} & set(avoid))})
    return out


def zodiac_advice(hit_rules):
    """hit_rules: the rule dicts that fire on one zodiac. Returns the colour advice for that zodiac."""
    use, avoid = _union(hit_rules, 'use_colours'), _union(hit_rules, 'avoid_colours')
    pure = [c for c in use if c not in avoid]
    n = len(hit_rules)
    blend_needed = n >= 2 or not pure
    blends = blend_options(use, avoid) if blend_needed else []
    recommended = ([{'colours': b['components'], 'result': b['result']} for b in blends] if n >= 2 else []) + [{'colours': [c], 'result': c} for c in pure]
    if n < 2:   # one negative: pure colours first; blends only if nothing pure remains
        recommended += [{'colours': b['components'], 'result': b['result']} for b in blends]
    return {'rules': [r['rule_no'] for r in hit_rules], 'n_negatives': n, 'use_union': use, 'avoid_union': avoid, 'pure_colours': pure,
            'blend_needed': blend_needed, 'blends': blends, 'blend_unavailable': bool(blend_needed and not blends), 'recommended': recommended}


def advise(final, rules):
    """final: output of d1_final. Returns {zodiac: {'weight_total', 'hits', **zodiac_advice}}."""
    by_no = {r['rule_no']: r for r in rules}
    out = {}
    for z, hits in final.items():
        a = zodiac_advice([by_no[h['rule_no']] for h in hits])
        a['weight_total'] = sum(h['weight'] for h in hits)
        a['hits'] = hits
        out[z] = a
    return out


# ---------------------------------------------------------------- D9 validation
def validate_d9(advice, d9_signs, rules):
    """advice: output of advise (D1 Final). d9_signs: {planet: D9 sign}. The rules are re-run on the D9 signs. For every D1 Final zodiac:
    anti colours = suggested colours that are an avoid colour of a D9 rule firing on the SAME zodiac. They are removed (blends are removed when their result is anti).
    If anything is anti, a mix is proposed: a blend of colours from the D1 Final use list and the D9 use list (at least one from D1 Final) whose result is an avoid
    colour in neither D1 Final nor D9, so it satisfies both. Status: approved (nothing anti) | adjusted (something anti, colours or a mix remain) | unresolved."""
    by_no = {r['rule_no']: r for r in rules}
    d9_hits = {}
    for h in hits_in_view(d9_signs, rules):
        d9_hits.setdefault(h['zodiac'], []).append(h)
    out = {}
    for z, a in advice.items():
        hz = d9_hits.get(z, [])
        d9_rules = [by_no[n] for n in sorted({h['rule_no'] for h in hz})]
        avoid9, use9 = _union(d9_rules, 'avoid_colours'), _union(d9_rules, 'use_colours')
        anti = [o for o in a['recommended'] if o['result'] in avoid9]
        kept = [o for o in a['recommended'] if o['result'] not in avoid9]
        mix = []
        if anti:
            avoid_all = list(dict.fromkeys(a['avoid_union'] + avoid9))
            mix = blend_options(list(dict.fromkeys(a['use_union'] + use9)), avoid_all, must_use_one_of=a['use_union'])
            known = [(o['colours'], o['result']) for o in kept]
            mix = [m for m in mix if (m['components'], m['result']) not in known]
        status = 'approved' if not anti else ('adjusted' if (kept or mix) else 'unresolved')
        out[z] = {'status': status, 'd9_hits': hz, 'd9_use': use9, 'd9_avoid': avoid9,
                  'anti_colours': sorted({o['result'] for o in anti}), 'kept': kept, 'mix': mix,
                  'final_recommended': kept + [{'colours': m['components'], 'result': m['result']} for m in mix]}
    return out


# ---------------------------------------------------------------- full pipeline
def analyse(lagna_lon, longitudes, kp_cusp_list=None, jd_ut=None, lat=None, lon=None, ayanamsa='lahiri', rules=None):
    """Whole flow for one chart. longitudes: {planet name: sidereal longitude, same ayanamsa as `ayanamsa`}; planets not supplied are not evaluated.
    KP cusps: pass kp_cusp_list, or jd_ut + lat + lon (computed by kp_cusps with `ayanamsa`)."""
    rules = load_rules() if rules is None else rules
    if kp_cusp_list is None:
        if jd_ut is None or lat is None or lon is None:
            raise ValueError('give kp_cusp_list, or jd_ut + lat + lon for the Placidus cusps')
        kp_cusp_list = kp_cusps(jd_ut, lat, lon, ayanamsa)
    b = build_views(lagna_lon, longitudes, kp_cusp_list)
    final = d1_final(b['views'], rules)
    adv = advise(final, rules)
    return {'source': SOURCE, 'ayanamsa': ayanamsa, 'view_weights': dict(VIEW_WEIGHTS), 'aspect_hit_weight': ASPECT_HIT_WEIGHT,
            'lagna_sign': SIGNS[sign_of(_lon(lagna_lon))], 'views': {v: {p: SIGNS[s] for p, s in m.items()} for v, m in b['views'].items()},
            'houses': b['houses'], 'moved_from_d1': b['moved'], 'd9_signs': {p: SIGNS[s] for p, s in b['d9'].items()},
            'zodiacs': adv, 'd9_validation': validate_d9(adv, b['d9'], rules)}
