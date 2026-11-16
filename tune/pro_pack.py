"""Professional-life data pack for one person (private output, never committed).
Usage: python pro_pack.py NAME START END   (dates YYYY-MM-DD).  Reads the private family file and the person's engine report from
/home/claude/astro/private/factsheets/NAME_report.json.  Writes /home/claude/astro/private/professional/NAME_pack.json and NAME_pack.md.
Everything here is computed (no AI). Houses are whole-sign from the lagna and from the Moon. Lahiri, true node.
"""
import sys, os, json, datetime as dt
import swisseph as swe

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
LORD = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter']
BODY = {'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.TRUE_NODE}
FL = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_MOSEPH
ASPECT_OFFSETS = {'Jupiter': {0, 4, 6, 8}, 'Saturn': {0, 2, 6, 9}, 'Mars': {0, 3, 6, 7}}   # sign offsets counted from the planet's sign (own sign + aspected signs)
VIM = [('Ketu', 7), ('Venus', 20), ('Sun', 6), ('Moon', 10), ('Mars', 7), ('Rahu', 18), ('Jupiter', 16), ('Saturn', 19), ('Mercury', 17)]
CAREER_WORDS = ('career', 'job', 'profession', 'business', 'work', 'income', 'wealth', 'authority', 'status', 'government', 'employ', 'service', 'trade', 'fame', 'promotion', 'tenth', '10th', 'karma')


def jd_ist(d, hour=12.0):
    return swe.julday(d.year, d.month, d.day, hour - 5.5)


def pos(name, jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    if name == 'Ketu':
        xx, _ = swe.calc_ut(jd, swe.TRUE_NODE, FL); return (xx[0] + 180) % 360, xx[3]
    xx, _ = swe.calc_ut(jd, BODY[name], FL); return xx[0], xx[3]


def house(sign0, ref0): return (sign0 - ref0) % 12 + 1


def parse(d): return dt.date(*map(int, d.split('-')))


def main():
    name, start, end = sys.argv[1], parse(sys.argv[2]), parse(sys.argv[3])
    fam = json.load(open('/home/claude/astro/astro_family_data.json'))['people'][name]
    rep = json.load(open(f'/home/claude/astro/private/factsheets/{name}_report.json'))
    D1 = rep['chart']['divisional']['D1']; lag0 = D1['Lagna']['sign0']; moon0 = D1['Moon']['sign0']
    out = {'person': name, 'window': [str(start), str(end)], 'lagna': SIGNS[lag0], 'moon_sign': SIGNS[moon0]}
    # ---- natal career factors
    pl = {k: v for k, v in D1.items() if k != 'Lagna'}
    nat = {'planets': {k: {'sign': v['sign'], 'deg': round(v['deg'], 2), 'house_from_lagna': house(v['sign0'], lag0), 'house_from_moon': house(v['sign0'], moon0)} for k, v in pl.items()}}
    h = {}
    for n in (2, 6, 7, 10, 11):
        s0 = (lag0 + n - 1) % 12; lord = LORD[s0]
        h[n] = {'sign': SIGNS[s0], 'lord': lord, 'lord_in': SIGNS[pl[lord]['sign0']], 'lord_house': house(pl[lord]['sign0'], lag0),
                'occupants': [k for k, v in pl.items() if v['sign0'] == s0]}
    nat['houses'] = h
    nat['d10'] = {k: v['sign'] for k, v in rep['chart']['divisional']['D10'].items()}
    nat['d9'] = {k: v['sign'] for k, v in rep['chart']['divisional']['D9'].items()}
    nat['sav_by_sign'] = dict(zip(SIGNS, rep['ashtakavarga']['bphs_plain']['sav']))
    nat['bav_saturn'] = dict(zip(SIGNS, rep['ashtakavarga']['bphs_plain']['bav'][6])); nat['bav_jupiter'] = dict(zip(SIGNS, rep['ashtakavarga']['bphs_plain']['bav'][4]))
    nat['shadbala_ratio'] = dict(zip(['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'], [rep['shadbala']['ratio'][str(i)] for i in range(7)]))
    nat['house_influence_10'] = rep['house_influence']['houses']['10']
    out['natal'] = nat
    # ---- dasha: antars around window + pratyantars inside window
    rows = rep['timing']['vimshottari']
    def when(r): y, m, d_, hh = r['start_local']; return dt.datetime(int(y), int(m), int(d_)) + dt.timedelta(hours=hh)
    starts = [when(r) for r in rows]
    def at(date):
        t = dt.datetime(date.year, date.month, date.day, 12)
        idx = max(i for i, s in enumerate(starts) if s <= t); return rows[idx]['maha'], rows[idx]['antar'], idx
    ds = []
    for i, r in enumerate(rows):
        s = starts[i]; e = starts[i + 1] if i + 1 < len(rows) else s + dt.timedelta(days=700)
        if e.date() >= start and s.date() <= end: ds.append({'maha': r['maha'], 'antar': r['antar'], 'start': s.strftime('%Y-%m-%d'), 'end': e.strftime('%Y-%m-%d')})
    out['dasha_antars'] = ds
    praty = []
    order = [n for n, _ in VIM]; yrs = dict(VIM)
    for a in ds:
        s = dt.datetime.fromisoformat(a['start']); e = dt.datetime.fromisoformat(a['end']); L = (e - s).total_seconds()
        k = order.index(a['antar']); cur = s
        for j in range(9):
            lord = order[(k + j) % 9]; ln = L * yrs[lord] / 120.0; nxt = cur + dt.timedelta(seconds=ln)
            if nxt.date() >= start and cur.date() <= end:
                praty.append({'maha': a['maha'], 'antar': a['antar'], 'praty': lord, 'start': cur.strftime('%Y-%m-%d'), 'end': nxt.strftime('%Y-%m-%d')})
            cur = nxt
    out['pratyantars'] = praty
    # ---- transits: state at start, ingresses/stations in window
    def state(d):
        jd = jd_ist(d); s = {}
        for p in ('Sun', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'):
            lon, sp = pos(p, jd); s0 = int(lon // 30)
            s[p] = {'sign': SIGNS[s0], 'deg': round(lon % 30, 2), 'retro': sp < 0, 'house_from_lagna': house(s0, lag0), 'house_from_moon': house(s0, moon0), 'sav_of_sign': nat['sav_by_sign'][SIGNS[s0]]}
        return s
    out['transit_at_start'] = state(start)
    ev = []; prev = None; d = start - dt.timedelta(days=1)
    while d <= end:
        jd = jd_ist(d); cur = {}
        for p in ('Sun', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu'):
            lon, sp = pos(p, jd); cur[p] = (int(lon // 30), sp < 0, lon)
        if prev:
            for p in cur:
                if cur[p][0] != prev[p][0] and cur[p][0] is not None:
                    ev.append({'date': str(d), 'type': 'ingress', 'planet': p + ('/Ketu' if p == 'Rahu' else ''), 'into': SIGNS[cur[p][0]], 'house_from_lagna': house(cur[p][0], lag0), 'house_from_moon': house(cur[p][0], moon0), 'retro_at_time': cur[p][1]})
                if cur[p][1] != prev[p][1] and p not in ('Sun', 'Rahu'):
                    ev.append({'date': str(d), 'type': 'station', 'planet': p, 'now': 'retrograde' if cur[p][1] else 'direct', 'in': SIGNS[cur[p][0]], 'house_from_lagna': house(cur[p][0], lag0), 'house_from_moon': house(cur[p][0], moon0)})
        prev = cur; d += dt.timedelta(days=1)
    out['transit_events'] = [e for e in ev if e['date'] >= str(start)]
    # ---- combust windows (classical orbs: Mercury 14 / 12 retro, Venus 10 / 8 retro)
    comb = {}
    for p, (o, orr) in {'Mercury': (14, 12), 'Venus': (10, 8)}.items():
        state_, begin = False, None; d = start
        while d <= end:
            jd = jd_ist(d); lp, sp = pos(p, jd); ls, _ = pos('Sun', jd); sep = abs((lp - ls + 180) % 360 - 180); is_c = sep <= (orr if sp < 0 else o)
            if is_c and not state_: begin = d
            if (not is_c or d == end) and state_: comb.setdefault(p, []).append([str(begin), str(d)])
            state_ = is_c; d += dt.timedelta(days=1)
        if state_ and begin and p not in comb: comb[p] = [[str(begin), str(end)]]
    out['combust_windows'] = comb
    # ---- eclipses
    ecl = []
    try:
        jd = jd_ist(start)
        while True:
            r, t = swe.sol_eclipse_when_glob(jd, swe.FLG_MOSEPH, 0, False); dd = swe.revjul(t[0] + 5.5 / 24)
            if dt.date(int(dd[0]), int(dd[1]), int(dd[2])) > end: break
            lon, _ = pos('Sun', t[0]); ecl.append({'date': f'{int(dd[0])}-{int(dd[1]):02d}-{int(dd[2]):02d}', 'type': 'solar', 'sign': SIGNS[int(lon // 30)], 'house_from_lagna': house(int(lon // 30), lag0)}); jd = t[0] + 20
        jd = jd_ist(start)
        while True:
            r, t = swe.lun_eclipse_when(jd, swe.FLG_MOSEPH, 0, False); dd = swe.revjul(t[0] + 5.5 / 24)
            if dt.date(int(dd[0]), int(dd[1]), int(dd[2])) > end: break
            lon, _ = pos('Moon', t[0]); ecl.append({'date': f'{int(dd[0])}-{int(dd[1]):02d}-{int(dd[2]):02d}', 'type': 'lunar', 'sign': SIGNS[int(lon // 30)], 'house_from_lagna': house(int(lon // 30), lag0)}); jd = t[0] + 20
    except Exception as ex:
        ecl.append({'error': str(ex)[:120]})
    out['eclipses'] = sorted(ecl, key=lambda x: x.get('date', ''))
    # ---- past career events: dasha + slow transits at each date
    ev_path = f'/home/claude/astro/private/{name.lower()}_events_from_email.jsonl'
    past = []
    for b in fam.get('breadcrumbs_rajat', []) if name == 'Rajat' else []:
        past.append({'date': dt.datetime.strptime(b['date'], '%d %b %Y').strftime('%Y-%m-%d'), 'what': b['label'], 'precision': b.get('precision', 'd'), 'src': 'family file'})
    if os.path.exists(ev_path):
        for l in open(ev_path):
            e = json.loads(l)
            if e['category'] in ('job', 'business'): past.append({'date': e['date'], 'what': e['description'], 'precision': 'email date', 'src': 'email'})
    if name == 'Rajat':   # stated by Rajat himself in earlier chats (approximate)
        past += [{'date': '2000-07-01', 'what': 'Starts MBA at IMT Ghaziabad (month approx)', 'precision': 'month', 'src': 'stated'},
                 {'date': '2002-06-01', 'what': 'Second job, software, Chennai, via campus placement (month approx)', 'precision': 'year', 'src': 'stated'},
                 {'date': '2017-06-01', 'what': 'Leaves Ola, starts working independently (month approx)', 'precision': 'year', 'src': 'stated'}]
    tab = []
    for pe in sorted(past, key=lambda x: x['date']):
        d0 = parse(pe['date']); jd = jd_ist(d0); mh, an, _ = at(d0); row = dict(pe, maha=mh, antar=an)
        for p in ('Jupiter', 'Saturn', 'Rahu'):
            lon, sp = pos(p, jd); s0 = int(lon // 30); row[p] = SIGNS[s0] + (' R' if sp < 0 else ''); row[p + '_h_lagna'] = house(s0, lag0)
        jl, _ = pos('Jupiter', jd); sl, _ = pos('Saturn', jd); j0, s0_ = int(jl // 30), int(sl // 30)
        tenth = (lag0 + 9) % 12
        row['jupiter_touches_10th'] = ((tenth - j0) % 12) in ASPECT_OFFSETS['Jupiter']; row['saturn_touches_10th'] = ((tenth - s0_) % 12) in ASPECT_OFFSETS['Saturn']
        row['saturn_from_moon'] = house(s0_, moon0); tab.append(row)
    out['past_events'] = tab
    # ---- career-related fired rules (tradition claims) grouped by life_area, with contradiction hint
    keep = []
    for k in ('events', 'dos', 'donts', 'remedies', 'rules_other'):
        for x in rep[k]['items']:
            txt = (x['input'] + ' ' + x['outcome']).lower()
            if x.get('life_area') in ('career', 'wealth', 'status', 'setback') or any(w in txt for w in CAREER_WORDS):
                keep.append({'id': x['id'], 'role': x['engine_role'], 'area': x.get('life_area'), 'fit': x.get('fit'), 'if': x['input'][:200], 'then': x['outcome'][:240], 'timing': x.get('timing', ''), 'remedy': x.get('remedy', ''), 'src': x.get('source', '')[:60]})
    out['career_rules_fired'] = keep
    os.makedirs('/home/claude/astro/private/professional', exist_ok=True)
    json.dump(out, open(f'/home/claude/astro/private/professional/{name}_pack.json', 'w'), indent=1)
    print(name, 'pack ok;', 'praty', len(praty), 'events', len(out['transit_events']), 'eclipses', len(ecl), 'past', len(tab), 'career rules', len(keep))


if __name__ == '__main__':
    main()
