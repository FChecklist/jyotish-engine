"""Vimshottari mahadasha wrapper (PyJHora). Returns [(lord_id, start_jd_local)] in order, lords 0 Sun..8 Ketu.
Antardasha etc. to be added after mahadasha is verified. Year length used by PyJHora: 365.256364 days (sidereal)."""
from jhora.panchanga import drik
from jhora import utils
from jhora.horoscope.dhasa.graha import vimsottari as _v

def vimshottari_maha(y, m, d, H, M, S, tz, lat, lon, ayanamsa='LAHIRI'):
    drik.set_ayanamsa_mode(ayanamsa)
    place = drik.Place('p', lat, lon, tz)
    jd = utils.julian_day_number(drik.Date(y, m, d), (H, M, S))
    md = _v.vimsottari_mahadasa(jd, place)
    return {'settings': {'ayanamsa': ayanamsa, 'tz': tz, 'jd_birth': jd, 'year_days': _v.year_duration},
            'maha': sorted(((int(k), float(v)) for k, v in md.items()), key=lambda t: t[1])}
