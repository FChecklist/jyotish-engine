"""Aspect strength: final aspect % = (P1 + P2 + P3 + P4) / 4, each principle scored 0..100.

Source: owner message OWNER-2026-11-23-B (Cloudflare D1 jyotish-rules, table owner_method_text). Plain maths, no AI.
Input is sidereal longitudes the calculator already gave us (we do not recompute charts). Aspects are DIRECTIONAL for
P1, P3 and P4 (planet A looks FORWARD at planet B); P2 (western) is symmetric.

P1  owner degree ladder. Aspect angle = (n-1)*30 forward from A, n = aspect house:
      all planets 7th (180); Mars 4/7/8 (90/180/210); Jupiter 5/7/9 (120/180/240); Saturn 3/7/10 (60/180/270).
      deviation <= 5% of the angle -> 100, <= 10% -> 75, <= 15% -> 50, else 0.
      The owner wrote "+/-5%". Default reading: PERCENT OF THE ASPECT ANGLE (7th: 9/18/27 deg). Alternative reading:
      ABSOLUTE DEGREES (7th: 5/10/15 deg). mode='percent_of_angle' | 'absolute_degrees'. OPEN QUESTION for the owner.
      Conjunction (angle 0) is not in the owner's P1 text, so P1 gives it 0 (percent of 0 is undefined).
P2  western. conjunction 0 (orb 8), sextile 60 (6), square 90 (8), trine 120 (8), opposition 180 (8). Linear: 100 at
      exact, 0 at the orb edge. Rahu-Ketu pair is skipped (always exactly 180, no information).
P3  Vedic graha drishti, SIGN based (houses counted from A's sign). Same sign (conjunction) = 100; full (100) on the
      owner's list (Sun/Moon/Mercury/Venus/Rahu/Ketu/Uranus/Neptune/Pluto: 7; Mars 4,7,8; Jupiter 5,7,9; Saturn 3,7,10);
      Parashara partials for the 7 classical planets only: 3rd/10th = 25, 5th/9th = 50, 4th/8th = 75, if not already full.
P4  Lal Kitab. PENDING: no verified table exists. p4_lal_kitab() returns None. While P4 is None the result is a LOWER
      BOUND (P4 counted as 0) and is labelled so; final_range_if_p4_known gives the possible span (P4 in 0..100).
"""
import itertools

SIGN_CODES = ['Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi']     # codes the site shows
_SIGN_IDX = {c: i for i, c in enumerate(SIGN_CODES)}

# House numbers each body aspects, counted forward from its own sign (1 = same sign). Owner list, message A/B.
OWNER_ASPECTS = {
    'Sun': (7,), 'Moon': (7,), 'Mercury': (7,), 'Venus': (7,),
    'Mars': (4, 7, 8), 'Jupiter': (5, 7, 9), 'Saturn': (3, 7, 10),
    'Rahu': (7,), 'Ketu': (7,), 'Uranus': (7,), 'Neptune': (7,), 'Pluto': (7,),
}
CLASSICAL = frozenset({'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'})
PARASHARA_PARTIAL = {3: 25, 10: 25, 5: 50, 9: 50, 4: 75, 8: 75}
LADDER = ((5.0, 100), (10.0, 75), (15.0, 50))          # (max deviation in % or deg, score)
WESTERN = ((0, 8.0, 'conjunction'), (60, 6.0, 'sextile'), (90, 8.0, 'square'), (120, 8.0, 'trine'), (180, 8.0, 'opposition'))
MODES = ('percent_of_angle', 'absolute_degrees')
_EPS = 1e-9


def _norm(lon):
    return float(lon) % 360.0


