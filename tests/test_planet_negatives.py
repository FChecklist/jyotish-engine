"""Tests for core/planet_negatives.py and data/planet_sign_negatives.csv (owner table 21 Nov 2026).
The expected values below are typed from the owner's wording, NOT read from the CSV, so a wrong CSV or a wrong engine both fail."""
import sys, os, csv, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core'))
import planet_negatives as PN
from zodiac import SIGNS, sign_at_house

SCOPES = ['body', 'house', 'office']
# (planet, rule_group): (negative signs, aspect numbers, single colours, combination)   -- owner rules 1..13
OWNER = {
    ('Sun', 'A'):     (['Taurus', 'Virgo'], [7], ['blue'], []),
    ('Moon', 'A'):    (['Scorpio', 'Aries'], [7], ['yellow', 'red'], ['yellow', 'red']),
    ('Mars', 'A'):    (['Cancer'], [4, 7, 8], ['blue', 'yellow'], ['blue', 'yellow']),
    ('Mercury', 'A'): (['Pisces', 'Cancer'], [7], ['blue', 'yellow', 'grey'], ['blue', 'yellow', 'grey']),
    ('Jupiter', 'A'): (['Capricorn', 'Aquarius'], [5, 7, 9], ['black', 'red'], ['black', 'red']),
    ('Venus', 'A'):   (['Gemini', 'Virgo', 'Cancer'], [7], ['blue', 'green'], ['blue', 'green']),
    ('Saturn', 'A'):  (['Aries', 'Scorpio', 'Cancer'], [3, 7, 10], ['red', 'yellow', 'grey'], ['red', 'yellow', 'grey']),
    ('Rahu', 'A'):    (['Sagittarius'], [7], ['yellow', 'green', 'black'], ['yellow', 'green', 'black']),
    ('Ketu', 'A'):    (['Gemini'], [7], ['green', 'purple'], ['green', 'purple']),
    ('Uranus', 'A'):  (['Cancer', 'Taurus', 'Libra'], [7], ['yellow'], []),
    ('Neptune', 'A'): (['Aries', 'Scorpio', 'Cancer'], [7], ['red', 'yellow'], ['red', 'yellow']),
    ('Neptune', 'B'): (['Gemini'], [7], ['green'], []),
    ('Pluto', 'A'):   (['Aries', 'Scorpio', 'Cancer', 'Leo'], [7], ['red', 'yellow'], ['red', 'yellow']),
}


def expected_flags(planet, sign):
    """Independent expectation: set of (rule_group, kind, aspect_number, flagged_sign) for `planet` sitting in `sign` (name)."""
    out = set()
    s0 = SIGNS.index(sign)
    for (p, g), (signs, asp, _, _) in OWNER.items():
        if p != planet:
            continue
        if sign in signs:
            out.add((g, 'placement', None, sign))
        for n in asp:
            t = SIGNS[sign_at_house(s0, n)]  # n-th sign counted from the planet's own sign as 1 (zodiac.sign_at_house)
            if t in signs:
                out.add((g, 'aspect', n, t))
    return out


def got_flags(planet, sign):
    r = PN.evaluate({planet: sign})
    return {(f['rule_group'], f['kind'], f['aspect_number'], f['flagged_sign']) for f in r['planets'][planet]['flags']}


def raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    return False


# ---- 1. the data file matches the owner's table: 13 rows, exact columns, one row per planet and sign group
rules = PN.load_rules()
assert len(rules) == 13
with open(PN.DATA_PATH, newline='', encoding='utf-8') as f:
    assert next(csv.reader(f)) == ['planet', 'rule_group', 'negative_signs', 'aspect_numbers', 'aspect_target_signs',
                                   'remedy_colours', 'remedy_combination', 'remedy_scopes', 'source', 'notes']
assert {(r['planet'], r['rule_group']) for r in rules} == set(OWNER)
for r in rules:
    signs, asp, singles, combo = OWNER[(r['planet'], r['rule_group'])]
    k = (r['planet'], r['rule_group'])
    assert sorted(r['negative_signs']) == sorted(signs), k
    assert r['aspect_target_signs'] == r['negative_signs'], k          # owner: aspect targets are the same sign list
    assert sorted(r['aspect_numbers']) == sorted(asp), k
    assert sorted(r['remedy_colours']) == sorted(singles), k
    assert sorted(r['remedy_combination']) == sorted(combo), k
    assert r['remedy_scopes'] == SCOPES, k
    assert r['source'] == 'owner 21 Nov 2026', k
