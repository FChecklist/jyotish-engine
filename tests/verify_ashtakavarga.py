"""Ashtakavarga checks: (1) BPHS fixed totals per planet on many charts, SAV = 337; (2) independent Sun and Moon BAV from BPHS tables."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import ashtakavarga as A
TOT = [48, 49, 39, 54, 56, 52, 39, 49]
SUN = {0: (1,2,4,7,8,9,10,11), 1: (3,6,10,11), 2: (1,2,4,7,8,9,10,11), 3: (3,5,6,9,10,11,12), 4: (5,6,9,11), 5: (6,7,12), 6: (1,2,4,7,8,9,10,11), 'L': (3,4,6,10,11,12)}
MOON = {0: (3,6,7,8,10,11), 1: (1,3,6,7,10,11), 2: (2,3,5,6,9,10,11), 3: (1,3,4,5,7,8,10,11), 4: (1,4,7,8,10,11,12), 5: (3,4,5,7,9,10,11), 6: (3,5,6,11), 'L': (3,6,10,11)}
def mine(table, signs):
    out = [0] * 12
    for k, houses in table.items():
        base = signs[k]
        for h in houses: out[(base + h - 1) % 12] += 1
    return out
random.seed(7); bad_tot = bad_sav = bad_sun = bad_moon = 0; N = 60
for i in range(N):
    y = random.randint(1900, 2020); m = random.randint(1, 12); d = random.randint(1, 28); H = random.randint(0, 23)
    lat = random.uniform(-50, 60); lon = random.uniform(-170, 170); tz = round(lon / 15 * 2) / 2
    r = A.ashtakavarga(y, m, d, H, 17, 0, tz, lat, lon, variant='bphs_plain')
    if [sum(row) for row in r['bav']] != TOT: bad_tot += 1
    if sum(r['sav']) != 337 or r['sav'] != r['sav_pyjhora']: bad_sav += 1
    if r['bav'][0] != mine(SUN, r['signs']): bad_sun += 1
    if r['bav'][1] != mine(MOON, r['signs']): bad_moon += 1
print(f'{N} random charts: bad_row_totals={bad_tot} bad_SAV={bad_sav} sun_BAV_mismatch={bad_sun} moon_BAV_mismatch={bad_moon}')
if bad_tot or bad_sav or bad_sun or bad_moon: sys.exit(1)
