"""Daily guidance (GR-D*, GR-G*, GR-A*): candidate items with weights; the user view keeps the top 3 do and 3 dont only."""
import datetime
import panchang as PCH, transit as TR, gochara as G, colour as COL
from guidance_rules import *
def hm(h): h = h % 24; m = int(round((h - int(h)) * 60)); h = int(h) + m // 60; return f'{h:02d}:{m % 60:02d}'
def natal_of(rep):
    d1 = rep['chart']['divisional']['D1']; av = rep['ashtakavarga']['bphs_plain']
    return {'moon_sign0': d1['Moon']['sign0'], 'birth_nak': rep['panchang']['nakshatra'], 'houses': rep['house_influence']['houses'],
            'bav': av['bav'][:7], 'sav': av['sav'], 'rep': rep}
def areas(natal, sign0):
    """GR-A1: natal houses touched by a transit sign, weighted by the sign's share in each house (main and minor)."""
    out = []
    for h, d in natal['houses'].items():
        w = d['shares'].get(SIGNS[sign0], 0)
        if w >= AREA_MIN_WEIGHT: out.append((int(h), w))
    return sorted(out, key=lambda x: -x[1])
def tara_of(birth_nak, day_nak):
    count = (day_nak - birth_nak) % 27 + 1; t = count % 9 or 9
    return t, TARA[t]
def is_vishti(n): return n in VISHTI
def rahu_window(weekday, sunrise, sunset):
    part = (sunset - sunrise) / 8; i = RAHU_PART[weekday]
    return sunrise + part * (i - 1), sunrise + part * i
def abhijit_window(sunrise, sunset):
    part = (sunset - sunrise) / 15
    return sunrise + part * 7, sunrise + part * 8
def _add(items, kind, text, w, why, rule, source):
    for it in items:
        if it['kind'] == kind and it['text'] == text: it['weight'] += w; it['why'].append(why); it['rule'].append(rule); return
    items.append({'kind': kind, 'text': text, 'weight': w, 'why': [why], 'rule': [rule], 'source': source})
def _quality_items(items, natal, p, g, scale, tag):
    """Turn one planet's gochara result into area-wise do/dont items (GR-A3), weighted by main/minor share."""
    if g['result'] in ('favourable', 'adverse', 'very_adverse'):
        sign0 = SIGNS.index(g['sign']); kind = 'do' if g['result'] == 'favourable' else 'dont'
        mult = 1.5 if g['result'] == 'very_adverse' else 1
        for h, w in areas(natal, sign0):
            text = AREA[h][1] if kind == 'do' else AREA[h][2]
            _add(items, kind, text, scale * w * mult, f"{tag}: {g['planet']} {g['house_from_moon']}th from Moon {g['result']}; touches house {h} weight {w}", g['rules'], 'DB gochara BK13 + house influence')