assert sum(1 for r in rules if r['planet'] == 'Neptune') == 2 and sum(1 for r in rules if r['planet'] != 'Neptune') == 11

# ---- 2. every rule x all 12 signs: engine == independent expectation (placement, every aspect case, and nothing extra)
n_checked = 0
for planet in sorted({p for p, _ in OWNER}):
    for sign in SIGNS:
        assert got_flags(planet, sign) == expected_flags(planet, sign), (planet, sign, got_flags(planet, sign), expected_flags(planet, sign))
        n_checked += 1
assert n_checked == 12 * 12

# ---- 3. hand-computed cases from the owner's wording (n-th sign counted from the planet's own sign as 1)
P, A = 'placement', 'aspect'
CASES = [  # (planet, sign it sits in, expected {(group, kind, aspect number, flagged sign)})
    ('Sun', 'Taurus', {('A', P, None, 'Taurus')}),
    ('Sun', 'Virgo', {('A', P, None, 'Virgo')}),
    ('Sun', 'Scorpio', {('A', A, 7, 'Taurus')}),
    ('Sun', 'Pisces', {('A', A, 7, 'Virgo')}),
    ('Moon', 'Scorpio', {('A', P, None, 'Scorpio')}),
    ('Moon', 'Aries', {('A', P, None, 'Aries')}),
    ('Moon', 'Libra', {('A', A, 7, 'Aries')}),
    ('Moon', 'Taurus', {('A', A, 7, 'Scorpio')}),
    ('Mars', 'Cancer', {('A', P, None, 'Cancer')}),
    ('Mars', 'Aries', {('A', A, 4, 'Cancer')}),
    ('Mars', 'Capricorn', {('A', A, 7, 'Cancer')}),
    ('Mars', 'Sagittarius', {('A', A, 8, 'Cancer')}),
    ('Mercury', 'Pisces', {('A', P, None, 'Pisces')}),
    ('Mercury', 'Cancer', {('A', P, None, 'Cancer')}),
    ('Mercury', 'Virgo', {('A', A, 7, 'Pisces')}),
    ('Mercury', 'Capricorn', {('A', A, 7, 'Cancer')}),
    ('Jupiter', 'Capricorn', {('A', P, None, 'Capricorn')}),
    ('Jupiter', 'Aquarius', {('A', P, None, 'Aquarius')}),
    ('Jupiter', 'Virgo', {('A', A, 5, 'Capricorn')}),
    ('Jupiter', 'Cancer', {('A', A, 7, 'Capricorn')}),
    ('Jupiter', 'Taurus', {('A', A, 9, 'Capricorn')}),
    ('Jupiter', 'Libra', {('A', A, 5, 'Aquarius')}),
    ('Jupiter', 'Leo', {('A', A, 7, 'Aquarius')}),
    ('Jupiter', 'Gemini', {('A', A, 9, 'Aquarius')}),
    ('Venus', 'Gemini', {('A', P, None, 'Gemini')}),
    ('Venus', 'Virgo', {('A', P, None, 'Virgo')}),
    ('Venus', 'Cancer', {('A', P, None, 'Cancer')}),
    ('Venus', 'Sagittarius', {('A', A, 7, 'Gemini')}),
    ('Venus', 'Pisces', {('A', A, 7, 'Virgo')}),
    ('Venus', 'Capricorn', {('A', A, 7, 'Cancer')}),
    ('Saturn', 'Aries', {('A', P, None, 'Aries')}),
    ('Saturn', 'Scorpio', {('A', P, None, 'Scorpio')}),
    ('Saturn', 'Cancer', {('A', P, None, 'Cancer'), ('A', A, 10, 'Aries')}),     # placement and an aspect in one chart position
    ('Saturn', 'Libra', {('A', A, 7, 'Aries'), ('A', A, 10, 'Cancer')}),          # two aspect hits from one sign
    ('Saturn', 'Aquarius', {('A', A, 3, 'Aries'), ('A', A, 10, 'Scorpio')}),
    ('Saturn', 'Virgo', {('A', A, 3, 'Scorpio')}),
    ('Saturn', 'Taurus', {('A', A, 3, 'Cancer'), ('A', A, 7, 'Scorpio')}),
    ('Rahu', 'Sagittarius', {('A', P, None, 'Sagittarius')}),
    ('Rahu', 'Gemini', {('A', A, 7, 'Sagittarius')}),
    ('Ketu', 'Gemini', {('A', P, None, 'Gemini')}),
    ('Ketu', 'Sagittarius', {('A', A, 7, 'Gemini')}),
    ('Uranus', 'Cancer', {('A', P, None, 'Cancer')}),
    ('Uranus', 'Taurus', {('A', P, None, 'Taurus')}),
    ('Uranus', 'Libra', {('A', P, None, 'Libra')}),
    ('Uranus', 'Capricorn', {('A', A, 7, 'Cancer')}),
    ('Uranus', 'Scorpio', {('A', A, 7, 'Taurus')}),
    ('Uranus', 'Aries', {('A', A, 7, 'Libra')}),
    ('Neptune', 'Aries', {('A', P, None, 'Aries')}),
    ('Neptune', 'Scorpio', {('A', P, None, 'Scorpio')}),
    ('Neptune', 'Cancer', {('A', P, None, 'Cancer')}),
    ('Neptune', 'Libra', {('A', A, 7, 'Aries')}),
    ('Neptune', 'Gemini', {('B', P, None, 'Gemini')}),
    ('Neptune', 'Sagittarius', {('B', A, 7, 'Gemini')}),
    ('Pluto', 'Aries', {('A', P, None, 'Aries')}),
    ('Pluto', 'Scorpio', {('A', P, None, 'Scorpio')}),
    ('Pluto', 'Cancer', {('A', P, None, 'Cancer')}),
    ('Pluto', 'Leo', {('A', P, None, 'Leo')}),
    ('Pluto', 'Libra', {('A', A, 7, 'Aries')}),
    ('Pluto', 'Aquarius', {('A', A, 7, 'Leo')}),
    ('Pluto', 'Taurus', {('A', A, 7, 'Scorpio')}),
]
for planet, sign, want in CASES:
    assert got_flags(planet, sign) == want, (planet, sign, got_flags(planet, sign), want)
