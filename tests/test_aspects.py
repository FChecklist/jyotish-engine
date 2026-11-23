"""core/aspects.py on SYNTHETIC longitudes only (no real birth data, no network).
Hand-worked values. After the checks pass, the logic is deliberately broken one piece at a time (mutations); every break must
make the checks FAIL, then the original is restored and the checks must pass again (falsifiability)."""
import sys, os, copy, inspect
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import aspects as A


def approx(x, y, tol=1e-6):
    return abs(x - y) <= tol


def checks():
    # ---------------- P1: owner ladder, default = percent of the aspect angle
    p1 = lambda a, la, lb, mode='percent_of_angle': A.p1_owner_ladder(a, la, lb, mode)
    assert p1('Sun', 10, 190) == (100, 7)                       # exact opposition
    assert p1('Sun', 10, 199.0)[0] == 100                       # dev 9.0 = 5% of 180: boundary, inside
    assert p1('Sun', 10, 199.5)[0] == 75                        # 9.5 deg > 5%
    assert p1('Sun', 10, 208.0)[0] == 75                        # 18 = 10%
    assert p1('Sun', 10, 208.5)[0] == 50
    assert p1('Sun', 10, 217.0)[0] == 50                        # 27 = 15%
    assert p1('Sun', 10, 217.5)[0] == 0
    assert p1('Sun', 10, 181.0)[0] == 100                       # dev -9.0 (other side) also counts
    assert p1('Sun', 10, 10.0)[0] == 0                          # conjunction is not in owner P1
    assert p1('Sun', 10, 100.0)[0] == 0                         # Sun has no 4th aspect
    # absolute-degree reading (alternative): 5 / 10 / 15 degrees
    ab = lambda a, la, lb: A.p1_owner_ladder(a, la, lb, 'absolute_degrees')[0]
    assert ab('Sun', 10, 195.0) == 100 and ab('Sun', 10, 195.5) == 75 and ab('Sun', 10, 200.0) == 75
    assert ab('Sun', 10, 205.0) == 50 and ab('Sun', 10, 205.5) == 0
    assert p1('Sun', 10, 199.5)[0] == 75 and ab('Sun', 10, 199.5) == 75 and p1('Sun', 10, 196.0)[0] == 100 and ab('Sun', 10, 196.0) == 75   # the two readings differ
    # special aspects: Mars 4/7/8 = 90/180/210; Jupiter 5/7/9 = 120/180/240; Saturn 3/7/10 = 60/180/270
    assert p1('Mars', 0, 90) == (100, 4) and p1('Mars', 0, 180) == (100, 7) and p1('Mars', 0, 210) == (100, 8)
    assert p1('Mars', 0, 94.5)[0] == 100 and p1('Mars', 0, 95.0)[0] == 75      # 5% of 90 = 4.5
    assert p1('Mars', 0, 120)[0] == 0 and p1('Mars', 0, 60)[0] == 0           # Mars has no 3rd/5th in P1
    assert p1('Jupiter', 0, 120) == (100, 5) and p1('Jupiter', 0, 240) == (100, 9) and p1('Jupiter', 0, 90)[0] == 0
    assert p1('Saturn', 0, 60) == (100, 3) and p1('Saturn', 0, 270) == (100, 10) and p1('Saturn', 0, 210)[0] == 0
    assert p1('Saturn', 350, 260) == (100, 10)                                 # wrap-around: 260 - 350 = 270 forward
    assert p1('Rahu', 0, 180) == (100, 7) and p1('Pluto', 0, 90)[0] == 0
    # direction matters: Mars at 0 aspects 90 forward, Mars at 90 does NOT hit 0 with its 4th (that is 270 forward)
    assert p1('Mars', 90, 0)[0] == 0

    # ---------------- P2: western, linear to 0 at the orb edge
    p2 = lambda la, lb: A.p2_western(la, lb)
    assert p2(100, 100)[0] == 100 and p2(100, 100)[1] == 'conjunction'
    assert approx(p2(100, 104)[0], 50) and approx(p2(100, 108)[0], 0) and p2(100, 108.01)[0] == 0
    assert p2(0, 60) == (100.0, 'sextile', 0.0) and approx(p2(0, 63)[0], 50) and p2(0, 66.5)[0] == 0
    assert p2(0, 90)[1] == 'square' and p2(0, 120)[1] == 'trine' and p2(0, 180)[1] == 'opposition'
    assert approx(p2(0, 177)[0], 62.5) and approx(p2(0, 123)[0], 62.5) and approx(p2(0, 96)[0], 25)
    assert p2(0, 30)[0] == 0 and p2(0, 150)[0] == 0 and p2(0, 45)[0] == 0
    assert approx(p2(359, 1)[0], 75)                                           # wrap: separation 2 deg
    assert p2(10, 190) == p2(190, 10)                                          # symmetric
    assert approx(p2(0, 56)[0], 100 * (1 - 4 / 6.0))                           # sextile orb is 6, not 8

    # ---------------- P3: Vedic, sign based
    p3 = lambda a, sa, sb: A.p3_graha_drishti(a, sa, sb)[0]
    assert p3('Sun', 0, 0) == 100 and p3('Sun', 0, 6) == 100 and p3('Sun', 3, 9) == 100
    assert p3('Sun', 0, 2) == 25 and p3('Sun', 0, 9) == 25                     # 3rd, 10th
    assert p3('Sun', 0, 4) == 50 and p3('Sun', 0, 8) == 50                     # 5th, 9th
    assert p3('Sun', 0, 3) == 75 and p3('Sun', 0, 7) == 75                     # 4th, 8th
    assert p3('Sun', 0, 1) == 0 and p3('Sun', 0, 5) == 0 and p3('Sun', 0, 10) == 0 and p3('Sun', 0, 11) == 0   # 2nd 6th 11th 12th
    assert p3('Mars', 0, 3) == 100 and p3('Mars', 0, 7) == 100 and p3('Mars', 0, 2) == 25 and p3('Mars', 0, 4) == 50
    assert p3('Jupiter', 0, 4) == 100 and p3('Jupiter', 0, 8) == 100 and p3('Jupiter', 0, 3) == 75 and p3('Jupiter', 0, 2) == 25
    assert p3('Saturn', 0, 2) == 100 and p3('Saturn', 0, 9) == 100 and p3('Saturn', 0, 4) == 50 and p3('Saturn', 0, 3) == 75
    assert p3('Rahu', 0, 6) == 100 and p3('Rahu', 0, 4) == 0 and p3('Ketu', 0, 3) == 0   # nodes: owner list only, no partials
    assert p3('Pluto', 0, 6) == 100 and p3('Neptune', 0, 3) == 0 and p3('Uranus', 0, 8) == 0
    assert p3('Mars', 11, 1) == 25                                             # wrap Pisces -> Taurus = 3rd
    # sign based, not degree based: 29.9 Aries and 0.1 Taurus are 0.2 deg apart but only the 2nd sign
    r = A.aspect('Sun', 'Moon', 29.9, 30.1)
    assert r['p3'] == 0 and r['p2'] > 95 and r['p1'] == 0

    # ---------------- P4 pending, final = (P1+P2+P3+P4)/4
    assert A.p4_lal_kitab('Sun', 'Moon', 0, 6, 10, 190) is None
    r = A.aspect('Sun', 'Moon', 10, 190)
    assert (r['p1'], r['p2'], r['p3'], r['p4']) == (100, 100.0, 100, None)
    assert r['final_pct'] == 75.0 and r['final_is_lower_bound'] is True and r['final_range_if_p4_known'] == (75.0, 100.0)
    r = A.aspect('Sun', 'Moon', 10, 190, p4_fn=lambda *a: 40)                  # pluggable once a source exists
    assert r['p4'] == 40 and r['final_pct'] == 85.0 and r['final_is_lower_bound'] is False
    r = A.aspect('Mars', 'Venus', 0, 105)        # P1: 4th (90) dev 15 = 16.7% -> 0 ; P2 square o=15 > 8 -> 0 ; P3 signs 0 vs 3 -> n=4 -> full
    assert r['p1'] == 0 and r['p2'] == 0 and r['p3'] == 100 and r['final_pct'] == 25.0
    r = A.aspect('Jupiter', 'Saturn', 0, 127)    # P1: 5th (120) dev 7 = 5.83% -> 75 ; P2 trine o=7 -> 12.5 ; P3 n=5 -> 100
    assert r['p1'] == 75 and approx(r['p2'], 12.5) and r['p3'] == 100 and approx(r['final_pct'], (75 + 12.5 + 100) / 4)
    assert r['p1_house'] == 5 and r['p2_name'] == 'trine' and r['p3_house'] == 5
    # directional: Mars looks at Sun with a 4th aspect but Sun does not look back with a 4th
    fwd = A.aspect('Mars', 'Sun', 0, 90); back = A.aspect('Sun', 'Mars', 90, 0)
    assert fwd['p1'] == 100 and back['p1'] == 0 and fwd['p3'] == 100 and back['p3'] == 25 and fwd['p2'] == back['p2']   # Sun->Mars is the 10th (270 fwd)

    # ---------------- errors
    for bad in (lambda: A.aspect('Sun', 'Sun', 1, 2), lambda: A.aspect('Lagna', 'Sun', 1, 2), lambda: A.aspect('Sun', 'Moon', 1, 2, mode='x'),
                lambda: A.p3_graha_drishti('Chiron', 0, 1)):
        try:
            bad()
        except ValueError:
            continue
        raise AssertionError('expected ValueError')

    # ---------------- all pairs / strongest per pair / adapter
    L = {'Sun': 10.0, 'Moon': 190.0, 'Rahu': 100.0, 'Ketu': 280.0}
    res = A.all_aspects(L)
    assert len(res) == 12 - 2                                                   # 4 bodies -> 12 ordered pairs, Rahu-Ketu both ways skipped
    assert not any({r['from'], r['to']} == {'Rahu', 'Ketu'} for r in res)
    best = A.strongest_per_pair(res)
    top = best[0]
    assert {top['from'], top['to']} == {'Sun', 'Moon'} and top['final_pct'] == 75.0
    assert all(b['final_pct'] > 0 for b in best) and best == sorted(best, key=lambda r: (-r['final_pct'], r['from'], r['to']))
    assert A.all_aspects(L) == res                                              # deterministic
    rows = [{'body': 'Lagna', 'rasi': 'Le', 'deg': 0, 'minute': 24}, {'body': 'Sun - PiK', 'rasi': 'Le', 'deg': 3, 'minute': 30},
            {'body': 'Dhuma', 'rasi': 'Ar', 'deg': 1, 'minute': 0}, {'body': 'Pluto', 'rasi': 'Pi', 'deg': 29, 'minute': 59},
            {'body': 'Moon', 'rasi': None, 'deg': None, 'minute': None}]
    lon = A.longitudes_from_key_info(rows)
    assert set(lon) == {'Sun', 'Pluto'} and approx(lon['Sun'], 120 + 3.5) and approx(lon['Pluto'], 330 + 29 + 59 / 60.0)


