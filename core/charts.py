"""Chart wrapper: one entry point for natal positions and divisional charts.
Calculation is delegated to PyJHora (checked in tests/verify_divisional.py against independent Swiss Ephemeris maths).
Output: {'settings':{...}, 'charts': {factor: {'asc': (sign0, deg), 0..8: (sign0, deg)}}}
sign0 = 0 Aries .. 11 Pisces; planet ids 0 Sun,1 Moon,2 Mars,3 Mercury,4 Jupiter,5 Venus,6 Saturn,7 Rahu,8 Ketu.
Degree inside the sign for divisional charts depends on the method PyJHora uses; the SIGN is the checked quantity."""
from jhora.panchanga import drik
from jhora import utils
from jhora.horoscope.chart import charts as _ch

FACTORS = (1,2,3,4,5,6,7,8,9,10,11,12,16,20,24,27,30,40,45,60)

def natal(y, m, d, H, M, S, tz, lat, lon, ayanamsa='LAHIRI', factors=FACTORS):
    drik.set_ayanamsa_mode(ayanamsa)
    place = drik.Place('p', lat, lon, tz)
    jd = utils.julian_day_number(drik.Date(y, m, d), (H, M, S))
    out = {'settings': {'ayanamsa': ayanamsa, 'tz': tz, 'lat': lat, 'lon': lon, 'jd': jd,
                        'engine': 'PyJHora 5.0.0 defaults (node and position settings as shipped)'}, 'charts': {}}
    for f in factors:
        rows = _ch.divisional_chart(jd, place, divisional_chart_factor=f)
        out['charts'][f] = {('asc' if r[0] == 'L' else int(r[0])): (r[1][0], r[1][1]) for r in rows}
    return out
