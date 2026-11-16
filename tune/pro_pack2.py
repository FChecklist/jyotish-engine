"""Second professional data pack: Jaimini, KP, Tajaka (yearly chart), Lal Kitab placements, ashtakavarga transit scores, D10.
Usage: ref/venv/bin/python pro_pack2.py NAME START END.  Private output only (/home/claude/astro/private/professional/NAME_pack2.json).
Reads birth data at run time from the private family file; nothing personal is stored in this script.
Lahiri for Parashari/Jaimini/Tajaka; Krishnamurti ayanamsa + Placidus + mean node for KP.
"""
import sys, json, datetime as dt
import swisseph as swe
from jhora.panchanga import drik
from jhora import utils
from jhora.horoscope.dhasa.raasi import chara
from jhora.horoscope.dhasa.graha import yogini
from jhora.horoscope.chart import charts, arudhas
from jhora.horoscope.transit import tajaka

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
SLORD = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter']
PN = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']   # PyJHora ids 0..8
VO = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
VY = dict(Ketu=7, Venus=20, Sun=6, Moon=10, Mars=7, Rahu=18, Jupiter=16, Saturn=19, Mercury=17)
MOV, FIX, DUAL = {0, 3, 6, 9}, {1, 4, 7, 10}, {2, 5, 8, 11}
FL = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_MOSEPH


def parse(s): return dt.date(*map(int, s.split('-')))
def hs(a, b): return (a - b) % 12 + 1   # house of sign a counted from sign b


def j_aspects(s):
    """Jaimini rashi drishti: signs aspected by sign s."""
    if s in MOV: return {x for x in FIX if x != (s + 1) % 12}
    if s in FIX: return {x for x in MOV if x != (s - 1) % 12}
    return {x for x in DUAL if x != s}


