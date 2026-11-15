"""Report assembler (Step 1 of docs/REPORT_CONTRACT.md). Plain code. Output is a JSON-serialisable dict with a fixed shape.
Sections that need the rule engine (events, dos, donts, precautions, remedies) are present but EMPTY with status 'not_built' --
the report never invents content. Every section lists the settings it used."""
import json, datetime
import swisseph as swe
import charts, dasha, panchang, kp, ashtakavarga, transit, influence, apply_rules, atoms_store, strength
SCHEMA_VERSION = 1
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PLANETS = {0:'Sun',1:'Moon',2:'Mars',3:'Mercury',4:'Jupiter',5:'Venus',6:'Saturn',7:'Rahu',8:'Ketu','asc':'Lagna'}

def _sens(inp, factors=(1, 9, 10, 12, 60), minutes=(-4, 4)):
    """Birth-time sensitivity: which divisional-chart signs change if birth time is off by the given minutes."""
    y, m, d, H, M, S, tz, lat, lon = inp
    base = charts.natal(y, m, d, H, M, S, tz, lat, lon, factors=factors)['charts']
    out = {}
    for dm in minutes:
        t = datetime.datetime(y, m, d, H, M, S) + datetime.timedelta(minutes=dm)
        alt = charts.natal(t.year, t.month, t.day, t.hour, t.minute, t.second, tz, lat, lon, factors=factors)['charts']
        for f in factors:
            ch = [PLANETS[k] for k in base[f] if base[f][k][0] != alt[f][k][0]]
            out.setdefault(f'D{f}', {})[f'{dm:+d}min'] = ch
    return out

