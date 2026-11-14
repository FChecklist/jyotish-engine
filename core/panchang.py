"""Panchang wrapper (PyJHora). All values 1-based as PyJHora gives them:
tithi 1-30 (16-30 = krishna), nakshatra 1-27 + pada, yoga 1-27, karana half-tithi 1-60 (PyJHora number), vara 0 Sunday..6 Saturday,
sunrise/sunset in local decimal hours."""
from jhora.panchanga import drik
from jhora import utils

def panchang(y, m, d, H, M, S, tz, lat, lon, ayanamsa='LAHIRI'):
    drik.set_ayanamsa_mode(ayanamsa)
    place = drik.Place('p', lat, lon, tz)
    jd = utils.julian_day_number(drik.Date(y, m, d), (H, M, S))
    t = drik.tithi(jd, place); n = drik.nakshatra(jd, place); yg = drik.yogam(jd, place); k = drik.karana(jd, place)
    return {'settings': {'ayanamsa': ayanamsa, 'tz': tz, 'jd': jd},
            'tithi': int(t[0]), 'nakshatra': int(n[0]), 'pada': int(n[1]), 'yoga': int(yg[0]), 'karana_half_tithi': int(k[0]),
            'vara': int(drik.vaara(jd, place)), 'sunrise_h': float(drik.sunrise(jd, place)[0]), 'sunset_h': float(drik.sunset(jd, place)[0])}
