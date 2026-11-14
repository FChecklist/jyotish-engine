import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import swisseph as swe, house_signs as HS, houses as H
# Neutral test chart (1990-01-01 06:00 IST Delhi). Family birth data must never be in git.
jd = swe.julday(1990, 1, 1, 6 - 5.5)
r = HS.house_signs(jd, 28.6139, 77.209)
h1 = r['houses'][1]
assert h1['main'] and set(h1['main']) <= {'Sagittarius', 'Scorpio'} and 'Scorpio' in h1['main'] + h1['also'], h1   # neutral chart: lagna in Scorpio near its start
# invariants for every system: 12 houses, widths sum to 360, spans cover width exactly
for sy in HS.SYSTEMS:
    ch = H.build(jd, 28.6139, 77.209, sy, 'kp' if sy == 'placidus' else 'lahiri')
    assert abs(sum(h['width'] for h in ch['houses']) - 360) < 1e-6, sy
    for h in ch['houses']: assert abs(sum(d for _, d in h['spans']) - h['width']) < 1e-4, (sy, h['h'])
# each house has at least one sign; whole-sign houses have exactly one
for h, d in r['houses'].items():
    assert d['main'], h
    assert len(d['by_system']['whole']) == 1
# navamsha formula hand checks: 0 deg Aries -> Aries; 3.34 deg Aries -> Taurus; 0 deg Taurus -> Capricorn; 0 deg Cancer -> Cancer; 0 deg Leo -> Aries
assert HS.navamsha_sign(0) == 0 and HS.navamsha_sign(3.34) == 1 and HS.navamsha_sign(30) == 9 and HS.navamsha_sign(90) == 3 and HS.navamsha_sign(120) == 0
print('house_signs tests passed; H1 votes', h1['votes'], 'main', h1['main'], 'also', h1['also'])
