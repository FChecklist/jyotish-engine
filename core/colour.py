"""Personal colour DO/DON'T (GR-C1..C3). Colours come from core/planet_colors.py (Rajat's table: tradition claim).
WHICH colour is personal: candidate planets are scored from the native's own chart, using the multi-sign house shares (MAIN PART) over all house views
(D1 whole-sign, equal, Sripati, Porphyry, KP Placidus, D9), so bhava-chalit/Sripati/KP/D9 placements all count; plus today's transit (gochara from natal Moon).
Candidates: weekday lord (daily panchang), running antar and maha lord, lagna lord, birth-nakshatra lord (birth panchang), and for the month the lord of the Sun's new sign.
Score = lordship_quality + placement_quality + transit. House weights are HYPOTHESES (classical: trikona best, dusthana worst), not measured.
Not yet used (not built): annual (Varshaphal) chart, other divisional charts beyond D9, Jaimini, Tajika."""
import planet_colors as PC
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SIGN_LORD = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]
PNAME = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
HW = {1: 1.0, 2: 0.3, 3: -0.2, 4: 0.5, 5: 1.5, 6: -1.0, 7: 0.5, 8: -1.0, 9: 1.5, 10: 0.5, 11: 0.1, 12: -0.8}
WEEKDAY_LORD = [1, 2, 3, 4, 5, 6, 0]                 # Python weekday(): Monday=0
NAK_CYCLE = [8, 5, 0, 1, 2, 7, 4, 6, 3]              # Vimshottari order Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury
TRANSIT = {'favourable': 0.5, 'adverse': -0.5, 'very_adverse': -1.0}
def score(p, houses, phs, gm=None):
    """houses: {h: {'shares': {sign: share}}}; phs: {planet_name: {house: share}}; gm: gochara result per planet id."""
    func = sum(HW[int(h)] * sh for h, d in houses.items() for s, sh in d['shares'].items() if SIGN_LORD[SIGNS.index(s)] == p)
    place = sum(HW[int(h)] * sh for h, sh in (phs.get(PNAME[p]) or {}).items())
    tr = TRANSIT.get((gm or {}).get(p, {}).get('result'), 0.0) if gm else 0.0
    return round(func + place + tr, 3), {'lordship': round(func, 3), 'placement': round(place, 3), 'transit': tr}
def current_dasha(vim, date):
    cur = None
    for r in vim:
        y, m, d, _ = r['start_local']
        if (y, m, d) <= (date.year, date.month, date.day): cur = r
        else: break
    return (PNAME.index(cur['maha']), PNAME.index(cur['antar'])) if cur else (None, None)
def lagna_lord(houses):
    sh = houses[1]['shares'] if 1 in houses else houses['1']['shares']
    return SIGN_LORD[SIGNS.index(max(sh, key=sh.get))]
def candidates(natal, date, gm, extra=()):
    rep = natal['rep']; houses = {int(h): d for h, d in natal['houses'].items()}; phs = rep['house_influence']['planet_house_shares']
    maha, antar = current_dasha(rep['timing']['vimshottari'], date)
    cand = {}
    def add(p, role):
        if p is None: return
        cand.setdefault(p, []).append(role)
    add(WEEKDAY_LORD[date.weekday()], 'weekday lord (daily panchang)'); add(antar, 'antar lord'); add(maha, 'maha lord'); add(lagna_lord(houses), 'lagna lord')
    add(NAK_CYCLE[(natal['birth_nak'] - 1) % 9], 'birth nakshatra lord (birth panchang)')
    for p, role in extra: add(p, role)
    out = []
    for p, roles in cand.items():
        s, parts = score(p, houses, phs, gm); out.append({'planet': PNAME[p], 'id': p, 'colour': PC.BY_ENGINE_ID[p], 'score': s, 'parts': parts, 'roles': roles})
    return sorted(out, key=lambda x: -x['score'])
def colour_items(natal, date, gm, add, period='today', extra=()):
    """add(kind, text, weight, why, rule, source) is daily._add bound to the items list."""
    c = candidates(natal, date, gm, extra)
    if not c: return c
    best, worst = c[0], c[-1]
    if best['score'] >= 1.0:
        add('do', f"Wear or use {best['colour'].lower()} {period}.", 4 + min(best['score'], 3), f"colour {best['planet']} score {best['score']} {best['parts']} roles {best['roles']}", 'GR-C1', 'Rajat planet-colour table + own chart')
    if worst['score'] <= -1.0:
        add('dont', f"Avoid wearing {worst['colour'].lower()} {period}.", 4 + min(-worst['score'], 3), f"colour {worst['planet']} score {worst['score']} {worst['parts']} roles {worst['roles']}", 'GR-C2', 'Rajat planet-colour table + own chart')
    return c
