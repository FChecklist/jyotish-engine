"""Compare nakshatra book facts (astro/nk/all_facts.jsonl) with core/nakshatra.py table. Prints disagreements per book. Usage: python nak_facts_check.py FACTS.jsonl"""
import sys, os, json, re; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import nakshatra as K
ALIAS = {'moola': 'mula', 'jyestha': 'jyeshtha', 'jyeshta': 'jyeshtha', 'shatabisha': 'shatabhisha', 'satabhisha': 'shatabhisha', 'p.phalguni': 'purva phalguni', 'u.phalguni': 'uttara phalguni', 'p.ashadha': 'purva ashadha', 'u.ashadha': 'uttara ashadha', 'p.bhadrapada': 'purva bhadrapada', 'u.bhadrapada': 'uttara bhadrapada', 'mrigasira': 'mrigashira', 'mrigashirsha': 'mrigashira', 'aslesha': 'ashlesha', 'sravana': 'shravana', 'dhanista': 'dhanishta', 'visakha': 'vishakha', 'krittika': 'krittika', 'kritika': 'krittika', 'ashvini': 'ashwini', 'aswini': 'ashwini'}
idx = {n.lower(): i + 1 for i, n in enumerate(K.NAMES)}
def num(name):
    k = name.lower().strip(); k = ALIAS.get(k, k); return idx.get(k)
ok = bad = unk = 0; out = []
for l in open(sys.argv[1]):
    f = json.loads(l); a = f['attr'].lower().replace('_', ' '); n = num(f['nakshatra'])
    if n is None: unk += 1; continue
    t = K.ident(n); v = f['value'].lower()
    key = {'ruling planet': 'lord', 'ruler': 'lord', 'gana': 'gana', 'yoni': 'yoni', 'yoni animal': 'yoni', 'nadi': 'nadi'}.get(a)
    if not key: continue
    first = re.split(r'[ /,(]', v)[0] if key != 'lord' else None
    good = (t[key].lower() in v) if key != 'yoni' else (t[key].lower() in v or v.startswith(t[key].lower()))
    if key == 'gana': good = t['gana'].lower() in v or (t['gana'] == 'Rakshasa' and 'rakshas' in v) or (t['gana'] == 'Manushya' and ('manav' in v or 'manush' in v or 'human' in v))
    if key == 'nadi': good = t['nadi'].lower() in v or {'Adi': 'vata', 'Madhya': 'pitta', 'Antya': 'kapha'}[t['nadi']] in v
    if good: ok += 1
    else: bad += 1; out.append(f"{f['book']} {t['name']} {key}: table={t[key]} book={f['value']}")
print('agree', ok, 'disagree', bad, 'unknown name', unk); print('\n'.join(out))
