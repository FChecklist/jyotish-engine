"""PERSON-SPECIFIC daily guidance (spec: docs/PERSONAL_PIPELINE.md). Plain code, no AI.
Why this exists: the older guide.py ranked mostly day-wide panchang lines (same Rahu Kaal / "avoid new starts" for everybody) and never read the running dasha
or the annual (Varshaphal) chart. This module analyses, per person: natal chart + running maha/antar/pratyantar dasha + natal yogas + annual chart (Muntha, Muntha lord,
year lord) + the day's panchang against the birth star + today's transit against the natal chart. Every finding becomes a SIGNAL (area, signed weight, reason, rule ids).
Signals are summed per life area; the 3 strongest positive areas are DO, the 3 strongest negative are DON'T. A factor the engine did not compute is never invented:
what is not built is listed in LIMITS and printed with every result.
All weights below are HYPOTHESES (tradition claims, accuracy not measured). Birth data is read by the caller from a private path; nothing here stores it."""
import datetime
import swisseph as swe
import panchang as PCH, transit as TR, gochara as G, dignity as DG, yogas as YG
from jhora.panchanga import drik
from jhora import utils
from jhora.horoscope.chart import charts as _ch
from guidance_rules import *
import daily

HOME = (28.6139, 77.209, 5.5)                      # family home (lat, lon, tz): used for today's panchang and for the annual chart, as in guide.py
PLN = {v: k for k, v in PL.items()}                # name -> id
ORD = [8, 5, 0, 1, 2, 7, 4, 6, 3]                  # Vimshottari order Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury
YRS = {8: 7, 5: 20, 0: 6, 1: 10, 2: 7, 7: 18, 4: 16, 6: 19, 3: 17}
YEAR_DAYS = 365.256364                             # PyJHora dasha year
VARA_LORD = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}   # python weekday (Mon=0) -> day lord
# hypothesis weights (all tunable; none measured)
W = {'maha': 2.5, 'antar': 3.5, 'praty': 2.0, 'yoga_act': 0.6, 'muntha': 2.0, 'muntha_lord': 1.5, 'year_lord': 1.5, 'tara': 4.0, 'chandra': 4.0, 'vara_lord': 2.0,
     'nak_lord': 1.5, 'contact': 2.5, 'tithi': 2.0, 'nakclass': 1.5, 'yoga': 1.5, 'karana': 1.5, 'gochara_moon': 4.0, 'gochara_fast': 2.0, 'gochara_jup': 3.0, 'gochara_sat': 3.5, 'gochara_node': 3.0}
THRESHOLD = 1.0                                    # |net| at or above this = a clear signal
MILD = 0.25                                        # between MILD and THRESHOLD: used only to fill up to 3 lines, and marked 'mild'
AREA_TXT = dict(AREA)                              # (theme, do-wording, dont-wording) from guidance_rules; two lines re-worded so a Do never tells you to sign when a Don't says wait
AREA_TXT[7] = (AREA[7][0], 'Spend quality time on your spouse and partnerships.', AREA[7][2])
AREA_TXT[10] = (AREA[10][0], 'Be visible at work and push your career matters.', AREA[10][2])
INIT = ('start and decide', 'Take up important meetings, decisions and new starts today.', 'Do not begin new ventures, sign anything or take major decisions today.')
LIMITS = ['Accuracy of every weight is NOT measured (event backtest on 20 dated events showed chance level).',
          'Only 9,849 of 29,430 book rules (33.5%) are executable; fired natal rules are shown as support, not scored.',
          'NOT built (so not used): planet strength (shadbala), Panchavargeeya bala (year lord uses a simplified dignity score), Mudda/Varsha dasha, Tajika aspects and ithasala, '
          'other dashas (only Vimshottari), divisional-chart rules, Lal Kitab states, Jaimini, KP ruling planets, doshas, transit aspects (drishti) to natal planets.',
          'Natural benefic/malefic is not used as a fact; dignity (exalted/own/friend/enemy/debilitated) and house position are used instead.',
          'Dasha dates carry +-5 days of uncertainty (PyJHora year length).',
          'Birth-day coincidences (same weekday or tithi as at birth) are recorded in the facts but NOT scored: no executable rule for them exists in the engine.',
          'Pratyantar (sub-sub-period) is computed by Vimshottari proportion from the antardasha dates; not cross-checked against PyJHora.']