# every aspect number of every rule is exercised at least once above
seen = {(p, n) for p, s, w in CASES for (_g, k, n, _t) in w if k == A}
need = {(p, n) for (p, _g), (_s, asp, _c, _cb) in OWNER.items() for n in asp}
assert need <= seen, need - seen

# ---- 4. no false positives
SAFE = {'Sun': 'Aries', 'Moon': 'Gemini', 'Mars': 'Leo', 'Mercury': 'Aries', 'Jupiter': 'Aries', 'Venus': 'Aries', 'Saturn': 'Leo',
        'Rahu': 'Aries', 'Ketu': 'Aries', 'Uranus': 'Leo', 'Neptune': 'Leo', 'Pluto': 'Virgo'}
for p, s in SAFE.items():
    assert expected_flags(p, s) == set(), (p, s)                     # the safe chart really is safe by the owner's rules
r = PN.evaluate(SAFE)
assert r['negative_planets'] == [] and r['flags'] == [] and r['by_sign'] == {}
assert all((not v['negative']) and v['flags'] == [] for v in r['planets'].values())
# aspects the planet does not have must not count (owner lists only its own aspects), and counting is forward only
assert got_flags('Sun', 'Aquarius') == set()      # Taurus is the 4th from Aquarius; Sun has only the 7th (Leo)
assert got_flags('Mars', 'Pisces') == set()       # Cancer is the 5th from Pisces; Mars has 4th, 7th, 8th only
assert got_flags('Mars', 'Taurus') == set()       # Cancer is the 3rd from Taurus; not a Mars aspect
assert got_flags('Jupiter', 'Scorpio') == set()   # Aquarius is the 4th, Capricorn the 3rd from Scorpio: neither is a Jupiter aspect
assert got_flags('Mars', 'Libra') == set()        # Cancer is the 4th BACKWARD from Libra; forward 4th/7th/8th are Capricorn/Aries/Taurus
assert got_flags('Venus', 'Taurus') == set()      # own sign, not listed; 7th = Scorpio
assert got_flags('Neptune', 'Capricorn') == {('A', A, 7, 'Cancer')}   # group A fires; group B (Gemini) must not

