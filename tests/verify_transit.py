"""Transit check vs Swiss Ephemeris: longitudes (arcsec) and retrograde flags (speed < 0) over 1900-2100, 40 dates."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import swisseph as swe
import transit
B = {0: swe.SUN, 1: swe.MOON, 2: swe.MARS, 3: swe.MERCURY, 4: swe.JUPITER, 5: swe.VENUS, 6: swe.SATURN}
random.seed(3); worst = 0; rbad = 0; sbad = 0; N = 40; nodes = 0
for _ in range(N):
    y = random.randint(1900, 2100); m = random.randint(1, 12); d = random.randint(1, 28); H = random.randint(0, 23)
    t = transit.transit(y, m, d, H, 0, 0, 5.5, 28.6, 77.2)
    jd = t['jd'] - 5.5 / 24; swe.set_sid_mode(swe.SIDM_LAHIRI)
    for k, b in B.items():
        r = swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
        dd = abs(((r[0] - t['lon'][k] + 180) % 360) - 180) * 3600; worst = max(worst, dd)
        if int(r[0] // 30) != t['sign'][k]: sbad += 1
        if k >= 2 and (r[3] < 0) != (k in t['retro']): rbad += 1
    tn = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
    if abs(((tn - t['lon'][7] + 180) % 360) - 180) * 3600 > 5: nodes += 1
print(f'{N} dates: worst longitude diff {worst:.1f} arcsec, sign mismatches {sbad}, retrograde flag mismatches {rbad}, node diffs >5" {nodes}')
if sbad or rbad or nodes or worst > 90: sys.exit(1)
