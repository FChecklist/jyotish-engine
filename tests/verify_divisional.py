"""Independent check: our own Swiss Ephemeris + BPHS divisional formulas vs PyJHora signs.
Run: ref venv python tests/verify_divisional.py   (prints mismatches per factor; exit 0 always, results are data)"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import swisseph as swe
import charts

def trop_to_sid(jd, ay=swe.SIDM_LAHIRI):
    swe.set_sid_mode(ay)
    return swe.get_ayanamsa_ut(jd)

def sid_lon(jd, body, ay):
    # PyJHora uses geometric-style settings; we use sidereal flag without apparent corrections off
    f = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    swe.set_sid_mode(ay)
    return swe.calc_ut(jd, body, f)[0][0] % 360

def asc_sid(jd, lat, lon, ay):
    swe.set_sid_mode(ay)
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'O', swe.FLG_SIDEREAL)
    return ascmc[0] % 360

ODD = lambda s: s % 2 == 0   # sign0 even index = odd sign (Aries=1st)
MOV = lambda s: s % 3 == 0; FIX = lambda s: s % 3 == 1

def dsign(L, f):
    s = int(L // 30); d = L % 30
    if f == 1: return s
    if f == 3:  return (s + 4 * int(d // 10)) % 12
    if f == 4:  return (s + 3 * int(d // 7.5)) % 12
    if f == 7:
        n = int(d // (30 / 7)); st = s if ODD(s) else (s + 6) % 12; return (st + n) % 12
    if f == 9:
        n = int(d // (30 / 9)); st = (s // 3 * 3 + 0) if False else [0, 9, 6, 3][s % 4]; return (st + n) % 12
    if f == 10:
        n = int(d // 3); st = s if ODD(s) else (s + 8) % 12; return (st + n) % 12
    if f == 12:
        n = int(d // 2.5); return (s + n) % 12
    if f == 16:
        n = int(d // (30 / 16)); st = [0, 4, 8][s % 3]; return (st + n) % 12
    if f == 20:
        n = int(d // 1.5); st = [0, 8, 4][s % 3]; return (st + n) % 12
    if f == 24:
        n = int(d // 1.25); st = 4 if ODD(s) else 3; return (st + n) % 12
    if f == 27:
        n = int(d // (30 / 27)); st = [0, 3, 6, 9][s % 4]; return (st + n) % 12
    if f == 40:
        n = int(d // 0.75); st = 0 if ODD(s) else 6; return (st + n) % 12
    if f == 45:
        n = int(d // (30 / 45)); st = [0, 4, 8][s % 3]; return (st + n) % 12
    if f == 60:
        n = int(d // 0.5); return (s + n) % 12
    return None

CASES = [('Delhi 1990', 1990, 6, 15, 14, 20, 0, 5.5, 28.6, 77.2), ('Sydney 1985', 1985, 12, 1, 13, 5, 0, 11.0, -33.9, 151.2),
         ('London 1960', 1960, 3, 3, 6, 45, 0, 0.0, 51.5, -0.12), ('NewYork 2001', 2001, 9, 11, 8, 46, 0, -4.0, 40.7, -74.0),
         ('Mumbai 1975', 1975, 1, 26, 22, 10, 0, 5.5, 19.07, 72.88)]
BODIES = {0: swe.SUN, 1: swe.MOON, 2: swe.MARS, 3: swe.MERCURY, 4: swe.JUPITER, 5: swe.VENUS, 6: swe.SATURN}
if __name__ == '__main__':
    bad = {}; tot = {}
    for name, y, m, d, H, M, S, tz, lat, lon in CASES:
        r = charts.natal(y, m, d, H, M, S, tz, lat, lon, factors=(1, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 40, 45, 60))
        jd = r['settings']['jd'] - 0  # PyJHora jd is local-time JD; convert to UT
        jd_ut = jd - tz / 24
        for f, c in r['charts'].items():
            for k in ['asc', 0, 1, 2, 3, 4, 5, 6]:
                L = asc_sid(jd_ut, lat, lon, swe.SIDM_LAHIRI) if k == 'asc' else sid_lon(jd_ut, BODIES[k], swe.SIDM_LAHIRI)
                mine = dsign(L, f); theirs = c[k][0]
                tot[f] = tot.get(f, 0) + 1
                if mine != theirs:
                    bad.setdefault(f, []).append((name, k, round(L, 3), mine, theirs))
    for f in sorted(tot):
        print(f'D{f}: {tot[f]-len(bad.get(f, []))}/{tot[f]} signs agree', ('; e.g. ' + str(bad[f][:2])) if f in bad else '')
    if bad: sys.exit(1)