BAD_HOUSES = (6, 8, 12)
GOOD_HOUSES = (1, 4, 5, 7, 9, 10)

def _name(p): return PL[p]
def _ordinal(n): return f'{n}{"th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")}'

# ---------- natal ----------
def natal_facts(rep):
    d1 = rep['chart']['divisional']['D1']
    names = {v: k for k, v in PL.items()}
    sg = {p: d1[PL[p]]['sign0'] for p in range(9)}; lon = {p: d1[PL[p]]['sign0'] * 30 + d1[PL[p]]['deg'] for p in range(9)}
    lagna = d1['Lagna']['sign0']; house_of = {p: (sg[p] - lagna) % 12 + 1 for p in sg}
    hi = rep['house_influence']; phs = hi['planet_house_shares']
    occ = {p: {int(h): s for h, s in phs.get(PL[p], {}).items() if s >= AREA_MIN_WEIGHT} for p in range(9)}
    lord = {p: {} for p in range(9)}
    for h, d in hi['houses'].items():
        for s_name, share in d['shares'].items():
            L = DG.SIGN_LORD[SIGNS.index(s_name)]
            if share >= AREA_MIN_WEIGHT: lord[L][int(h)] = lord[L].get(int(h), 0) + share
    yg = [n for n in YG.NAMES if _yoga_ok(n, sg, house_of)]
    return {'sg': sg, 'lon': lon, 'lagna': lagna, 'house_of': house_of, 'occ': occ, 'lord': lord, 'yogas': yg, 'moon_sign0': sg[1], 'birth_nak': rep['panchang']['nakshatra'],
            'houses': hi['houses'], 'bav': rep['ashtakavarga']['bphs_plain']['bav'][:7], 'sav': rep['ashtakavarga']['bphs_plain']['sav'], 'rep': rep}
def _yoga_ok(n, sg, house_of):
    try: return bool(YG.yoga(n, sg, house_of))
    except Exception: return False
def condition(p, sign0, house):
    """Natal strength of planet p: dignity (-2..+2) + house (kendra/trikona +0.5, dusthana -1). Returns (score, words). Rahu/Ketu: house only (schools differ on dignity)."""
    st = DG.states(p, sign0); s = 0.0; w = []
    if 'exalted' in st: s += 2; w.append('exalted')
    elif 'debilitated' in st: s -= 2; w.append('debilitated')
    elif 'own' in st: s += 1.5; w.append('in its own sign')
    elif 'friend' in st: s += 0.5; w.append("in a friend's sign")
    elif 'enemy' in st: s -= 0.5; w.append("in an enemy's sign")
    elif 'neutral' in st: w.append("in a neutral sign")
    if house in BAD_HOUSES: s -= 1; w.append(f'in a difficult house ({_ordinal(house)})')
    elif house in GOOD_HOUSES: s += 0.5; w.append(f'in a strong house ({_ordinal(house)})')
    return s, ', '.join(w) if w else 'no dignity rule'
RW = {'favourable': 'favourable', 'neutral': 'neutral', 'adverse': 'unfavourable', 'very_adverse': 'very unfavourable'}
def dig_word(p, sign0):
    st = DG.states(p, sign0)
    for k, w in (('exalted', 'exalted'), ('debilitated', 'debilitated'), ('own', 'in its own sign'), ('friend', "in a friend's sign"), ('enemy', "in an enemy's sign"), ('neutral', 'in a neutral sign')):
        if k in st: return w
    return 'no dignity rule'
TR_NORM = {'favourable': 1.0, 'neutral': 0.0, 'adverse': -0.7, 'very_adverse': -1.0}