def day_items(natal, date, tz, lat, lon, rules=None):
    y, m, d = date.year, date.month, date.day
    p0 = PCH.panchang(y, m, d, 6, 0, 0, tz, lat, lon); sr, ss = p0['sunrise_h'], p0['sunset_h']
    h, mi = int(sr), int((sr - int(sr)) * 60)
    p = PCH.panchang(y, m, d, h, mi, 0, tz, lat, lon)
    mid = PCH.panchang(y, m, d, int((sr + ss) / 2), int(((sr + ss) / 2 % 1) * 60), 0, tz, lat, lon); end = PCH.panchang(y, m, d, int(ss), int((ss % 1) * 60), 0, tz, lat, lon)
    wd = date.weekday(); items = []
    tr = TR.transit(y, m, d, h, mi, 0, tz, lat, lon); signs = tr['sign']
    gm = G.assess(natal['moon_sign0'], signs, natal['bav'], natal['sav'])
    chandra_h = gm[1]['house_from_moon']; chandra_good = chandra_h in CHANDRA_GOOD
    t, (tn, tq) = tara_of(natal['birth_nak'], p['nakshatra']); net = 0
    # Rahu Kaal and Abhijit (GR-D7, D8)
    a, b = rahu_window(wd, sr, ss); _add(items, 'dont', f'Do not start new work or sign anything between {hm(a)} and {hm(b)}.', 9, 'Rahu Kaal', 'GR-D7', 'classical')
    a2, b2 = abhijit_window(sr, ss); _add(items, 'do', f'Start your most important task between {hm(a2)} and {hm(b2)}.', 7, 'Abhijit muhurta', 'GR-D8', 'classical')
    # Chandra and Tara (GR-D2, D1)
    if chandra_good: net += 1; _add(items, 'do', 'Take up important meetings and decisions today.', 7, f'Chandra Bala good (Moon {chandra_h}th from natal Moon)', 'GR-D2', 'DB BK13 Moon houses')
    else: net -= 1; _add(items, 'dont', 'Avoid major decisions and arguments today.', 8, f'Chandra Bala weak (Moon {chandra_h}th)', 'GR-D2', 'DB BK13 Moon houses')
    if tq == 'good': net += 1; _add(items, 'do', 'Start or push important work today.', 8, f'Tara {tn} good', 'GR-D1', 'classical; DB BK13_0036 consistent')
    elif tq == 'bad': net -= 1; _add(items, 'dont', 'Do not begin new ventures or take risky trips today.', 8, f'Tara {tn} bad', 'GR-D1', 'classical; DB BK13_0036')
    else: _add(items, 'dont', 'Avoid starting anything new today.', 4, f'Tara {tn} mixed', 'GR-D1', 'classical')
    # Tithi, nakshatra class, yoga, karana (GR-D3..D6)
    n = (p['tithi'] - 1) % 15 + 1
    if n in RIKTA or p['tithi'] == 30: net -= 1; _add(items, 'dont', 'Avoid starting anything new today.', 6, f"tithi {p['tithi']} rikta/amavasya", 'GR-D3', 'classical')
    if p['tithi'] in (11, 26): _add(items, 'do', 'Keep food light, or fast if you observe Ekadashi.', 5, 'Ekadashi', 'GR-D3', 'classical')
    c = NAK_CLASS[p['nakshatra']]; kind, txt = NAK_ADVICE[c]
    if kind == 'dont': net -= 1
    if kind == 'do': net += 1
    if kind: _add(items, kind, txt, 5, f'nakshatra {NAKS[p["nakshatra"] - 1]} class {c}', 'GR-D4', 'classical')
    if p['yoga'] in BAD_YOGA: net -= 1; _add(items, 'dont', 'Avoid starting anything new today.', 4, f"yoga {BAD_YOGA[p['yoga']]}", 'GR-D5', 'classical')
    if any(is_vishti(x['karana_half_tithi']) for x in (p, mid, end)): net -= 1; _add(items, 'dont', 'Avoid starting anything new today.', 4, 'Bhadra (Vishti karana) during the day', 'GR-D6', 'classical')
    # Moon area and standing slow-planet areas (GR-A1..A3)
    _quality_items(items, natal, 1, gm[1], 5, 'Moon today')
    for q in (6, 7, 8, 4): _quality_items(items, natal, q, gm[q], 3, 'standing')
    # weekday remedies and don'ts from fired natal rules (GR-D10)
    wname = WEEKDAYS[wd].lower()
    for r in (rules or []):
        txt = (r.get('remedy') or r.get('outcome') or ''); blob = (txt + ' ' + r.get('timing', '')).lower()
        if wname in blob and txt:
            first = txt.split(';')[0].strip().rstrip('.')
            if first: _add(items, 'do' if r['engine_role'] == 'remedy' else 'dont', f'On {WEEKDAYS[wd]}: {first}.', 4 * r.get('fit', 1), 'weekday rule ' + r['id'], 'GR-D10', r['source'])
    # personal colour (GR-C1, C2): from own chart, all house views, transit, dasha, weekday
    COL.colour_items(natal, date, gm, lambda k, t, w, why, r, src: _add(items, k, t, w, why, r, src), 'today')
    # conflict check: a strong "do not start" signal removes "start" advice (no self-contradicting lines)
    if any(i['kind'] == 'dont' and i['weight'] >= 4 and ('new' in i['text'] or 'begin' in i['text']) and 'between' not in i['text'] for i in items):
        items = [i for i in items if not (i['kind'] == 'do' and (i['text'].startswith('Start') or i['text'].startswith('Take up important') or i['text'].startswith('Good for lasting starts')))]
    # same for travel: a strong "risky trips" warning removes "Good for travel" advice
    if any(i['kind'] == 'dont' and i['weight'] >= 4 and 'trip' in i['text'] for i in items):
        items = [i for i in items if not (i['kind'] == 'do' and i['text'].startswith('Good for travel'))]
    grade = 'favourable' if net >= 2 else 'careful' if net <= -2 else 'mixed'
    facts = {'date': date.isoformat(), 'weekday': WEEKDAYS[wd], 'tithi': p['tithi'], 'nakshatra': NAKS[p['nakshatra'] - 1], 'yoga': p['yoga'], 'karana_half': p['karana_half_tithi'],
             'chandra_house': chandra_h, 'tara': tn, 'net': net, 'grade': grade, 'moon_sign': SIGNS[signs[1]], 'sunrise': hm(sr), 'sunset': hm(ss)}
    return items, facts
def top(items, cap=CAP):
    out = {}
    for kind in ('do', 'dont'):
        out[kind] = [i for i in sorted((x for x in items if x['kind'] == kind), key=lambda x: -x['weight'])][:cap[kind]]
    return out
