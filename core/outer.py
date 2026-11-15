"""Outer planets: Indra (Uranus), Varuna (Neptune), Yama (Pluto). Sidereal Lahiri, Swiss Ephemeris.
They are NOT part of classical Jyotish (Raman says so; Frawley, a modern author, says some Vedic astrologers add them, tentatively). So: positions and contacts only, labelled author view,
kept in the engine JSON, never used in the 3 DO + 3 DONT.
Contact rules follow Frawley: ordinary 7th-sign aspect, conjunction, degree orb about 10 degrees or less (he says distant planets act weaker). Tentative house links: Pluto 8, Neptune 12, Uranus 6."""
import datetime
import swisseph as swe
OUTER = {'Uranus': ('Indra', swe.URANUS), 'Neptune': ('Varuna', swe.NEPTUNE), 'Pluto': ('Yama', swe.PLUTO)}
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
TENTATIVE_HOUSE = {'Pluto': 8, 'Neptune': 12, 'Uranus': 6}
ORB = 10.0
def positions(dt_local, tz_hours):
    u = dt_local - datetime.timedelta(hours=tz_hours); jd = swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)
    swe.set_sid_mode(swe.SIDM_LAHIRI); out = {}
    for n, (alias, b) in OUTER.items():
        r, _ = swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED); out[n] = {'alias': alias, 'lon': r[0], 'retro': r[3] < 0}
    return out
def _sep(a, b):
    d = abs(a - b) % 360; return min(d, 360 - d)
def describe(pos, lagna_sign0, natal_lon):
    """pos from positions(); natal_lon {planet name: sidereal longitude}. Returns per outer planet: sign, degree, house (whole sign), contacts within the orb."""
    res = {}
    for n, v in pos.items():
        s = int(v['lon'] // 30); h = (s - lagna_sign0) % 12 + 1; contacts = []
        for q, ql in natal_lon.items():
            sep = _sep(v['lon'], ql)
            if sep <= ORB: contacts.append({'planet': q, 'kind': 'conjunction', 'orb_deg': round(sep, 2)})
            elif abs(sep - 180) <= ORB: contacts.append({'planet': q, 'kind': 'opposition (7th aspect)', 'orb_deg': round(abs(sep - 180), 2)})
        res[n] = {'alias': v['alias'], 'sign': SIGNS[s], 'deg': round(v['lon'] % 30, 4), 'house': h, 'retro': v['retro'], 'contacts': sorted(contacts, key=lambda c: c['orb_deg']),
                  'tentative_house_link': TENTATIVE_HOUSE[n], 'in_tentative_house': h == TENTATIVE_HOUSE[n]}
    res['label'] = 'author view (Frawley), not classical; tentative; unmeasured'
    return res
