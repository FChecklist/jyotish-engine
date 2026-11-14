"""Which zodiac signs influence each house (Gautam: a house is touched by 2-3 signs).
For every house we list, per house system, the signs its span covers and the degrees in each; then combine:
  votes[sign]  = number of systems whose span for that house includes the sign
  deg[sign]    = average degrees of the sign inside the house across systems
  main / also  = signs in >= 50% / < 50% of systems
D9 layer: navamsha sign of the house start and middle, and where that sign falls counted from the D9 lagna.
KP layer: Placidus cusps with the Krishnamurti ayanamsa (KP convention); other systems use the chosen ayanamsa.
Nothing here says which sign 'wins'; that is a rule question (see docs/OPEN_QUESTIONS.md)."""
import swisseph as swe
import houses as H

SYSTEMS = ('whole', 'equal_asc', 'equal_mid', 'sripati', 'porphyry', 'placidus')
MIN_DEG = 2.0   # heuristic: a sign with under 2 degrees (avg) inside the house is ignored as noise; OPEN QUESTION
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

def navamsha_sign(lon):
    s = int(lon % 360 // 30); n = int((lon % 30) // (30 / 9)); return ([0, 9, 6, 3][s % 4] + n) % 12

def house_signs(jd_ut, lat, lon, ayan='lahiri'):
    charts = {}
    for sy in SYSTEMS:
        charts[sy] = H.build(jd_ut, lat, lon, sy, 'kp' if sy == 'placidus' else ayan)
    lagna_ref = charts['whole']['asc']; d9_lagna = navamsha_sign(charts['equal_asc']['asc'])
    out = {'d9_lagna': SIGNS[d9_lagna], 'lagna_deg': charts['porphyry']['asc'], 'houses': {}}
    for h in range(1, 13):
        votes, deg, by = {}, {}, {}
        for sy, ch in charts.items():
            hh = ch['houses'][h - 1]; by[sy] = [(SIGNS[s], round(d, 2)) for s, d in hh['spans']]
            for s, d in hh['spans']:
                votes[s] = votes.get(s, 0) + 1; deg[s] = deg.get(s, 0) + d / len(SYSTEMS)
        main = sorted((s for s in votes if votes[s] >= len(SYSTEMS) / 2), key=lambda s: -deg[s])
        also = sorted((s for s in votes if votes[s] < len(SYSTEMS) / 2 and deg[s] >= MIN_DEG), key=lambda s: -deg[s])
        kp = charts['placidus']['houses'][h - 1]
        d9s = navamsha_sign(kp['start']); d9m = navamsha_sign(kp['mid'])
        out['houses'][h] = {'by_system': by, 'votes': {SIGNS[s]: v for s, v in sorted(votes.items())},
                            'avg_deg': {SIGNS[s]: round(deg[s], 1) for s in sorted(deg)},
                            'main': [SIGNS[s] for s in main], 'also': [SIGNS[s] for s in also],
                            'kp_cusp_deg': round(kp['start'] % 360, 2),
                            'd9_cusp_sign': SIGNS[d9s], 'd9_mid_sign': SIGNS[d9m],
                            'd9_cusp_house_from_d9_lagna': (d9s - d9_lagna) % 12 + 1}
    return out

def planets_by_house(positions, jd_ut, lat, lon, ayan='lahiri'):
    """positions = {name: absolute sidereal longitude}. Returns {name: {system: house}} and which planets change house between systems."""
    res = {}
    for sy in SYSTEMS:
        ch = H.build(jd_ut, lat, lon, sy, 'kp' if sy == 'placidus' else ayan)
        for name, L in positions.items():
            res.setdefault(name, {})[sy] = H.house_of(L, ch)
    shifts = {n: sorted(set(v.values())) for n, v in res.items() if len(set(v.values())) > 1}
    return {'by_system': res, 'shifts': shifts}
