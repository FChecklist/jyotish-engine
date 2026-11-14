"""Transit wrapper (PyJHora): sidereal positions of all planets at a given local date/time, plus retrograde list.
Result: {'lon': {0..8: abs_long}, 'sign': {...}, 'retro': [planet ids], 'jd': ..., 'settings': {...}}.
Transit over a natal chart = compare these signs to the natal signs (done in the method packs, not here)."""
from jhora.panchanga import drik
from jhora import utils
from jhora.horoscope.chart import charts as _ch

def transit(y, m, d, H, M, S, tz, lat, lon, ayanamsa='LAHIRI'):
    drik.set_ayanamsa_mode(ayanamsa)
    place = drik.Place('p', lat, lon, tz)
    jd = utils.julian_day_number(drik.Date(y, m, d), (H, M, S))
    rows = _ch.divisional_chart(jd, place, divisional_chart_factor=1)
    lon_ = {int(r[0]): r[1][0] * 30 + r[1][1] for r in rows if r[0] != 'L'}
    retro = [int(p) for p in drik.planets_in_retrograde(jd, place)]
    return {'lon': lon_, 'sign': {k: int(v // 30) for k, v in lon_.items()}, 'retro': retro, 'jd': jd,
            'settings': {'ayanamsa': ayanamsa, 'tz': tz, 'node': 'true (PyJHora default)'}}
