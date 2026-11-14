"""Independent panchang check from Swiss Ephemeris: tithi, nakshatra+pada, yoga, half-tithi, weekday, sunrise/sunset."""
import sys, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import swisseph as swe
import panchang
from verify_divisional import CASES
PLACES = [(5.5, 28.6, 77.2), (0.0, 51.5, -0.12), (11.0, -33.9, 151.2), (-4.0, 40.7, -74.0), (5.5, 19.07, 72.88)]
DATES = [(1960, 3, 3, 6, 45), (1975, 1, 26, 22, 10), (1985, 12, 1, 13, 5), (1990, 6, 15, 14, 20), (2001, 9, 11, 8, 46),
         (2010, 1, 15, 11, 30), (2018, 7, 27, 2, 15), (2022, 10, 25, 18, 50), (2026, 11, 14, 17, 0), (1947, 8, 15, 0, 0)]
def lon_sid(jd, b):
    swe.set_sid_mode(swe.SIDM_LAHIRI); return swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
def sun_rise_set(jd_ut_midnight_local, tz, lat, lon, rsmi):
    r = swe.rise_trans(jd_ut_midnight_local, swe.SUN, rsmi | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION * 0, (lon, lat, 0), 1013.25, 15)
    return r[1][0]
bad = {k: 0 for k in ('tithi', 'nak', 'pada', 'yoga', 'karana', 'vara', 'sunrise', 'sunset')}; tot = 0; worst_sr = 0; worst_ss = 0
for (tz, lat, lon) in PLACES:
    for (y, m, d, H, M) in DATES:
        p = panchang.panchang(y, m, d, H, M, 0, tz, lat, lon)
        jd_ut = p['settings']['jd'] - tz / 24
        S, Mo = lon_sid(jd_ut, swe.SUN), lon_sid(jd_ut, swe.MOON)
        el = (Mo - S) % 360; tot += 1
        mine = {'tithi': int(el // 12) + 1, 'nak': int(Mo // (360 / 27)) + 1, 'pada': int((Mo % (360 / 27)) // (360 / 27 / 4)) + 1,
                'yoga': int(((S + Mo) % 360) // (360 / 27)) + 1, 'karana': int(el // 6) + 1}
        theirs = {'tithi': p['tithi'], 'nak': p['nakshatra'], 'pada': p['pada'], 'yoga': p['yoga'], 'karana': p['karana_half_tithi']}
        for k in mine:
            if mine[k] != theirs[k]: bad[k] += 1
        wd = (datetime.date(y, m, d).weekday() + 1) % 7
        # weekday runs sunrise to sunrise: before sunrise counts as previous day
        if H + M / 60 < p['sunrise_h']: wd = (wd - 1) % 7
        if wd != p['vara']: bad['vara'] += 1
        jd0 = swe.julday(y, m, d, 0.0) - tz / 24
        sr = sun_rise_set(jd0 - 0.0, tz, lat, lon, swe.CALC_RISE); ss = sun_rise_set(jd0, tz, lat, lon, swe.CALC_SET)
        def loc(t): return ((t + tz / 24 - 0.5) % 1) * 24
        dsr = abs(loc(sr) - p['sunrise_h']) * 60; dss = abs(loc(ss) - p['sunset_h']) * 60
        worst_sr = max(worst_sr, min(dsr, 1440 - dsr)); worst_ss = max(worst_ss, min(dss, 1440 - dss))
print('cases', tot, 'mismatches', bad)
print('worst sunrise diff minutes', round(worst_sr, 2), 'worst sunset diff minutes', round(worst_ss, 2))
if sum(bad.values()) or worst_sr > 6 or worst_ss > 6: sys.exit(1)