def sign_of(lon):
    return int(_norm(lon) // 30)


def aspect_angle(n):
    """Aspect house n (1-based) -> exact angle forward from the aspecting planet."""
    return (n - 1) * 30


def _ladder(dev, exact, mode):
    if mode == 'percent_of_angle':
        if exact == 0:
            return 0
        measure_ok = lambda limit: dev <= exact * limit / 100.0 + _EPS
    elif mode == 'absolute_degrees':
        measure_ok = lambda limit: dev <= limit + _EPS
    else:
        raise ValueError('mode must be one of %s' % (MODES,))
    for limit, score in LADDER:
        if measure_ok(limit):
            return score
    return 0


def _check_body(a):
    if a not in OWNER_ASPECTS:
        raise ValueError('unknown body %r; known: %s' % (a, sorted(OWNER_ASPECTS)))


def p1_owner_ladder(a, lon_a, lon_b, mode='percent_of_angle'):
    """P1: best ladder score over the aspects planet `a` has. Returns (score, aspect_house or None)."""
    _check_body(a)
    forward = (_norm(lon_b) - _norm(lon_a)) % 360.0
    best, best_n = 0, None
    for n in OWNER_ASPECTS[a]:
        exact = aspect_angle(n)
        dev = abs(forward - exact)
        dev = min(dev, 360.0 - dev)                      # wrap-around (e.g. 359.9 vs 0)
        s = _ladder(dev, exact, mode)
        if s > best:
            best, best_n = s, n
    return best, best_n


def p2_western(lon_a, lon_b):
    """P2: strongest western aspect, linear to 0 at the orb edge. Returns (score 0..100, name or None, orb_deg or None)."""
    d = abs(_norm(lon_a) - _norm(lon_b)) % 360.0
    d = min(d, 360.0 - d)
    best, name, orb_used = 0.0, None, None
    for angle, orb, nm in WESTERN:
        o = abs(d - angle)
        if o <= orb + _EPS:
            v = 100.0 * (1.0 - o / orb)
            if v > best:
                best, name, orb_used = v, nm, o
    return max(best, 0.0), name, orb_used


def p3_graha_drishti(a, sign_a, sign_b):
    """P3: sign-based Vedic aspect. Returns (score, house_count)."""
    _check_body(a)
    n = (sign_b - sign_a) % 12 + 1
    if n == 1:
        return 100, n                                      # same sign: conjunction
    if n in OWNER_ASPECTS[a]:
        return 100, n
    if a in CLASSICAL and n in PARASHARA_PARTIAL:
        return PARASHARA_PARTIAL[n], n
    return 0, n


def p4_lal_kitab(a, b, sign_a, sign_b, lon_a, lon_b):
    """P4: Lal Kitab aspect. PENDING - no verified Lal Kitab aspect table is in the project. Returns None on purpose.
    Do not invent a table. When the owner/BOSS supplies a source, implement it here (return 0..100)."""
    return None


def aspect(a, b, lon_a, lon_b, mode='percent_of_angle', p4_fn=None):
    """Aspect of planet `a` (at lon_a) on planet `b` (at lon_b). Returns a dict with every principle shown.
    p4_fn(a, b, sign_a, sign_b, lon_a, lon_b) -> 0..100 or None; default is the pending p4_lal_kitab (None)."""
    p4_fn = p4_fn or p4_lal_kitab
    if a == b:
        raise ValueError('a planet does not aspect itself')
    _check_body(a)
    _check_body(b)
    la, lb = _norm(lon_a), _norm(lon_b)
    sa, sb = sign_of(la), sign_of(lb)
    v1, n1 = p1_owner_ladder(a, la, lb, mode)
    v2, west, orb = p2_western(la, lb)
    v3, n3 = p3_graha_drishti(a, sa, sb)
    v4 = p4_fn(a, b, sa, sb, la, lb)
    known = v1 + v2 + v3
    out = {
        'from': a, 'to': b, 'forward_sep_deg': round((lb - la) % 360.0, 4), 'mode': mode,
        'p1': v1, 'p1_house': n1, 'p2': round(v2, 4), 'p2_name': west, 'p2_orb_deg': None if orb is None else round(orb, 4),
        'p3': v3, 'p3_house': n3, 'p4': v4,
    }
    if v4 is None:
        out['final_pct'] = round(known / 4.0, 4)
        out['final_is_lower_bound'] = True                # P4 missing, counted as 0
        out['final_range_if_p4_known'] = (round(known / 4.0, 4), round((known + 100.0) / 4.0, 4))
    else:
        out['final_pct'] = round((known + v4) / 4.0, 4)
        out['final_is_lower_bound'] = False
        out['final_range_if_p4_known'] = (out['final_pct'], out['final_pct'])
    return out


def all_aspects(longitudes, mode='percent_of_angle', p4_fn=None):
    """Every ordered pair (A looks at B) from {body: sidereal longitude}. Rahu-Ketu skipped. Deterministic order."""
    res = []
    for a, b in itertools.permutations(sorted(longitudes), 2):
        if {a, b} == {'Rahu', 'Ketu'}:
            continue
        res.append(aspect(a, b, longitudes[a], longitudes[b], mode, p4_fn))
    return res


def strongest_per_pair(results):
    """Keep, for each unordered pair, the direction with the higher final_pct (ties: alphabetical `from`). Drops zeros."""
    best = {}
    for r in results:
        k = frozenset((r['from'], r['to']))
        cur = best.get(k)
        if cur is None or (r['final_pct'], cur['from']) > (cur['final_pct'], r['from']):
            best[k] = r
    return sorted((r for r in best.values() if r['final_pct'] > 0), key=lambda r: (-r['final_pct'], r['from'], r['to']))


def longitudes_from_key_info(rows):
    """Adapter for the site 'Key Info' rows ({'body','rasi','deg','minute'}, body like 'Sun - PiK'): -> {planet: longitude}.
    Only the 9 grahas and the 3 outer planets that appear by plain name are taken; Lagna and sensitive points are ignored."""
    out = {}
    for r in rows:
        name = r['body'].split(' - ')[0].strip()
        if name in OWNER_ASPECTS and r.get('rasi') in _SIGN_IDX and r.get('deg') is not None:
            out[name] = _SIGN_IDX[r['rasi']] * 30 + r['deg'] + (r.get('minute') or 0) / 60.0
    return out
