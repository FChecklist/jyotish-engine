"""KP star lord / sub lord / sub-sub lord from a sidereal longitude (Vimshottari proportional split).
Ayanamsa choice is explicit: 'lahiri' or 'kp' (Krishnamurti). Planet ids 0 Sun .. 8 Ketu as elsewhere."""
import swisseph as swe
ORDER = [8, 5, 0, 1, 2, 7, 4, 6, 3]                 # Ketu Venus Sun Moon Mars Rahu Jupiter Saturn Mercury
YEARS = {8: 7, 5: 20, 0: 6, 1: 10, 2: 7, 7: 18, 4: 16, 6: 19, 3: 17}
NAK = 360 / 27
AYAN = {'lahiri': swe.SIDM_LAHIRI, 'kp': swe.SIDM_KRISHNAMURTI}

def _split(start_lord, width, start):
    """Yield (lord, lo, hi) sub-divisions of [start, start+width), starting from start_lord."""
    i = ORDER.index(start_lord); lo = start
    for k in range(9):
        l = ORDER[(i + k) % 9]; w = width * YEARS[l] / 120
        yield l, lo, lo + w; lo += w

def lords(lon):
    lon %= 360; n = int(lon // NAK); star = ORDER[n % 9]; s0 = n * NAK
    for sub, lo, hi in _split(star, NAK, s0):
        if lo <= lon < hi + 1e-12:
            for ss, lo2, hi2 in _split(sub, hi - lo, lo):
                if lo2 <= lon < hi2 + 1e-12:
                    return {'star': star, 'sub': sub, 'subsub': ss}
    return {'star': star, 'sub': sub, 'subsub': ss}

def sidereal_lon(jd_ut, body, ayan='kp'):
    swe.set_sid_mode(AYAN[ayan]); return swe.calc_ut(jd_ut, body, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