# ---------- dasha ----------
def running_dasha(rep, asof):
    rows = rep['timing']['vimshottari']; run = None; nxt = None
    for i, r in enumerate(rows):
        t = datetime.datetime(*[int(x) for x in r['start_local'][:3]])
        if t <= asof: run, ri = r, i
        else: break
    if run is None: return None
    s = datetime.datetime(*[int(x) for x in run['start_local'][:3]])
    e = datetime.datetime(*[int(x) for x in rows[ri + 1]['start_local'][:3]]) if ri + 1 < len(rows) else s + datetime.timedelta(days=run['years'] * YEAR_DAYS)
    maha, antar = PLN[run['maha']], PLN[run['antar']]; total = (e - s).total_seconds() / 86400
    k = ORD.index(antar); t0 = s; praty = None
    for j in range(9):
        p = ORD[(k + j) % 9]; d = total * YRS[p] / 120.0; t1 = t0 + datetime.timedelta(days=d)
        if t0 <= asof < t1: praty = p; pend = t1; break
        t0 = t1
    if praty is None: praty = antar; pend = e
    return {'maha': maha, 'antar': antar, 'praty': praty, 'antar_start': s.date().isoformat(), 'antar_end': e.date().isoformat(), 'praty_end': pend.date().isoformat()}

# ---------- annual chart (Varshaphal) ----------
def _sun_sid(jd_ut):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0][0]
def solar_return(natal_sun_lon, birth_md, asof, tz):
    """Latest moment <= asof when the sidereal (Lahiri) Sun is back on its natal longitude. Returns local datetime."""
    for yr in (asof.year, asof.year - 1):
        g = datetime.datetime(yr, birth_md[0], birth_md[1]) - datetime.timedelta(days=3)
        t = g; step = datetime.timedelta(hours=1); prev = None
        while t < g + datetime.timedelta(days=7):
            jd = swe.julday(t.year, t.month, t.day, t.hour + t.minute / 60 - tz); d = (_sun_sid(jd) - natal_sun_lon + 180) % 360 - 180
            if prev is not None and prev < 0 <= d:
                lo, hi = t - step, t
                while (hi - lo).total_seconds() > 30:
                    mid = lo + (hi - lo) / 2; jm = swe.julday(mid.year, mid.month, mid.day, mid.hour + mid.minute / 60 + mid.second / 3600 - tz)
                    if (_sun_sid(jm) - natal_sun_lon + 180) % 360 - 180 < 0: lo = mid
                    else: hi = mid
                if hi <= asof: return hi.replace(microsecond=0)
            prev = d; t += step
    raise RuntimeError('solar return not found')
def chart_at(dt, tz, lat, lon):
    drik.set_ayanamsa_mode('LAHIRI'); place = drik.Place('p', lat, lon, tz)
    jd = utils.julian_day_number(drik.Date(dt.year, dt.month, dt.day), (dt.hour, dt.minute, dt.second))
    rows = _ch.divisional_chart(jd, place, divisional_chart_factor=1)
    pl = {int(r[0]): r[1][0] for r in rows if r[0] != 'L'}; lg = [r[1][0] for r in rows if r[0] == 'L'][0]
    return lg, pl