def starsub(lon):
    L = 360 / 27; lon %= 360; i = int(lon // L); rem = lon - i * L; st = VO.index(VO[i % 9]); acc = 0
    for k in range(9):
        l = VO[(st + k) % 9]; w = VY[l] / 120 * L
        if rem < acc + w or k == 8:
            r2 = rem - acc; acc2 = 0; st2 = VO.index(l)
            for k2 in range(9):
                l2 = VO[(st2 + k2) % 9]; w2 = VY[l2] / 120 * w
                if r2 < acc2 + w2 or k2 == 8: return VO[i % 9], l, l2
                acc2 += w2
        acc += w


def main():
    name, start, end = sys.argv[1], parse(sys.argv[2]), parse(sys.argv[3])
    p = json.load(open('/home/claude/astro/astro_family_data.json'))['people'][name]
    y, m, d = map(int, p['birth'][:10].split('-')); H, M, S = map(int, p['birth'][11:].split(':'))
    lat, lon, tz = p['lat'], p['lon'], 5.5
    drik.set_ayanamsa_mode('LAHIRI'); place = drik.Place(name, lat, lon, tz)
    dob = drik.Date(y, m, d); tob = (H, M, S); jd = utils.julian_day_number(dob, tob)
    pos = charts.rasi_chart(jd, place)
    lagS = pos[0][1][0]; sg = {PN[x[0]]: x[1] for x in pos[1:]}      # planet -> (sign0, deg)
    out = {'person': name, 'window': [str(start), str(end)]}
    # ---------------- Jaimini
    seven = sorted([(sg[k][1], k) for k in PN[:7]], reverse=True)
    names = ['AK', 'AmK', 'BK', 'MK', 'PK', 'GK', 'DK']
    ck = {n: k for n, (_, k) in zip(names, seven)}
    nav = charts.navamsa_chart(pos); nsg = {PN[x[0]]: x[1][0] for x in nav[1:]}; navL = nav[0][1][0]
    ar = arudhas.bhava_arudhas_from_planet_positions(pos)
    ak = ck['AK']; km = nsg[ak]
    UL = ar[11]; A1 = ar[0]; A10 = ar[9]; A11 = ar[10]
    tenth = (lagS + 9) % 12
    arg = {}
    for lab, off, ctr in (('2nd', 1, 11), ('4th', 3, 9), ('11th', 10, 2), ('5th (secondary)', 4, 8)):
        s0 = (tenth + off) % 12; s1 = (tenth + ctr) % 12
        arg[lab] = {'sign': SIGNS[s0], 'planets': [k for k in PN if sg[k][0] == s0], 'obstructed_by_sign': SIGNS[s1], 'obstructors': [k for k in PN if sg[k][0] == s1]}
    jaim = {'chara_karakas': ck, 'karakamsha_sign': SIGNS[km], 'AK_in_D1': SIGNS[sg[ak][0]], 'arudha_lagna_A1': SIGNS[A1], 'A10': SIGNS[A10], 'A11': SIGNS[A11],
            'upapada': SIGNS[UL], 'navamsa_lagna': SIGNS[navL], 'arudhas_all': [SIGNS[x] for x in ar],
            'planets_in_karakamsha_from_D1': [k for k in PN if sg[k][0] == km], 'planets_in_D9_karakamsha': [k for k in PN if nsg[k] == km],
            'amk_house_from_lagna': hs(sg[ck['AmK']][0], lagS), 'amk_sign': SIGNS[sg[ck['AmK']][0]], 'amk_in_D9': SIGNS[nsg[ck['AmK']]],
            'argala_on_10th': arg, 'sign_aspects_on_10th': [SIGNS[s] for s in range(12) if tenth in j_aspects(s)],
            'planets_aspecting_10th_jaimini': [k for k in PN if tenth in j_aspects(sg[k][0]) and sg[k][0] != tenth]}
    # chara dasha (K N Rao) rows inside window
    rows = chara.get_dhasa_antardhasa(dob, tob, place)
    cd = []
    for i, r in enumerate(rows):
        (mS, aS), (yy, mm, dd, hh), dur = r[0], r[1], r[2]
        s = dt.date(yy, mm, dd); nxt = rows[i + 1][1] if i + 1 < len(rows) else (yy + 2, mm, dd, 0); e = dt.date(*nxt[:3])
        if e >= start and s <= end: cd.append({'maha': SIGNS[mS], 'antar': SIGNS[aS], 'start': str(s), 'end': str(e), 'antar_house_from_lagna': hs(aS, lagS),
                                                'antar_is_10th_or_A10_or_AL_or_KM': aS in (tenth, A10, A1, km)})
    jaim['chara_dasha_rows'] = cd
    out['jaimini'] = jaim
    # Jaimini transit hits (Jupiter, Saturn, Mars, Rahu) on 10th / A1 / A10 / karakamsha / UL, daily compressed
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    targets = {'10th': tenth, 'A1 (arudha lagna)': A1, 'A10': A10, 'karakamsha': km, 'lagna': lagS}
    seg = []; cur = None; dday = start
    while dday <= end:
        jdn = swe.julday(dday.year, dday.month, dday.day, 6.5)
        sig = {}
        for b, nm in ((swe.JUPITER, 'Jupiter'), (swe.SATURN, 'Saturn'), (swe.MARS, 'Mars')):
            sig[nm] = int(swe.calc_ut(jdn, b, FL)[0][0] // 30)
        rs = int(swe.calc_ut(jdn, swe.TRUE_NODE, FL)[0][0] // 30); sig['Rahu'] = rs; sig['Ketu'] = (rs + 6) % 12
        key = tuple(sorted(sig.items()))
        if key != cur:
            hits = {}
            for pl in ('Jupiter', 'Saturn', 'Mars'):
                h = [tn for tn, ts in targets.items() if ts == sig[pl] or ts in j_aspects(sig[pl])]
                if h: hits[pl] = h
            seg.append({'from': str(dday), 'signs': {k: SIGNS[v] for k, v in sig.items()}, 'jaimini_hits': hits}); cur = key
        dday += dt.timedelta(days=1)
    out['jaimini_transits'] = seg
    # ---------------- Ashtakavarga transit scores (BPHS plain) from the saved engine report
    rep = json.load(open(f'/home/claude/astro/private/factsheets/{name}_report.json'))
    bav = rep['ashtakavarga']['bphs_plain']['bav']; sav = rep['ashtakavarga']['bphs_plain']['sav']
    rowi = {'Sun': 0, 'Moon': 1, 'Mars': 2, 'Mercury': 3, 'Jupiter': 4, 'Venus': 5, 'Saturn': 6}
    out['av_transit'] = [{'from': s['from'], **{pl: {'sign': s['signs'][pl], 'own_bav': bav[rowi[pl]][SIGNS.index(s['signs'][pl])], 'sav': sav[SIGNS.index(s['signs'][pl])]} for pl in ('Jupiter', 'Saturn', 'Mars')}} for s in seg]
    # ---------------- KP
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    jdu = swe.julday(y, m, d, H + M / 60 + S / 3600 - tz)
    cusps, ascmc = swe.houses_ex(jdu, lat, lon, b'P', swe.FLG_SIDEREAL)
    kpl = {}
    for b, nm in ((swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'), (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'), (swe.SATURN, 'Saturn'), (swe.MEAN_NODE, 'Rahu')):
        kpl[nm] = swe.calc_ut(jdu, b, FL)[0][0] % 360
    kpl['Ketu'] = (kpl['Rahu'] + 180) % 360
    cu = [c % 360 for c in cusps]
    def house_of(lg):
        for i in range(12):
            a, b2 = cu[i], cu[(i + 1) % 12]
            if (a <= b2 and a <= lg < b2) or (a > b2 and (lg >= a or lg < b2)): return i + 1
    kp = {'cusps': {}, 'planets': {}}
    for i, c in enumerate(cu):
        st, sb, ss = starsub(c); kp['cusps'][i + 1] = {'sign': SIGNS[int(c // 30)], 'deg': round(c % 30, 2), 'sign_lord': SLORD[int(c // 30)], 'star': st, 'sub': sb, 'subsub': ss}
    for k, lg in kpl.items():
        st, sb, ss = starsub(lg); kp['planets'][k] = {'sign': SIGNS[int(lg // 30)], 'deg': round(lg % 30, 2), 'house': house_of(lg), 'star': st, 'sub': sb, 'subsub': ss}
    occ = {h: [k for k in kpl if kp['planets'][k]['house'] == h] for h in range(1, 13)}
    ownd = {h: {SLORD[int(cu[h - 1] // 30)]} for h in range(1, 13)}
    # Rahu/Ketu also act for the sign lord they sit with / the planet conjunct (reported but not added here: standard KP uses star lord)
    def signif(h):
        l2 = set(occ[h]); l4 = set(ownd[h])
        l1 = {k for k in kpl if kp['planets'][k]['star'] in l2}; l3 = {k for k in kpl if kp['planets'][k]['star'] in l4}
        return {'L1': sorted(l1), 'L2': sorted(l2), 'L3': sorted(l3), 'L4': sorted(l4)}
    kp['house_significators'] = {h: signif(h) for h in range(1, 13)}
    plan_h = {k: set() for k in kpl}
    for h in range(1, 13):
        for lv in signif(h).values():
            for k in lv: plan_h[k].add(h)
    kp['planet_signifies_houses'] = {k: sorted(v) for k, v in plan_h.items()}
    # signified by star lord weighting (strong) : houses of its star lord's occupied+owned
    kp['planet_strong_signifies'] = {}
    for k in kpl:
        sl = kp['planets'][k]['star']
        hh = {kp['planets'][sl]['house']} | {h for h in range(1, 13) if SLORD[int(cu[h - 1] // 30)] == sl}
        kp['planet_strong_signifies'][k] = sorted(hh)
    c10 = kp['cusps'][10]; sub10 = c10['sub']
    kp['tenth_cusp_sublord'] = {'sub': sub10, 'star_of_sub': kp['planets'][sub10]['star'], 'sub_signifies': sorted(plan_h[sub10]), 'sub_strong_signifies': kp['planet_strong_signifies'][sub10],
                                'promise_2_6_10_11_count': len(set(plan_h[sub10]) & {2, 6, 10, 11}), 'against_5_8_12': sorted(set(plan_h[sub10]) & {5, 8, 12})}
    # KP timing grid: Vimshottari antar + pratyantar lords inside window
    pk = json.load(open(f'/home/claude/astro/private/professional/{name}_pack.json'))
    grid = []
    for q in pk['pratyantars']:
        row = {'span': f"{q['start']} to {q['end']}"}
        for role, lord in (('MD', q['maha']), ('AD', q['antar']), ('PD', q['praty'])):
            row[role] = {'lord': lord, 'signifies': sorted(plan_h[lord]), 'job_houses': sorted(set(plan_h[lord]) & {2, 6, 10, 11}), 'against': sorted(set(plan_h[lord]) & {5, 8, 12}), 'strong': kp['planet_strong_signifies'][lord]}
        grid.append(row)
    kp['timing_grid'] = grid
    out['kp'] = kp
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    # ---------------- Tajaka annual charts (age 51 and 52)
    taj = []
    for yrs in (start.year - y + 1, start.year - y + 2):   # PyJHora 'years' = completed age + 1
        yrs = int(yrs)
        try:
            cht, (dd3, fh) = tajaka.annual_chart(jd, place, years=yrs)
            aL = cht[0][1][0]; asg = {PN[x[0]]: x[1] for x in cht[1:]}
            muntha = (lagS + yrs - 1) % 12
            ml = SLORD[muntha]
            taj.append({'years_completed': yrs - 1, 'varsha_pravesh': [dd3, str(fh)], 'annual_lagna': SIGNS[aL], 'muntha_sign': SIGNS[muntha], 'muntha_house_in_annual': hs(muntha, aL),
                        'muntha_lord': ml, 'muntha_lord_house': hs(asg[ml][0], aL) if ml in asg else None, 'annual_10th': SIGNS[(aL + 9) % 12], 'annual_10th_lord': SLORD[(aL + 9) % 12],
                        'annual_10th_lord_house': hs(asg[SLORD[(aL + 9) % 12]][0], aL), 'planets_in_annual_10th': [k for k in PN if asg[k][0] == (aL + 9) % 12],
                        'planets': {k: {'sign': SIGNS[v[0]], 'house': hs(v[0], aL), 'deg': round(v[1], 1)} for k, v in asg.items()}})
        except Exception as ex:
            taj.append({'years_completed': yrs - 1, 'error': str(ex)[:160]})
    out['tajaka'] = taj
    # ---------------- Yogini dasha cross-check
    try:
        yr = yogini.get_dhasa_antardhasa(dob, tob, place)
        yl = []
        for i, r in enumerate(yr):
            s = dt.date(*r[1][:3]); nx = yr[i + 1][1][:3] if i + 1 < len(yr) else (s.year + 1, 1, 1); e = dt.date(*nx)
            if e >= start and s <= end: yl.append({'dasha': str(r[0]), 'start': str(s), 'end': str(e)})
        out['yogini'] = yl
    except Exception as ex:
        out['yogini'] = {'error': str(ex)[:160]}
    # ---------------- Lal Kitab placements (fixed houses: Aries = house 1)
    lk = {k: hs(sg[k][0], 0) for k in PN}
    maturity = {'Jupiter': 16, 'Sun': 22, 'Moon': 24, 'Venus': 25, 'Mars': 28, 'Mercury': 32, 'Ketu': 48, 'Saturn': 36, 'Rahu': 42}
    age = (start - dt.date(y, m, d)).days // 365
    out['lalkitab'] = {'houses': lk, 'age_at_start': age, 'maturity_age': maturity, 'matured_planets': [k for k, a in maturity.items() if a <= age],
                       'house10_occupants': [k for k in PN if lk[k] == 10], 'house10_lord': 'Saturn', 'saturn_house': lk['Saturn'],
                       'house10_empty': not [k for k in PN if lk[k] == 10],
                       'rin_pitru': [k for k in ('Venus', 'Mercury', 'Rahu') if lk[k] in (2, 5, 9, 12)], 'rin_nirdayi': [k for k in ('Sun', 'Moon', 'Mars') if lk[k] in (10, 12)],
                       'rin_swa': [k for k in ('Venus', 'Saturn', 'Rahu', 'Ketu') if lk[k] == 5],
                       'together': {'Sun+Venus+Mercury in house': lk['Sun'] if lk['Sun'] == lk['Venus'] == lk['Mercury'] else None, 'Mars+Ketu in house': lk['Mars'] if lk['Mars'] == lk['Ketu'] else None}}
    # ---------------- D10 dignity snapshot
    d10 = charts.dasamsa_chart(pos); d10L = d10[0][1][0]
    EXALT = {'Sun': 0, 'Moon': 1, 'Mars': 9, 'Mercury': 5, 'Jupiter': 3, 'Venus': 11, 'Saturn': 6}; DEB = {k: (v + 6) % 12 for k, v in EXALT.items()}
    OWN = {'Sun': {4}, 'Moon': {3}, 'Mars': {0, 7}, 'Mercury': {2, 5}, 'Jupiter': {8, 11}, 'Venus': {1, 6}, 'Saturn': {9, 10}}
    dd10 = {}
    for x in d10[1:]:
        k = PN[x[0]]; s0 = x[1][0]
        st = 'exalted' if EXALT.get(k) == s0 else 'debilitated' if DEB.get(k) == s0 else 'own sign' if s0 in OWN.get(k, ()) else ''
        dd10[k] = {'sign': SIGNS[s0], 'house': hs(s0, d10L), 'state': st}
    out['d10'] = {'lagna': SIGNS[d10L], 'tenth_sign': SIGNS[(d10L + 9) % 12], 'tenth_lord': SLORD[(d10L + 9) % 12], 'planets': dd10,
                  'tenth_lord_in': dd10[SLORD[(d10L + 9) % 12]], 'in_tenth': [k for k, v in dd10.items() if v['house'] == 10]}
    json.dump(out, open(f'/home/claude/astro/private/professional/{name}_pack2.json', 'w'), indent=1, default=str)
    print('ok', name, 'chara rows', len(cd), 'jaimini transit segs', len(seg), 'tajaka', len(taj))


if __name__ == '__main__':
    main()