def mutate(name, fn):
    """Apply a deliberate bug, expect checks() to fail, then restore."""
    saved = {k: copy.deepcopy(getattr(A, k)) for k in dir(A) if not k.startswith('__') and not inspect.ismodule(getattr(A, k))}
    try:
        fn()
        try:
            checks()
        except AssertionError:
            return                                                              # good: the break was detected
        raise SystemExit('FALSIFIABILITY FAILED: mutation %r was not detected' % name)
    finally:
        for k, v in saved.items():
            setattr(A, k, v)


checks()                                                                        # 1. the real code passes

orig_ladder, orig_p1, orig_p3 = A._ladder, A.p1_owner_ladder, A.p3_graha_drishti
mutate('ladder 5% -> 6%', lambda: setattr(A, 'LADDER', ((6.0, 100), (10.0, 75), (15.0, 50))))
mutate('ladder 75 -> 70', lambda: setattr(A, 'LADDER', ((5.0, 100), (10.0, 70), (15.0, 50))))
mutate('partial 4th/8th 75 -> 50', lambda: setattr(A, 'PARASHARA_PARTIAL', {3: 25, 10: 25, 5: 50, 9: 50, 4: 50, 8: 50}))
mutate('partial 3rd/10th 25 -> 0', lambda: setattr(A, 'PARASHARA_PARTIAL', {3: 0, 10: 0, 5: 50, 9: 50, 4: 75, 8: 75}))
mutate('trine orb 8 -> 6', lambda: setattr(A, 'WESTERN', ((0, 8.0, 'conjunction'), (60, 6.0, 'sextile'), (90, 8.0, 'square'), (120, 6.0, 'trine'), (180, 8.0, 'opposition'))))
mutate('sextile orb 6 -> 8', lambda: setattr(A, 'WESTERN', ((0, 8.0, 'conjunction'), (60, 8.0, 'sextile'), (90, 8.0, 'square'), (120, 8.0, 'trine'), (180, 8.0, 'opposition'))))
mutate('Saturn aspects 3/7/10 -> 3/7/9', lambda: A.OWNER_ASPECTS.__setitem__('Saturn', (3, 7, 9)))
mutate('Mars loses 8th', lambda: A.OWNER_ASPECTS.__setitem__('Mars', (4, 7)))
mutate('Rahu treated as classical', lambda: setattr(A, 'CLASSICAL', A.CLASSICAL | {'Rahu', 'Ketu'}))
mutate('percent mode uses absolute degrees', lambda: setattr(A, '_ladder', lambda dev, exact, mode: orig_ladder(dev, exact, 'absolute_degrees')))
mutate('P1 direction reversed', lambda: setattr(A, 'p1_owner_ladder', lambda a, la, lb, mode='percent_of_angle': orig_p1(a, lb, la, mode)))
mutate('P3 direction reversed', lambda: setattr(A, 'p3_graha_drishti', lambda a, sa, sb: orig_p3(a, sb, sa)))
mutate('P3 same sign not 100', lambda: setattr(A, 'p3_graha_drishti', lambda a, sa, sb: (0, 1) if sa == sb else orig_p3(a, sa, sb)))
mutate('P2 switched off', lambda: setattr(A, 'p2_western', lambda la, lb: (0.0, None, None)))
mutate('P4 invented as 100', lambda: setattr(A, 'p4_lal_kitab', lambda *a: 100))
orig_aspect = A.aspect
mutate('final divided by 3', lambda: setattr(A, 'aspect', lambda a, b, la, lb, mode='percent_of_angle', p4_fn=None: dict(
    orig_aspect(a, b, la, lb, mode, p4_fn), final_pct=orig_aspect(a, b, la, lb, mode, p4_fn)['final_pct'] * 4 / 3)))

checks()                                                                        # 3. restored, passes again
print('test_aspects ok')