TRIRASI = {0: (0, 4), 4: (0, 4), 8: (0, 4), 1: (5, 1), 5: (5, 1), 9: (5, 1), 2: (6, 3), 6: (6, 3), 10: (6, 3), 3: (5, 2), 7: (5, 2), 11: (5, 2)}   # sign -> (day lord, night lord): fire Sun/Jup, earth Ven/Moon, air Sat/Mer, water Ven/Mars
def annual_chart(nf, birth_year, birth_md, asof):
    lat, lon, tz = HOME
    ret = solar_return(nf['lon'][0], birth_md, asof, tz); age = ret.year - birth_year
    lg, pl = chart_at(ret, tz, lat, lon); ah = lambda s: (s - lg) % 12 + 1
    muntha = (nf['lagna'] + age) % 12; mh = ah(muntha); ml = DG.SIGN_LORD[muntha]; mlh = ah(pl[ml]) if ml in pl else None
    is_day = ah(pl[0]) >= 7
    cands = [DG.SIGN_LORD[pl[0]] if is_day else DG.SIGN_LORD[pl[1]], DG.SIGN_LORD[nf['lagna']], DG.SIGN_LORD[lg], ml, TRIRASI[lg][0 if is_day else 1]]
    best = None
    for c in set(cands):
        if c not in pl: continue
        sc, wds = condition(c, pl[c], ah(pl[c])); sc += 0.5 * (cands.count(c) - 1)
        if best is None or sc > best[0]: best = (sc, c, wds)
    return {'return_local': ret.isoformat(sep=' '), 'completed_years': age, 'annual_lagna': lg, 'muntha_sign': muntha, 'muntha_house': mh, 'muntha_lord': ml, 'muntha_lord_house': mlh,
            'day_chart': is_day, 'year_lord': best[1] if best else None, 'year_lord_house': ah(pl[best[1]]) if best else None, 'year_lord_words': best[2] if best else None,
            'year_lord_candidates': sorted(set(PL[c] for c in cands)), 'sign_of': dict(pl), 'house_of': {p: ah(s) for p, s in pl.items()}}

# ---------- signal collection ----------
class Sig:
    def __init__(s): s.items = []
    def add(s, area, w, group, tag, why, rules=(), personal=True, brief=None):
        if abs(w) < 1e-9: return
        s.items.append({'area': area, 'w': round(w, 3), 'group': group, 'tag': tag, 'why': why, 'brief': brief or why, 'rules': list(rules), 'personal': personal})
def planet_areas(nf, p):
    """{house: weight}: houses the planet occupies (share-weighted, weight 1) and rules (share-weighted, 0.8). Main part design: every house is touched by 2-3 signs."""
    out = {}
    for h, s in nf['occ'][p].items(): out[h] = ('occupies', out.get(h, (None, 0))[1] + s)
    for h, s in nf['lord'][p].items():
        if h in out: out[h] = ('occupies and rules', out[h][1] + 0.8 * s)
        else: out[h] = ('rules', 0.8 * s)
    return out
def planet_signals(sig, nf, p, W_, group, tag, prefix, tr_res, tr_h):
    """Activated planet p (a dasha lord, the day lord, ...): effect = weight x (natal condition/2 + today's transit norm), spread over the houses it occupies and rules."""
    cs, words = condition(p, nf['sg'][p], nf['house_of'][p]); tn = TR_NORM.get(tr_res, 0)
    s = cs / 2.0 + tn
    for h, (how, share) in planet_areas(nf, p).items():
        sig.add(h, W_ * s * share, group, tag, f'{prefix} {_name(p)} is {words}; whole-sign house {nf["house_of"][p]}; counting its sign shares it {how} your {_ordinal(h)} house; today it moves {_ordinal(tr_h)} from your Moon ({RW.get(tr_res, tr_res)})', ['BK13_0001'] if tr_res else [],
                brief=f'{prefix} {_name(p)} ({dig_word(p, nf["sg"][p])}) {how.replace("occupies", "sits in")} your {_ordinal(h)} house, and today it is {RW.get(tr_res, tr_res)} for you')
