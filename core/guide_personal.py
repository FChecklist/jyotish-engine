"""Entry point for person-specific daily guidance (spec: docs/PERSONAL_PIPELINE.md).
Usage: python guide_personal.py FAMILY.json YYYY-MM-DD OUTDIR RULES_GLOB[,RULES_GLOB..] ATOMS_GLOB
Birth data is read from the private FAMILY.json path; nothing private is written into git. OUTDIR gets guidance_personal_DATE.txt (user view) and personal_DATE.json (full workings)."""
import sys, json, datetime, os
import report, personal
def text_view(res, date):
    L = [f'{res["person"]} - {date.strftime("%a %d %b %Y")}']
    for kind, lab in (('do', 'DO'), ('dont', "DON'T")):
        for it in res['chosen'][kind]: L.append(f'  {lab}{" (mild)" if it["strength"] == "mild" else ""}: {it["text"]}  [because {"; and ".join(it["because"][:2])}]')
        if not res['chosen'][kind]: L.append(f'  ({lab}: no area reached the minimum strength today; nothing padded)')
    return '\n'.join(L)
def run(family_json, date, outdir, rules_globs, atoms_glob):
    people = json.load(open(family_json, encoding='utf-8'))['people']; os.makedirs(outdir, exist_ok=True); out = {}; text = []
    for name, p in people.items():
        dt = datetime.datetime.strptime(p['birth'], '%Y-%m-%d %H:%M:%S')
        rep = report.build(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, 5.5, p['lat'], p['lon'], asof=(date.year, date.month, date.day, 12), rules_glob=rules_globs, ai_atoms_glob=atoms_glob)
        res = personal.person_result(name, rep, dt, date); out[name] = res; text.append(text_view(res, date))
    ev = next(iter(out.values()))['facts']['everybody_today']
    text.append(f'Same for everybody today: Rahu Kaal {ev["rahu_kaal"]} (no new work or signing); best window {ev["abhijit"]} (Abhijit).')
    open(os.path.join(outdir, f'guidance_personal_{date}.txt'), 'w', encoding='utf-8').write('\n\n'.join(text) + '\n')
    json.dump(out, open(os.path.join(outdir, f'personal_{date}.json'), 'w', encoding='utf-8'), indent=1, default=str)
    return '\n\n'.join(text)
if __name__ == '__main__':
    print(run(sys.argv[1], datetime.date.fromisoformat(sys.argv[2]), sys.argv[3], sys.argv[4].split(','), sys.argv[5]))
