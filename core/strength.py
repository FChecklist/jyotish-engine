"""Planet strength from PyJHora Shadbala (we do not recompute it). Atom 'strength': strong = Shadbala ratio >= 1 (planet meets its classical minimum), weak = ratio < 1.
The 1.0 threshold is the classical minimum rule; whether a rule's word 'strong' means this is a reading choice (hypothesis, labelled). Sun..Saturn only (ids 0..6)."""
from jhora.panchanga import drik
from jhora import utils
from jhora.horoscope.chart import strength as _st
ROWS = ['sthana', 'kala', 'dig', 'cheshta', 'naisargika', 'drik', 'total_virupa', 'rupa', 'ratio']
def shadbala(y, m, d, H, M, S, tz, lat, lon):
    drik.set_ayanamsa_mode('LAHIRI'); place = drik.Place('p', lat, lon, tz)
    jd = utils.julian_day_number(drik.Date(y, m, d), (H, M, S)); r = _st.shad_bala(jd, place)
    return {name: {p: float(r[i][p]) for p in range(7)} for i, name in enumerate(ROWS)}
def ratios(sb): return {p: sb['ratio'][p] for p in range(7)}
def is_strong(ratio): return ratio >= 1.0