def build_signals(rep, birth_dt, date):
    nf = natal_facts(rep); sig = Sig(); facts = {}
    y, m, dd = date.year, date.month, date.day; lat, lon, tz = HOME; asof = datetime.datetime(y, m, dd, 12)
    # today's panchang at sunrise, transit, gochara from natal Moon
    p0 = PCH.panchang(y, m, dd, 6, 0, 0, tz, lat, lon); sr, ss = p0['sunrise_h'], p0['sunset_h']; h, mi = int(sr), int((sr - int(sr)) * 60)
    pc = PCH.panchang(y, m, dd, h, mi, 0, tz, lat, lon); mid = PCH.panchang(y, m, dd, int((sr + ss) / 2), int(((sr + ss) / 2 % 1) * 60), 0, tz, lat, lon); end = PCH.panchang(y, m, dd, int(ss), int((ss % 1) * 60), 0, tz, lat, lon)
    tr = TR.transit(y, m, dd, 12, 0, 0, tz, lat, lon); gm = G.assess(nf['moon_sign0'], tr['sign'], nf['bav'], nf['sav'])
    wd = date.weekday()
    # 1. dasha (maha, antar, pratyantar) + yogas the dasha lords belong to
    ds = running_dasha(rep, asof); facts['dasha'] = ds
    for role, key in (('maha', 'maha'), ('antar', 'antar'), ('praty', 'praty')):
        p = ds[key]; g = gm[p]
        planet_signals(sig, nf, p, W[role], 'dasha', f'F-DASHA-{role.upper()}', {'maha': 'Main period', 'antar': 'Sub-period', 'praty': 'Sub-sub-period'}[role], g['result'], g['house_from_moon'])
    YOGA_PLAN = {'gajakesari': ((4, 1), 1), 'budhaditya': ((0, 3), 1), 'chandra_mangala': ((1, 2), 1), 'guru_chandala': ((4, 7), -1), 'shrapit': ((6, 7), -1), 'angarak': ((2, 7), -1),
                 'kemadruma': ((1,), -1), 'sunapha': ((1,), 1), 'anapha': ((1,), 1), 'duradhara': ((1,), 1), 'vesi': ((0,), 1), 'vosi': ((0,), 1), 'ubhayachari': ((0,), 1),
                 'ruchaka': ((2,), 1), 'bhadra': ((3,), 1), 'hamsa': ((4,), 1), 'malavya': ((5,), 1), 'sasa': ((6,), 1), 'grahan': ((0, 1), -1)}
    act = []
    for yn in nf['yogas']:
        if yn not in YOGA_PLAN: continue
        parts, sgn = YOGA_PLAN[yn]
        for role in ('maha', 'antar', 'praty'):
            if ds[role] in parts:
                act.append({'yoga': yn, 'by': role})
                for q in parts:
                    for h2, (how, share) in planet_areas(nf, q).items():
                        sig.add(h2, W[role] * W['yoga_act'] * sgn * share, 'yoga', f'F-YOGA-{yn}', f'natal {yn.replace("_", " ")} yoga (planets {", ".join(_name(x) for x in parts)}) is switched on because {_name(ds[role])} runs your {role} period; touches your {_ordinal(h2)} house', ['CALCULATION_LEDGER step 4'], brief=f'your natal {yn.replace("_", " ")} yoga is switched on by the running {role} period of {_name(ds[role])}')
    facts['yogas_natal'] = nf['yogas']; facts['yogas_activated'] = act
    # 2. annual chart (Varshaphal)
    ac = annual_chart(nf, birth_dt.year, (birth_dt.month, birth_dt.day), asof); facts['varsha'] = {k: v for k, v in ac.items() if k not in ('sign_of', 'house_of')}
    GOOD_M = (1, 2, 3, 5, 9, 10, 11); mh = ac['muntha_house']; mid_ = {1: 'BK9_0318', 2: 'BK9_0319', 3: 'BK9_0320', 4: 'BK9_0321', 5: 'BK9_0322', 6: 'BK9_0323', 7: 'BK9_0324', 8: 'BK9_0325', 9: 'BK9_0326', 10: 'BK9_0327', 11: 'BK9_0328', 12: 'BK9_0329'}[mh]
    sig.add(mh, W['muntha'] * (1 if mh in GOOD_M else -1), 'varsha', 'F-MUNTHA', f'your year (Muntha) sits in the {_ordinal(mh)} house of this year\'s chart: {"supportive" if mh in GOOD_M else "difficult"} for its matters', [mid_, 'BK9_0306'], brief=f'your yearly point (Muntha) is in the {_ordinal(mh)} house of this year\'s chart ({"supportive" if mh in GOOD_M else "difficult"})')
    mlh = ac['muntha_lord_house']
    if mlh:
        mu = (-1 if mlh in (6, 8, 12) else 1 if mlh in (2, 5, 7, 9) else 0.5); mr = 'BK9_0314' if mlh in (6, 8, 12) else 'BK9_0315' if mlh in (2, 5, 7, 9) else 'BK9_0316' if mlh in (3, 10, 11) else None
        if mr: sig.add(mlh, W['muntha_lord'] * mu, 'varsha', 'F-MUNTHA-LORD', f'the lord of your year ({_name(ac["muntha_lord"])}, Muntha lord) sits in the {_ordinal(mlh)} house of this year\'s chart', [mr])
    if ac['year_lord'] is not None:
        yl = ac['year_lord']; ylh = ac['year_lord_house']; ycs, ywd = condition(yl, ac['sign_of'][yl], ylh)
        sig.add(ylh, W['year_lord'] * ycs / 2.0, 'varsha', 'F-YEAR-LORD', f'the year lord ({_name(yl)}, chosen by a simplified strength score) is {ywd}, in the {_ordinal(ylh)} house of this year\'s chart', ['BK9_0305', 'BK9_0310', 'BK9_0309'], brief=f'the year lord {_name(yl)} ({dig_word(yl, ac["sign_of"][yl])}) is in the {_ordinal(ylh)} house of this year\'s chart')
    # 3. birth-day details: Tara (birth star vs today's star), Chandra (today's Moon from natal Moon)
    t, (tn, tq) = daily.tara_of(nf['birth_nak'], pc['nakshatra']); ch = gm[1]['house_from_moon']; cgood = ch in CHANDRA_GOOD
    sig.add('init', W['tara'] * (1 if tq == 'good' else -1 if tq == 'bad' else -0.5), 'birth-vs-today', 'F-TARA', f'today\'s star is your {tn} Tara from your birth star ({tq})', ['GR-D1', 'BK13_0036'])
    sig.add('init', W['chandra'] * (1 if cgood else -1), 'birth-vs-today', 'F-CHANDRA', f'today\'s Moon is {_ordinal(ch)} from your birth Moon ({"good" if cgood else "weak"} Chandra Bala)', ['GR-D2'])
    facts['birth_vs_today'] = {'tara': tn, 'tara_quality': tq, 'chandra_house': ch, 'same_weekday_as_birth': VARA_LORD[wd] == VARA_LORD[birth_dt.weekday()], 'same_tithi_as_birth': pc['tithi'] == rep['panchang']['tithi']}
    # 4. today's panchang (day-wide, same for everybody: marked non-personal)
    n15 = (pc['tithi'] - 1) % 15 + 1
    if n15 in RIKTA or pc['tithi'] == 30: sig.add('init', -W['tithi'], 'panchang', 'F-TITHI', f'tithi {pc["tithi"]} is rikta/amavasya (everybody)', ['GR-D3'], personal=False)
    c = NAK_CLASS[pc['nakshatra']]; kd, _ = NAK_ADVICE[c]
    if kd: sig.add('init', W['nakclass'] * (1 if kd == 'do' else -1), 'panchang', 'F-NAKCLASS', f'today\'s star {NAKS[pc["nakshatra"] - 1]} is {c} class (everybody)', ['GR-D4'], personal=False)
    if pc['yoga'] in BAD_YOGA: sig.add('init', -W['yoga'], 'panchang', 'F-YOGA-DAY', f'today\'s yoga is {BAD_YOGA[pc["yoga"]]} (everybody)', ['GR-D5'], personal=False)
    if any(daily.is_vishti(x['karana_half_tithi']) for x in (pc, mid, end)): sig.add('init', -W['karana'], 'panchang', 'F-BHADRA', 'Bhadra (Vishti) runs during the day (everybody)', ['GR-D6'], personal=False)
    # day lords: weekday lord and the lord of today's star are "switched on" today; their natal condition decides what they bring to THIS person
    vl = VARA_LORD[wd]; planet_signals(sig, nf, vl, W['vara_lord'], 'day-lord', 'F-VARA-LORD', "Today's day lord", gm[vl]['result'], gm[vl]['house_from_moon'])
    nl = ORD[(pc['nakshatra'] - 1) % 9]; planet_signals(sig, nf, nl, W['nak_lord'], 'day-lord', 'F-NAK-LORD', "Today's star lord", gm[nl]['result'], gm[nl]['house_from_moon'])
    # 5. transit vs natal: gochara from natal Moon for the 9 planets, spread over the houses the transit sign touches
    SCALE = {1: W['gochara_moon'], 0: W['gochara_fast'], 2: W['gochara_fast'], 3: W['gochara_fast'], 5: W['gochara_fast'], 4: W['gochara_jup'], 6: W['gochara_sat'], 7: W['gochara_node'], 8: W['gochara_node']}
    for p in range(9):
        g = gm[p]
        if g['result'] in ('favourable', 'adverse', 'very_adverse'):
            for h2, w in daily.areas(nf, SIGNS.index(g['sign'])):
                sig.add(h2, SCALE[p] * w * (TR_NORM[g['result']] if g['result'] != 'very_adverse' else -1.5), 'transit', f'F-GOCHARA-{_name(p).upper()}',
                        f'{_name(p)} is in {g["sign"]} today, {_ordinal(g["house_from_moon"])} from your Moon ({RW[g["result"]]}{", blocked by " + g["vedha_by"] if g["vedha_by"] and g["result"] == "neutral" else ""}); that sign touches your {_ordinal(h2)} house', g['rules'],
                        brief=f'{_name(p)} is {_ordinal(g["house_from_moon"])} from your Moon today ({RW[g["result"]]}) and touches your {_ordinal(h2)} house')
    # 6. transit planet sitting on a natal planet (same sign, within orb)
    contacts = []
    for p in range(9):
        for q in range(9):
            orb = 6.0 if p == 1 else 3.0
            if p == q: continue
            dlt = abs((tr['lon'][p] - nf['lon'][q] + 180) % 360 - 180)
            if dlt <= orb:
                contacts.append({'transit': _name(p), 'natal': _name(q), 'orb_deg': round(dlt, 2)})
                g = gm[p]; cs, wds = condition(q, nf['sg'][q], nf['house_of'][q]); s = TR_NORM.get(g['result'], 0) + 0.25 * cs
                for h2, (how, share) in planet_areas(nf, q).items():
                    sig.add(h2, W['contact'] * s * share * (1 - dlt / (orb + 1e-9) * 0.5), 'transit', f'F-CONTACT-{_name(p)}-{_name(q)}', f'transiting {_name(p)} is within {dlt:.1f} deg of your natal {_name(q)} ({wds}), which {how} your {_ordinal(h2)} house; {_name(p)} is {g["result"]} for you today', ['no DB rule: classical conjunction-by-transit'])
    facts['contacts'] = contacts
    facts['today'] = {'date': date.isoformat(), 'weekday': WEEKDAYS[wd], 'tithi': pc['tithi'], 'nakshatra': NAKS[pc['nakshatra'] - 1], 'yoga': pc['yoga'], 'moon_sign': SIGNS[tr['sign'][1]],
                      'sunrise': daily.hm(sr), 'sunset': daily.hm(ss)}
    a, b = daily.rahu_window(wd, sr, ss); a2, b2 = daily.abhijit_window(sr, ss); facts['everybody_today'] = {'rahu_kaal': f'{daily.hm(a)}-{daily.hm(b)}', 'abhijit': f'{daily.hm(a2)}-{daily.hm(b2)}'}
    facts['gochara'] = {PL[p]: {k: v for k, v in gm[p].items() if k in ('sign', 'house_from_moon', 'result', 'vedha_by')} for p in range(9)}
    return nf, sig, facts