def build(y, m, d, H, M, S, tz, lat, lon, birth_time_grade='unknown', ayanamsa='LAHIRI', asof=None, rules_glob=None, ai_atoms_glob=None):
    inp = (y, m, d, H, M, S, tz, lat, lon)
    c = charts.natal(*inp, ayanamsa=ayanamsa)
    p = panchang.panchang(*inp, ayanamsa=ayanamsa)
    md = dasha.vimshottari_antar(*inp, ayanamsa=ayanamsa)
    av = ashtakavarga.ashtakavarga(*inp, ayanamsa=ayanamsa, variant='bphs_plain')
    avd = ashtakavarga.ashtakavarga(*inp, ayanamsa=ayanamsa, variant='pyjhora_default')
    d1 = c['charts'][1]
    kp_rows = {}
    for k, (sg, dg) in d1.items():
        lords = kp.lords(sg * 30 + dg)   # NOTE: uses the chart ayanamsa; KP-ayanamsa variant is a separate call (not yet wired)
        kp_rows[PLANETS[k]] = lords
    pos = {k: v[0] * 30 + v[1] for k, v in d1.items() if k != 'asc'}
    jd_ut = swe.julday(y, m, d, H + M / 60 + S / 3600 - tz)
    views = influence.bundle(jd_ut, lat, lon, pos, ayan=ayanamsa.lower())
    rep = {
        'schema_version': SCHEMA_VERSION,
        'input': {'date': f'{y:04d}-{m:02d}-{d:02d}', 'time': f'{H:02d}:{M:02d}:{S:02d}', 'tz_hours': tz, 'lat': lat, 'lon': lon, 'birth_time_grade': birth_time_grade},
        'settings': {'ayanamsa': ayanamsa, 'node': 'true', 'positions': 'PyJHora default', 'house_system_for_rules': 'declared per rule (not yet applied)',
                     'dasha_year': 'PyJHora calendar-style year; start dates +-5 days'},
        'house_influence': {'note': 'MAIN PART: each house is touched by 2-3 signs. shares sum to 1 per house; main = biggest share, minor = the rest. Rules are judged with a weighted fit over these views, never on one sign alone.',
                            'views_and_weights': {k: round(v['weight'], 4) for k, v in views.items()}, 'minor_cutoff': influence.MINOR_CUTOFF,
                            'weights_status': 'hypothesis: equal weights, to be tuned on validation data',
                            'houses': influence.house_sign_shares(views),
                            'planet_house_shares': {PLANETS[p]: {str(h): round(x, 3) for h, x in sorted(d_.items())} for p, d_ in influence.planet_house_shares(views).items()}},
        'divisional_house_influence': {'note': 'Same principle for every chart: each house of D9 and of every divisional chart is touched by 2+ signs (whole-sign view + equal-from-lagna-degree view). D9 exact; others use PyJHora degrees, unverified. Sripati/KP views exist only for D1 (need a real midheaven).', 'charts': influence.divisional_shares(c['charts'])},
        'chart': {'divisional': {f'D{f}': {PLANETS[k]: {'sign': SIGNS[v[0]], 'sign0': v[0], 'deg': round(v[1], 3)} for k, v in ch.items()} for f, ch in c['charts'].items()}},
        'panchang': p,
        'kp': {'ayanamsa_used': ayanamsa, 'lords_by_planet': kp_rows,
               'warning': 'KP normally uses Krishnamurti ayanamsa; this block uses the report ayanamsa until the KP variant is wired.'},
        'timing': {'vimshottari': [{'maha': PLANETS[a], 'antar': PLANETS[b], 'start_local': list(t), 'years': round(dur, 4)} for a, b, t, dur in md],
                   'date_uncertainty_days': 5},
        'ashtakavarga': {'bav_rows': ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Lagna'], 'bphs_plain': {'bav': av['bav'], 'sav': av['sav']},
                         'pyjhora_default': {'bav': avd['bav'], 'sav': avd['sav']}, 'note': 'Moon/Venus variant is an open question'},
        'quality': {'birth_time_grade': birth_time_grade, 'sensitivity_minutes_4': _sens(inp)},
        'events': {'status': 'not_built', 'items': []},
        'dos': {'status': 'not_built', 'items': []}, 'donts': {'status': 'not_built', 'items': []},
        'precautions': {'status': 'not_built', 'items': []}, 'remedies': {'status': 'not_built', 'items': []},
        'calibration': {'status': 'none', 'note': 'No technique has a validated record yet; all earlier skill tests were at chance. Probabilities are null.'},
    }
    if rules_glob:
        sb = strength.shadbala(y, m, d, H, M, S, tz, lat, lon); rep_sb = {'note': 'PyJHora Shadbala; ratio >= 1 means the planet meets its classical minimum (threshold is a reading choice)', 'components': sb, 'ratio': strength.ratios(sb)}
        ctx = {'strength': strength.ratios(sb), 'lon': dict(pos), 'retro': set(p for p in transit.transit(y, m, d, H, M, S, tz, lat, lon, ayanamsa=ayanamsa)['retro'] if p <= 6)}   # birth data for nakshatra / retro / combust atoms
        if asof:   # running Vimshottari maha and antar at the as-of date (dasha-linked rules need it)
            ad = datetime.datetime(*asof[:3]); run_row = None
            for a_, b_, t_, _ in md:
                if datetime.datetime(int(t_[0]), int(t_[1]), int(t_[2])) <= ad: run_row = (a_, b_)
            if run_row: ctx.update({'maha': run_row[0], 'antar': run_row[1]})
        rule_stats = {}
        fired = apply_rules.apply(apply_rules.load(rules_glob), views, {k: v[0] for k, v in d1.items() if k != 'asc'}, ctx=ctx, stats=rule_stats, ai_atoms=(atoms_store.load(ai_atoms_glob)[0] if ai_atoms_glob else None))
        rep['shadbala'] = rep_sb
        rep['rules_ledger'] = {**rule_stats, 'note': 'Every loaded rule is counted. unparsed and partial rules are NOT executed yet (see docs/CALCULATION_LEDGER.md). Nothing is silently skipped.'}
        def sect(roles):
            items = [{**f, 'label': 'tradition claim', 'probability': None, 'calibration': 'none'} for f in fired if f['engine_role'] in roles]
            return {'status': 'built_unvalidated', 'parsed_coverage_note': 'only rules the parser fully understands (about 15%) are applied', 'items': items}
        rep['events'] = sect(('event',)); rep['dos'] = sect(('do',)); rep['donts'] = sect(('donot',)); rep['remedies'] = sect(('remedy',))
        rep['rules_other'] = sect(('rule', 'foundation', 'yoga'))
        if asof:
            import guidance
            rep['guidance'] = guidance.guidance(rep, datetime.datetime(*asof[:3]))
    if asof:
        ay, am, ad, ah = asof
        rep['transit'] = transit.transit(ay, am, ad, ah, 0, 0, tz, lat, lon, ayanamsa=ayanamsa)
        rep['transit']['sign_names'] = {PLANETS[k]: SIGNS[v] for k, v in rep['transit']['sign'].items()}
    return rep

if __name__ == '__main__':
    import sys
    print(json.dumps(build(1990, 6, 15, 14, 20, 0, 5.5, 28.6, 77.2, asof=(2026, 11, 14, 17)), indent=1)[:3000])
