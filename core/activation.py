"""Activation (maturity) ages. Two parts, both tradition claims, unmeasured:
1. Planet maturity ages. Two schemes found on the web (secondary sources, NOT primary classical texts, and they CONFLICT, e.g. Jupiter 16 vs 33-34). Both are kept, labelled, never merged.
2. Nakshatra age statements from the nakshatra books (rules/nakshatra_ages_v1.jsonl, made by tune/make_nak_ages.py), for the person's birth (Moon) nakshatra.
Output goes to the engine JSON only. Not used for the 3 DO + 3 DONT until it is validated."""
import json, glob
SCHEMES = {
    'table_A_bphs_reference_page': {'source': 'panchangbodh.com maturity table (page says BPHS/Phaladeepika/Uttara Kalamrita; no verse cited)', 'ages': {'Jupiter': (16,), 'Sun': (22,), 'Moon': (24,), 'Venus': (25,), 'Mars': (28,), 'Mercury': (32,), 'Saturn': (36,), 'Rahu': (42,), 'Ketu': (48,)}},
    'table_B_rath': {'source': "Sanjay Rath, Crux of Vedic Astrology (as quoted on sanjayprabhakaran.blogspot.com); Rahu/Ketu ages disputed in its comments", 'ages': {'Sun': (21, 22), 'Moon': (23, 24), 'Mars': (27, 28), 'Mercury': (31, 32), 'Jupiter': (33, 34), 'Venus': (25, 26), 'Saturn': (35, 36), 'Rahu': (41, 42), 'Ketu': (45, 46)}},
}
def age_years(birth, date):
    a = date.year - birth.year - ((date.month, date.day) < (birth.month, birth.day)); return a
def planet_status(age, window=1):
    """For each scheme and planet: matured / this year (|age-m|<=window) / upcoming, with the maturity age(s)."""
    out = {}
    for k, s in SCHEMES.items():
        rows = {}
        for p, ms in s['ages'].items():
            lo, hi = min(ms), max(ms)
            st = 'active_now' if lo - window <= age <= hi + window else 'matured_earlier' if age > hi + window else 'not_yet'
            rows[p] = {'ages': list(ms), 'status': st}
        out[k] = {'source': s['source'], 'planets': rows}
    return out
def load_nak_ages(path='/home/claude/jyotish-code/rules/nakshatra_ages_v1.jsonl'):
    by = {}
    for p in glob.glob(path):
        for l in open(p):
            r = json.loads(l); by.setdefault(r['nakshatra'], []).append(r)
    return by
def nak_status(nak_name, age, by):
    """Book age statements for the birth nakshatra, marked whether the current age falls inside the quoted range or near a quoted age."""
    out = []
    for r in by.get(nak_name, []):
        a = sorted(set(r['ages'])); inside = (len(a) >= 2 and a[0] <= age <= a[-1]) or any(abs(age - x) <= 1 for x in a)
        out.append({'id': r['id'], 'ages': a, 'kinds': r['kinds'], 'text': r['text'], 'source': r['source'], 'age_now_in_or_near': inside})
    return out
def person_activation(birth, date, birth_nak_name, by=None):
    age = age_years(birth, date)
    return {'age_completed': age, 'planets': planet_status(age), 'nakshatra': nak_status(birth_nak_name, age, by if by is not None else load_nak_ages()),
            'label': 'tradition claims from secondary sources and paraphrased books; schemes conflict; unmeasured'}