# ---- 5. remedies: any ONE listed colour or the combination, for body, house and office, in the flagged sign's zodiac area
for (planet, g), (signs, asp, singles, combo) in OWNER.items():
    want_opts = [[c] for c in singles] + ([list(combo)] if combo else [])
    for sign in signs:                                              # placement case
        fl = [f for f in PN.evaluate({planet: sign})['flags'] if f['kind'] == P and f['rule_group'] == g]
        assert len(fl) == 1, (planet, sign)
        rem = fl[0]['remedy']
        assert rem['zodiac_area'] == sign and rem['single_colours'] == singles and rem['combination'] == combo, (planet, sign)
        assert sorted(rem['options']) == sorted(want_opts), (planet, sign, rem['options'])
        assert list(rem['by_scope']) == SCOPES and all(sorted(rem['by_scope'][s]) == sorted(want_opts) for s in SCOPES), (planet, sign)
        assert fl[0]['source'] == 'owner 21 Nov 2026'
    for n in asp:                                                   # each aspect case: remedy belongs to the ASPECTED sign
        for sign in signs:
            src = SIGNS[sign_at_house(SIGNS.index(sign), 13 - (n - 1))]   # sign from which the n-th aspect lands on `sign` (independent: walk back n-1)
            assert SIGNS[sign_at_house(SIGNS.index(src), n)] == sign
            fl = [f for f in PN.evaluate({planet: src})['flags'] if f['kind'] == A and f['aspect_number'] == n and f['rule_group'] == g]
            assert len(fl) == 1 and fl[0]['flagged_sign'] == sign and fl[0]['from_sign'] == src, (planet, n, sign, src)
            assert fl[0]['remedy']['zodiac_area'] == sign and sorted(fl[0]['remedy']['options']) == sorted(want_opts)
# the owner's single-colour rules have no combination
for planet, g in (('Sun', 'A'), ('Uranus', 'A'), ('Neptune', 'B')):
    assert OWNER[(planet, g)][3] == []
assert PN.evaluate({'Moon': 'Aries'})['flags'][0]['remedy']['options'] == [['yellow'], ['red'], ['yellow', 'red']]
assert PN.evaluate({'Sun': 'Taurus'})['flags'][0]['remedy']['options'] == [['blue']]

# ---- 6. several planets: one report, flags grouped by flagged sign, each keeps its own remedy (not merged)
r = PN.evaluate({'Sun': 'Taurus', 'Uranus': 'Scorpio', 'Moon': 'Leo'})
assert r['negative_planets'] == ['Sun', 'Uranus'] and r['planets']['Moon']['negative'] is False
assert sorted(f['planet'] for f in r['by_sign']['Taurus']) == ['Sun', 'Uranus']
assert {f['planet']: f['remedy']['options'] for f in r['by_sign']['Taurus']} == {'Sun': [['blue']], 'Uranus': [['yellow']]}
assert [f['kind'] for f in r['planets']['Uranus']['flags']] == [A] and [f['kind'] for f in r['planets']['Sun']['flags']] == [P]
assert list(r['by_sign']) == ['Taurus'] and len(r['flags']) == 2