# ---------- ranking ----------
def rank(sig):
    areas = {}
    for s in sig.items:
        a = areas.setdefault(s['area'], {'net': 0.0, 'pos': 0.0, 'neg': 0.0, 'signals': []}); a['net'] += s['w']; a['signals'].append(s)
        if s['w'] > 0: a['pos'] += s['w']
        else: a['neg'] += s['w']
    for a in areas.values(): a['signals'].sort(key=lambda s: -abs(s['w']))
    return areas
def line(area, kind, a, nf):
    th, do_t, dont_t = (INIT if area == 'init' else AREA_TXT[area])
    drivers = [s for s in a['signals'] if (s['w'] > 0) == (kind == 'do')]
    # one best reason per factor family, so the line is not three copies of the same planet
    top = []; seen_g = set()
    for s in drivers:                      # best driver of each factor group first, so a line is not two copies of the same kind of reason; personal factors before day-wide ones
        if s['group'] in seen_g: continue
        seen_g.add(s['group']); top.append(s)
    top.sort(key=lambda s: (not s['personal'], -abs(s['w']))); top = top[:2]
    # guard for the user view: personal reasons first when a line would otherwise be only "everybody" facts
    return {'text': do_t if kind == 'do' else dont_t, 'area': area, 'theme': th, 'net': round(a['net'], 2), 'strength': 'clear' if abs(a['net']) >= THRESHOLD else 'mild', 'because': [s['brief'] for s in top], 'because_full': [s['why'] for s in top], 'factors': sorted({s['tag'] for s in drivers})[:12], 'groups': sorted({s['group'] for s in drivers}),
            'rules': sorted({r for s in drivers for r in s['rules']})}
