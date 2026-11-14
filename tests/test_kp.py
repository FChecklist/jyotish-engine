"""KP hand-checks from the published KP table (Krishnamurti) plus structure checks."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import kp
def dms(d, m, s): return d + m / 60 + s / 3600
# Ashwini: Ke-Ke 0:00:00-0:46:40 ; Ke-Ve 0:46:40-3:00:00 (standard published values)
assert kp.lords(0.0) == {'star': 8, 'sub': 8, 'subsub': 8}
assert kp.lords(dms(0, 46, 41))['sub'] == 5 and kp.lords(dms(0, 46, 41))['star'] == 8
assert kp.lords(dms(0, 46, 39))['sub'] == 8
assert kp.lords(2.999)['sub'] == 5 and kp.lords(3.001)['sub'] == 0       # Ke-Ve ends at 3:00, Ke-Su starts
assert kp.lords(13.34)['star'] == 5                                      # Bharani = Venus
assert kp.lords(359.99)['star'] == 3                                     # Revati = Mercury
# widths of all 243 sub divisions sum to 360, each nakshatra's subs sum to 13:20
tot = 0
for n in range(27):
    s = sum(hi - lo for _, lo, hi in kp._split(kp.ORDER[n % 9], kp.NAK, n * kp.NAK)); assert abs(s - kp.NAK) < 1e-9; tot += s
assert abs(tot - 360) < 1e-9
# every 0.01 deg step gives valid lords
for i in range(36000):
    r = kp.lords(i / 100); assert set(r) == {'star', 'sub', 'subsub'}
print('KP tests passed')
