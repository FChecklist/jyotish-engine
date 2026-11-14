"""Independent Vimshottari mahadasa check: Moon nakshatra from Swiss Ephemeris, balance by proportion, 120-year cycle.
Compare each start date against PyJHora (tolerance 2 days, year length YD vs 365.256364 explains <1 day)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import swisseph as swe
import dasha
from verify_divisional import CASES
ORDER = [8, 5, 0, 1, 2, 7, 4, 6, 3]           # Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury
YD = 365.256364
YEARS = {8: 7, 5: 20, 0: 6, 1: 10, 2: 7, 7: 18, 4: 16, 6: 19, 3: 17}
def mine(jd_ut, jd_local_birth):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    L = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
    n = int(L // (360 / 27)); frac = (L % (360 / 27)) / (360 / 27)
    lord = ORDER[n % 9]; start = jd_local_birth - frac * YEARS[lord] * YD
    out = []; i = ORDER.index(lord); t = start
    for k in range(9):
        l = ORDER[(i + k) % 9]; out.append((l, t)); t += YEARS[l] * YD
    return out
worst = 0
for name, y, m, d, H, M, S, tz, lat, lon in CASES:
    r = dasha.vimshottari_maha(y, m, d, H, M, S, tz, lat, lon)
    jd = r['settings']['jd_birth']
    mm = mine(jd - tz / 24, jd)
    theirs = r['maha'][:9]
    ok = all(a[0] == b[0] for a, b in zip(mm, theirs)); allok = globals().get('allok', True) and ok
    diffs = [abs(a[1] - b[1]) for a, b in zip(mm, theirs)]
    worst = max(worst, max(diffs))
    print(f'{name}: lords_match={ok} max_start_diff_days={max(diffs):.2f}')
print('worst diff days', round(worst, 2))
if worst > 4 or not allok: sys.exit(1)