def choose(areas, nf, cap=3):
    out = {'do': [], 'dont': []}
    pos = sorted(((k, a) for k, a in areas.items() if a['net'] >= MILD), key=lambda x: -x[1]['net'])[:cap]
    neg = sorted(((k, a) for k, a in areas.items() if a['net'] <= -MILD), key=lambda x: x[1]['net'])[:cap]
    out['do'] = [line(k, 'do', a, nf) for k, a in pos]; out['dont'] = [line(k, 'dont', a, nf) for k, a in neg]
    return out
SUPPORT_AREA = {'wealth': (2, 11), 'career': (10,), 'status': (10,), 'marriage': (7,), 'children': (5,), 'health': (1, 6), 'setback': ()}
def natal_support(rep, area):
    """Book rules that fired on the NATAL chart for this life area (shown as support, not scored; life-long, not day-specific). Safety filter as in guidance.py."""
    import guidance
    out = []
    if area == 'init': return out
    for sec in ('events', 'dos', 'donts', 'remedies'):
        for f in rep[sec]['items']:
            if area in SUPPORT_AREA.get(f['life_area'], ()) and not guidance._blocked(f) and f['outcome'][:1]: out.append({'id': f['id'], 'system': f['system'], 'if': f['input'][:90], 'claim': (f['remedy'] or f['outcome'])[:110]})
    return out[:3]
def person_result(name, rep, birth_dt, date):
    nf, sig, facts = build_signals(rep, birth_dt, date); areas = rank(sig); ch = choose(areas, nf)
    for k in ('do', 'dont'):
        for it in ch[k]: it['natal_rules_support'] = natal_support(rep, it['area'])
    return {'person': name, 'date': date.isoformat(), 'facts': facts, 'chosen': ch, 'area_totals': {str(k): {'net': round(a['net'], 2), 'pos': round(a['pos'], 2), 'neg': round(a['neg'], 2)} for k, a in sorted(areas.items(), key=lambda x: str(x[0]))},
            'n_signals': len(sig.items), 'signals': sig.items, 'rules_ledger': {k: rep.get('rules_ledger', {}).get(k) for k in ('total', 'evaluated', 'fired')}, 'limits': LIMITS, 'label': 'tradition claims, unmeasured; no probability'}
