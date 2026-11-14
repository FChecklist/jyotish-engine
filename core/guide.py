"""User-facing guidance: ONLY 3 do + 3 dont per day and 3 do + 3 dont for the Sun-sign month, per person.
No predictions, no reasons in the user view. Reasons and rule ids stay in the 'engine' part (internal, for AI inference and audit).
Birth data is read from a private JSON path given on the command line. It is never stored in git.
Usage: python guide.py FAMILY.json YYYY-MM-DD OUTDIR [rules_glob ...]"""
import sys, json, datetime, os
import report, daily, shortterm
def person_guidance(rep, date, tz, lat, lon):
    natal = daily.natal_of(rep)
    pool = [r for sec in ('remedies', 'donts') for r in rep.get(sec, {}).get('items', [])]
    d_items, d_facts = daily.day_items(natal, date, tz, lat, lon, pool)
    m_items, m_facts = shortterm.month_items(natal, date, tz, lat, lon)
    dt, mt = daily.top(d_items), daily.top(m_items)
    plain = lambda t: {k: [i['text'] for i in v] for k, v in t.items()}
    return {'user': {'daily': plain(dt), 'month': plain(mt), 'month_window': [m_facts['window_start'][:10], m_facts['window_end'][:10]]},
            'engine': {'daily_facts': d_facts, 'month_facts': m_facts, 'daily_chosen': dt, 'month_chosen': mt,
                       'daily_candidates': sorted(d_items, key=lambda x: -x['weight']), 'month_candidates': sorted(m_items, key=lambda x: -x['weight']),
                       'label': 'tradition claims, unmeasured; probability none'}}
def text_view(name, g, date):
    u = g['user']; L = [f'{name} - {date.strftime("%a %d %b %Y")}', 'TODAY', *[f'  DO: {t}' for t in u['daily']['do']], *[f"  DON'T: {t}" for t in u['daily']['dont']],
                        f'THIS SUN-SIGN PERIOD ({u["month_window"][0]} to {u["month_window"][1]})', *[f'  DO: {t}' for t in u['month']['do']], *[f"  DON'T: {t}" for t in u['month']['dont']]]
    return '\n'.join(L)
def run(family_json, date, outdir, rules_globs):
    people = json.load(open(family_json))['people']; os.makedirs(outdir, exist_ok=True); text = []; eng = {}
    for name, p in people.items():
        dt = datetime.datetime.strptime(p['birth'], '%Y-%m-%d %H:%M:%S')
        rep = report.build(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, 5.5, p['lat'], p['lon'], asof=(date.year, date.month, date.day, 12), rules_glob=rules_globs)
        g = person_guidance(rep, date, 5.5, 28.6139, 77.209)   # today's panchang for the family home (Indirapuram, Delhi NCR); change when travelling
        text.append(text_view(name, g, date)); eng[name] = g['engine']
    open(os.path.join(outdir, f'guidance_{date}.txt'), 'w').write('\n\n'.join(text) + '\n')
    json.dump(eng, open(os.path.join(outdir, f'engine_{date}.json'), 'w'), indent=1, default=str)
    return '\n\n'.join(text)
if __name__ == '__main__':
    print(run(sys.argv[1], datetime.date.fromisoformat(sys.argv[2]), sys.argv[3], sys.argv[4:]))