# ---- 7. input handling
assert got_flags('Sun', 'taurus') == {('A', P, None, 'Taurus')}
assert [f['planet'] for f in PN.evaluate({'sun': 'TAURUS'})['flags']] == ['Sun']      # names are case-insensitive, output uses the canonical name
assert PN.evaluate({'Sun': 1})['planets']['Sun']['sign'] == 'Taurus'          # index 0 = Aries
assert PN.evaluate({'Sun': 0})['planets']['Sun']['sign'] == 'Aries' and PN.evaluate({'Sun': 11})['planets']['Sun']['sign'] == 'Pisces'
for alias, planet, sign in (('Indra', 'Uranus', 'Cancer'), ('Varun', 'Neptune', 'Gemini'), ('Varuna', 'Neptune', 'Gemini'),
                            ('Yum', 'Pluto', 'Leo'), ('Yama', 'Pluto', 'Leo'), ('indra', 'Uranus', 'Taurus')):
    rr = PN.evaluate({alias: sign})
    assert list(rr['planets']) == [planet] and rr['planets'][planet]['negative'], alias
assert raises(lambda: PN.evaluate({'Lagna': 'Leo'}))                              # unknown planet is an error, not silently ignored
assert PN.evaluate({'Lagna': 'Leo', 'Sun': 'Taurus'}, ignore_unknown=True)['negative_planets'] == ['Sun']
assert raises(lambda: PN.evaluate({'Sun': 'Taurs'})) and raises(lambda: PN.evaluate({'Sun': 12})) and raises(lambda: PN.evaluate({'Sun': -1}))
assert raises(lambda: PN.evaluate({'Sun': True})) and raises(lambda: PN.evaluate({'Sun': None})) and raises(lambda: PN.evaluate({'Sun': 1.0}))
assert raises(lambda: PN.evaluate({'Neptune': 'Aries', 'Varun': 'Aries'}))        # alias of the same planet given twice
assert PN.evaluate({})['flags'] == []
assert PN.from_engine_chart({0: (1, 12.5), 1: (3, 4.0), 7: 8, 'asc': (0, 1.0)}) == {'Sun': 1, 'Moon': 3, 'Rahu': 8}
assert PN.evaluate(PN.from_engine_chart({0: (1, 12.5), 1: (3, 4.0)}))['negative_planets'] == ['Sun']   # Sun Taurus; Moon Cancer is fine
assert PN.aspected_sign(0, 7) == 6 and PN.aspected_sign(11, 7) == 5 and PN.aspected_sign(9, 4) == 0
# a custom rule list can be passed
one = [r for r in rules if r['planet'] == 'Sun']
assert PN.evaluate({'Sun': 'Taurus'}, rules=one)['negative_planets'] == ['Sun'] and raises(lambda: PN.evaluate({'Moon': 'Aries'}, rules=one))

# ---- 8. the loader rejects a bad table (never silently accepts)
src = open(PN.DATA_PATH, encoding='utf-8').read().split('\n')
head, rows = src[0], [l for l in src[1:] if l]


def load_text(text):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 't.csv')
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        return PN.load_rules(p)


def mutated(i, old, new):
    """Table text with `old` replaced by `new` in data row i (the replacement must really change the row)."""
    assert old in rows[i], (i, old)
    return '\n'.join([head] + rows[:i] + [rows[i].replace(old, new, 1)] + rows[i + 1:]) + '\n'


assert len(load_text('\n'.join([head] + rows) + '\n')) == 13                      # unchanged copy loads
assert raises(lambda: load_text('\n'.join([head] + rows + [rows[0]]) + '\n'))     # duplicate (planet, group)
assert raises(lambda: load_text('\n'.join([head.replace('notes', 'comment')] + rows) + '\n'))   # wrong columns
assert raises(lambda: load_text(mutated(0, '"[""Taurus"",""Virgo""]",[7],"[""Taurus"",""Virgo""]"', '"[""Taurs"",""Virgo""]",[7],"[""Taurs"",""Virgo""]"')))   # unknown sign
assert raises(lambda: load_text(mutated(0, ',[7],', ',[1],')))                                   # aspect 1 would be the planet's own sign
assert raises(lambda: load_text(mutated(1, '"[""yellow"",""red""]","[""yellow"",""red""]"', '"[""yellow"",""blue""]","[""yellow"",""red""]"')))  # combination not the listed colours
assert raises(lambda: load_text(mutated(0, '"[""body"",""house"",""office""]"', '[]')))           # empty scopes
assert raises(lambda: load_text(mutated(0, 'Sun,A', 'sun,A')))                                  # non-canonical planet name in the table
print('test_planet_negatives ok')
