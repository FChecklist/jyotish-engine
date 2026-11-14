"""Ashtakavarga wrapper (PyJHora). Returns bav[row][sign0] bindus, rows 0 Sun,1 Moon,2 Mars,3 Mercury,4 Jupiter,5 Venus,6 Saturn,7 Lagna;
sav[sign0] = sum of rows 0-6 (BPHS). Input: D1 planet positions from core.charts or a PyJHora position list."""
from jhora.panchanga import drik
from jhora import utils
from jhora.horoscope.chart import charts as _ch, ashtakavarga as _av

def ashtakavarga(y, m, d, H, M, S, tz, lat, lon, ayanamsa='LAHIRI', variant='pyjhora_default'):
    """variant: 'pyjhora_default' (library defaults, four Moon/Venus table switches on) or 'bphs_plain' (all four switches off:
    Moon table = Sun 3,6,7,8,10,11; Moon 1,3,6,7,10,11; Mars 2,3,5,6,9,10,11; Mercury 1,3,4,5,7,8,10,11; Jupiter 1,4,7,8,10,11,12;
    Venus 3,4,5,7,9,10,11; Saturn 3,5,6,11; Lagna 3,6,10,11). Which one the source books prefer is an OPEN QUESTION."""
    drik.set_ayanamsa_mode(ayanamsa)
    place = drik.Place('p', lat, lon, tz)
    jd = utils.julian_day_number(drik.Date(y, m, d), (H, M, S))
    ph = _ch.divisional_chart(jd, place, divisional_chart_factor=1)
    hp = utils.get_house_planet_list_from_planet_positions(ph)
    kw = {} if variant == 'pyjhora_default' else dict(moon_benefic_9_from_moon=False, moon_malefic_9_from_mars=False, moon_benefic_2_from_jupiter=False, moon_malefic_12_from_jupiter=False)
    bav, sav, _ = _av.get_ashtaka_varga(hp, **kw)
    bav = [list(map(int, r)) for r in bav]
    return {'bav': bav, 'sav': [sum(bav[r][s] for r in range(7)) for s in range(12)], 'sav_pyjhora': list(map(int, sav)),
            'signs': {('L' if p[0] == 'L' else int(p[0])): p[1][0] for p in ph}}
