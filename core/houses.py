"""Module A2: house systems. For each system a chart gets 12 houses, each with start, middle, end (ecliptic longitude, in whichever zodiac was requested)
and the list of signs the house spans with degrees in each. Planets are assigned per system. Nothing is chosen for the caller: every system is computed and kept.
Systems:  whole      - sign of the ascendant is house 1, every house = one full sign (Parashari/Jaimini default tradition)
          equal_asc  - houses start at the ascendant degree, 30 deg each (ascendant = cusp / start)
          equal_mid  - ascendant degree is the MIDDLE of house 1, 30 deg each
          sripati    - Porphyry cusps are bhava-madhya (middles); houses run midpoint to midpoint (Bhava Chalit, Sripati)
          porphyry   - Porphyry cusps taken as house STARTS
          placidus   - Placidus cusps as house starts (used by KP)
"""
import swisseph as swe
from zodiac import sign_of, SIGNS
AYAN = {'lahiri': swe.SIDM_LAHIRI, 'kp': swe.SIDM_KRISHNAMURTI, 'raman': swe.SIDM_RAMAN, 'fagan_bradley': swe.SIDM_FAGAN_BRADLEY, 'tropical': None}
SYSTEMS = ('whole', 'equal_asc', 'equal_mid', 'sripati', 'porphyry', 'placidus')
def _flags(ayan):
    if AYAN[ayan] is None: return 0
    swe.set_sid_mode(AYAN[ayan], 0, 0); return swe.FLG_SIDEREAL
def ayanamsa_value(jd, ayan):
    if AYAN[ayan] is None: return 0.0
    swe.set_sid_mode(AYAN[ayan], 0, 0); return swe.get_ayanamsa_ut(jd)
def _mid(a, b): return (a + ((b - a) % 360) / 2) % 360
def _cusps(jd, lat, lon, system, ayan):
    fl = _flags(ayan)
    asc = swe.houses_ex(jd, lat, lon, b'O', fl)[1][0]   # ascendant does not depend on the house system; Porphyry works at every latitude
    if system == 'whole':
        s0 = sign_of(asc) * 30; return [(s0 + 30 * i) % 360 for i in range(12)], asc
    if system == 'equal_asc': return [(asc + 30 * i) % 360 for i in range(12)], asc
    if system == 'equal_mid': return [(asc - 15 + 30 * i) % 360 for i in range(12)], asc
    if system == 'placidus':
        if abs(lat) >= 90 - 23.4393:   # Placidus is undefined inside the polar circles; refuse, never fall back silently
            raise ValueError('placidus undefined at latitude %.2f' % lat)
        return list(swe.houses_ex(jd, lat, lon, b'P', fl)[0]), asc
    por = list(swe.houses_ex(jd, lat, lon, b'O', fl)[0])
    if system == 'porphyry': return por, asc
    if system == 'sripati':  # madhya = por[i]; start of house i = midpoint of madhya[i-1], madhya[i]
        return [_mid(por[i - 1], por[i]) for i in range(12)], asc
    raise ValueError(system)
def spans(start, end):
    """signs covered by [start, end) as list of (sign_index, degrees)."""
    width = (end - start) % 360 or 360; out = []; x = start % 360; left = width
    while left > 1e-9:
        s = sign_of(x); room = (s + 1) * 30 - x if x < (s + 1) * 30 else 30
        d = min(room, left); out.append((s, round(d, 6))); x = (x + d) % 360; left -= d
    return out
def build(jd, lat, lon, system, ayan):
    cusp, asc = _cusps(jd, lat, lon, system, ayan)
    H = []
    for i in range(12):
        st, en = cusp[i], cusp[(i + 1) % 12]
        H.append(dict(h=i + 1, start=st, end=en, mid=_mid(st, en), width=(en - st) % 360 or 360, spans=spans(st, en),
                      start_sign=sign_of(st), mid_sign=sign_of(_mid(st, en)), n_signs=len(spans(st, en))))
    return dict(system=system, ayan=ayan, asc=asc, houses=H)
def house_of(lon, chart):
    for h in chart['houses']:
        if ((lon - h['start']) % 360) < h['width'] - 1e-9: return h['h']
    return 12
