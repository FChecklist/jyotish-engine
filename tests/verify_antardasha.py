"""Antardasha structure check (independent): order, durations = MD*AD/120, contiguity, 9x9 rows."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import dasha
from verify_divisional import CASES
ORDER = [8, 5, 0, 1, 2, 7, 4, 6, 3]; YEARS = {8: 7, 5: 20, 0: 6, 1: 10, 2: 7, 7: 18, 4: 16, 6: 19, 3: 17}
from datetime import datetime, timedelta
def dt(t): return datetime(t[0], t[1], t[2]) + timedelta(hours=t[3])
for name, y, m, d, H, M, S, tz, lat, lon in CASES:
    rows = dasha.vimshottari_antar(y, m, d, H, M, S, tz, lat, lon)
    bad = 0; fails = globals().get('fails', 0)
    for md, ad, t, dur in rows:
        if abs(dur - YEARS[md] * YEARS[ad] / 120) > 1e-6: bad += 1
    for i in range(1, len(rows)):
        gap = (dt(rows[i][2]) - dt(rows[i-1][2])).total_seconds() / 86400
        if abs(gap - rows[i-1][3] * 365.256364) > 6.0: bad += 1
    seq_ok = all([r[1] for r in rows[k:k+9]] == [ORDER[(ORDER.index(rows[k][0]) + j) % 9] for j in range(9)] for k in range(0, 81, 9))
    print(f'{name}: rows={len(rows)} errors_dur_or_gap_over_6d={bad} order_ok={seq_ok}')
    fails += bad + (0 if seq_ok else 1)
if fails: sys.exit(1)
