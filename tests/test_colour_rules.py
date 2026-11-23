"""Tests for core/colour_rules.py and data/owner_colour_rules.csv (owner rules of 23 Nov 2026, OWNER-2026-11-23-A).
Expected values are typed from the owner's wording and worked by hand, NOT read from the CSV or computed by the module under test,
so a wrong CSV and a wrong engine both fail. Birth data: none; every chart below is synthetic."""
import sys, os, math, random, tempfile, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'core'))
import colour_rules as CR
from zodiac import SIGNS, sign_at_house

ROOT = os.path.join(HERE, '..')


def raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    return False


# ------------------------------------------------------------------ the owner's 15 rules, typed from docs/OWNER_RULES_2026-11-23.md
# rule_no: (planet, trigger signs, use colours, avoid colours)
OWNER = {
    1:  ('Sun',     ['Taurus', 'Libra'],                ['blue'],                      ['orange']),
    2:  ('Moon',    ['Scorpio', 'Aries'],               ['red', 'yellow'],             ['white', 'black']),
    3:  ('Mars',    ['Cancer'],                         ['blue', 'yellow'],            ['red']),
    4:  ('Mercury', ['Pisces', 'Cancer'],               ['yellow', 'blue', 'grey'],    ['green', 'brown', 'red']),
    5:  ('Jupiter', ['Capricorn', 'Aquarius'],          ['black', 'red'],              ['yellow', 'golden']),
    6:  ('Venus',   ['Virgo', 'Gemini', 'Cancer'],      ['blue', 'green'],             ['white', 'silver']),
    7:  ('Saturn',  ['Aries', 'Scorpio'],               ['red', 'yellow', 'grey'],     ['white', 'black']),
    8:  ('Saturn',  ['Cancer'],                         ['yellow', 'grey'],            ['red']),
    9:  ('Rahu',    ['Sagittarius'],                    ['yellow', 'green', 'black'],  ['brown', 'blue']),
    10: ('Ketu',    ['Gemini'],                         ['green', 'purple'],           ['grey', 'silver']),
    11: ('Uranus',  ['Cancer', 'Taurus', 'Libra'],      ['yellow'],                    ['red', 'orange']),
    12: ('Neptune', ['Aries', 'Scorpio', 'Gemini'],     ['red', 'yellow', 'green'],    ['black', 'white', 'grey', 'silver']),
    13: ('Neptune', ['Cancer'],                         ['yellow'],                    ['red']),
    14: ('Pluto',   ['Aries', 'Scorpio', 'Leo'],        ['red', 'yellow'],             ['white', 'black']),
    15: ('Pluto',   ['Cancer'],                         ['yellow'],                    ['red']),
}
# house numbers each planet looks at (owner's "aspects to be seen" line); 1 = where it sits
ASP = {'Sun': [1, 7], 'Moon': [1, 7], 'Mercury': [1, 7], 'Venus': [1, 7], 'Mars': [1, 4, 7, 8], 'Jupiter': [1, 5, 7, 9], 'Saturn': [1, 3, 7, 10],
       'Rahu': [1, 7], 'Ketu': [1, 7], 'Uranus': [1, 7], 'Neptune': [1, 7], 'Pluto': [1, 7]}
BLEND_TABLE = {frozenset(('blue', 'yellow')): 'green', frozenset(('red', 'yellow')): 'orange', frozenset(('red', 'blue')): 'purple',
               frozenset(('black', 'white')): 'grey', frozenset(('red', 'green')): 'brown'}

RULES = CR.load_rules()
BY_NO = {r['rule_no']: r for r in RULES}


def all_views(signs):
    """The same sign map in D1, KP and BC."""
    return {'D1': dict(signs), 'KP': dict(signs), 'BC': dict(signs)}


def expected_hits(planet, sign):
    """Independent expectation for one planet alone in `sign` (name): {(rule_no, zodiac): weight}. Uses zodiac.sign_at_house for the counting."""
    out = {}
    s0 = SIGNS.index(sign)
    for no, (p, trig, _, _) in OWNER.items():
        if p != planet:
            continue
        for n in ASP[p]:
            z = SIGNS[sign_at_house(s0, n)]
            if z in trig:
                out[(no, z)] = 1.0 if n == 1 else 0.5
    return out


def hit_map(signs, rules=RULES):
    return {(h['rule_no'], h['zodiac']): h['weight'] for h in CR.hits_in_view(signs, rules)}


# ------------------------------------------------------------------ constants and the table
assert CR.ASPECT_HIT_WEIGHT == 0.5 and CR.PLACEMENT_HIT_WEIGHT == 1.0
assert CR.VIEW_WEIGHTS == {'D1': 0.5, 'KP': 0.25, 'BC': 0.25} and sum(CR.VIEW_WEIGHTS.values()) == 1.0
assert CR.ASPECTS == {p: tuple(v) for p, v in ASP.items()}
assert CR.BLENDS == BLEND_TABLE

assert [r['rule_no'] for r in RULES] == list(range(1, 16))
for r in RULES:
    p, trig, use, avoid = OWNER[r['rule_no']]
    assert (r['planet'], sorted(r['trigger_signs']), sorted(r['use_colours']), sorted(r['avoid_colours'])) == (p, sorted(trig), sorted(use), sorted(avoid)), r['rule_no']
    assert r['source'] == 'OWNER-2026-11-23-A'
assert 'Virgo' not in BY_NO[1]['trigger_signs'] and set(BY_NO[1]['trigger_signs']) == {'Taurus', 'Libra'}   # change from the 21 Nov table (Taurus/Virgo)
assert set(BY_NO[5]['avoid_colours']) == {'yellow', 'golden'}                                                  # rule 5 "Or" read as "And"
assert BY_NO[2]['avoid_colours'] == ['white', 'black']                                                          # owner wrote "While"

# ------------------------------------------------------------------ each of the 15 rules fires in its zodiac (placement, weight 1.0, in all three views)
for no, (p, trig, use, avoid) in OWNER.items():
    for z in trig:
        final = CR.d1_final(all_views({p: z}), RULES)
        assert z in final, (no, z)
        h = [x for x in final[z] if x['rule_no'] == no]
        assert len(h) == 1 and h[0]['weight'] == 1.0 and h[0]['by_view'] == {'D1': 1.0, 'KP': 1.0, 'BC': 1.0} and h[0]['planet'] == p, (no, z, h)
        adv = CR.advise(final, RULES)[z]
        assert no in adv['rules']
    # and it does NOT fire by placement in a sign outside its triggers
    for z in SIGNS:
        if z not in trig:
            assert (no, z) not in {k for k, w in hit_map({p: z}).items() if w == 1.0}, (no, z)

# ------------------------------------------------------------------ one planet alone, all 12 signs, against the independent expectation
for p in ASP:
    for z in SIGNS:
        assert hit_map({p: z}) == expected_hits(p, z), (p, z, hit_map({p: z}), expected_hits(p, z))

# hand-computed spot cases: (planet, sign) -> {(rule_no, zodiac): weight}
HAND = [
    ('Sun', 'Taurus', {(1, 'Taurus'): 1.0}), ('Sun', 'Libra', {(1, 'Libra'): 1.0}), ('Sun', 'Aries', {(1, 'Libra'): 0.5}),
    ('Sun', 'Scorpio', {(1, 'Taurus'): 0.5}), ('Sun', 'Virgo', {}),                 # Virgo is no longer a Sun trigger
    ('Moon', 'Libra', {(2, 'Aries'): 0.5}), ('Moon', 'Taurus', {(2, 'Scorpio'): 0.5}),
    ('Mars', 'Cancer', {(3, 'Cancer'): 1.0}), ('Mars', 'Aries', {(3, 'Cancer'): 0.5}), ('Mars', 'Capricorn', {(3, 'Cancer'): 0.5}),
    ('Mars', 'Sagittarius', {(3, 'Cancer'): 0.5}), ('Mars', 'Libra', {}), ('Mars', 'Taurus', {}),
    ('Jupiter', 'Taurus', {(5, 'Capricorn'): 0.5}), ('Jupiter', 'Cancer', {(5, 'Capricorn'): 0.5}), ('Jupiter', 'Gemini', {(5, 'Aquarius'): 0.5}),
    ('Jupiter', 'Virgo', {(5, 'Capricorn'): 0.5}), ('Jupiter', 'Leo', {(5, 'Aquarius'): 0.5}), ('Jupiter', 'Libra', {(5, 'Aquarius'): 0.5}),
    ('Jupiter', 'Capricorn', {(5, 'Capricorn'): 1.0}), ('Jupiter', 'Aries', {}),
    ('Saturn', 'Libra', {(7, 'Aries'): 0.5, (8, 'Cancer'): 0.5}), ('Saturn', 'Taurus', {(8, 'Cancer'): 0.5, (7, 'Scorpio'): 0.5}),
    ('Saturn', 'Aries', {(7, 'Aries'): 1.0}), ('Saturn', 'Cancer', {(8, 'Cancer'): 1.0, (7, 'Aries'): 0.5}), ('Saturn', 'Pisces', {}),
    ('Rahu', 'Gemini', {(9, 'Sagittarius'): 0.5}), ('Rahu', 'Aries', {}), ('Rahu', 'Leo', {}),       # Rahu 5th/9th are NOT in the owner's list
    ('Ketu', 'Sagittarius', {(10, 'Gemini'): 0.5}), ('Ketu', 'Aquarius', {}), ('Ketu', 'Libra', {}),
    ('Uranus', 'Aries', {(11, 'Libra'): 0.5}), ('Uranus', 'Scorpio', {(11, 'Taurus'): 0.5}), ('Uranus', 'Capricorn', {(11, 'Cancer'): 0.5}),
    ('Neptune', 'Libra', {(12, 'Aries'): 0.5}), ('Neptune', 'Sagittarius', {(12, 'Gemini'): 0.5}), ('Neptune', 'Capricorn', {(13, 'Cancer'): 0.5}),
    ('Pluto', 'Libra', {(14, 'Aries'): 0.5}), ('Pluto', 'Aquarius', {(14, 'Leo'): 0.5}), ('Pluto', 'Capricorn', {(15, 'Cancer'): 0.5}), ('Pluto', 'Cancer', {(15, 'Cancer'): 1.0}),
    ('Venus', 'Sagittarius', {(6, 'Gemini'): 0.5}), ('Venus', 'Pisces', {(6, 'Virgo'): 0.5}), ('Venus', 'Aries', {}),
    ('Mercury', 'Virgo', {(4, 'Pisces'): 0.5}), ('Mercury', 'Capricorn', {(4, 'Cancer'): 0.5}), ('Mercury', 'Libra', {}),
]
for p, z, exp in HAND:
    assert hit_map({p: z}) == exp, (p, z, hit_map({p: z}), exp)
# Neptune and Pluto: 12 vs 13 and 14 vs 15 never overlap in sign, so a planet fires at most one of each pair on a zodiac
assert all(len(hit_map({p: z})) <= 2 for p in ASP for z in SIGNS)

# ------------------------------------------------------------------ aspect weight is 0.5 and is used everywhere
v = all_views({'Sun': 'Aries'})                                    # Sun in Aries looks at Libra with its 7th
fin = CR.d1_final(v, RULES)
assert list(fin) == ['Libra'] and fin['Libra'][0]['weight'] == 0.5 and fin['Libra'][0]['by_view'] == {'D1': 0.5, 'KP': 0.5, 'BC': 0.5}
assert CR.advise(fin, RULES)['Libra']['weight_total'] == 0.5
assert CR.hits_in_view({'Mars': 'Aries'}, RULES)[0]['kind'] == 'aspect' and CR.hits_in_view({'Mars': 'Aries'}, RULES)[0]['aspect_number'] == 4
assert CR.hits_in_view({'Mars': 'Cancer'}, RULES)[0]['kind'] == 'placement' and CR.hits_in_view({'Mars': 'Cancer'}, RULES)[0]['aspect_number'] is None

# ------------------------------------------------------------------ D1 Final = 0.5 D1 + 0.25 KP + 0.25 BC
def final_w(d1, kp, bc, zodiac):
    f = CR.d1_final({'D1': {'Sun': d1}, 'KP': {'Sun': kp}, 'BC': {'Sun': bc}}, RULES)
    return {h['rule_no']: h['weight'] for h in f.get(zodiac, [])}.get(1, 0.0)

assert final_w('Taurus', 'Taurus', 'Taurus', 'Taurus') == 1.0                      # placement in all three: weights sum to 1
assert final_w('Taurus', 'Pisces', 'Pisces', 'Taurus') == 0.5                      # D1 only
assert final_w('Pisces', 'Taurus', 'Pisces', 'Taurus') == 0.25                     # KP only
assert final_w('Pisces', 'Pisces', 'Taurus', 'Taurus') == 0.25                     # Bhav Chalit only
assert final_w('Taurus', 'Taurus', 'Pisces', 'Taurus') == 0.75
assert final_w('Taurus', 'Pisces', 'Taurus', 'Taurus') == 0.75
assert final_w('Pisces', 'Taurus', 'Taurus', 'Taurus') == 0.5
assert final_w('Scorpio', 'Pisces', 'Pisces', 'Taurus') == 0.25                    # D1 aspect only (Sun in Scorpio, 7th = Taurus): 0.5 x 0.5
assert final_w('Scorpio', 'Scorpio', 'Scorpio', 'Taurus') == 0.5                   # aspect in all three: 0.5 x (0.5+0.25+0.25)
# mixed example worked by hand: Sun D1 Taurus, KP Aries, BC Libra
mix = CR.d1_final({'D1': {'Sun': 'Taurus'}, 'KP': {'Sun': 'Aries'}, 'BC': {'Sun': 'Libra'}}, RULES)
assert {z: [h['weight'] for h in hs] for z, hs in mix.items()} == {'Taurus': [0.5], 'Libra': [0.375]}   # Libra: BC placement 0.25 x 1.0 + KP aspect 0.25 x 0.5
assert mix['Libra'][0]['by_view'] == {'D1': 0.0, 'KP': 0.5, 'BC': 1.0}
assert raises(lambda: CR.d1_final({'D1': {}, 'KP': {}}, RULES))                    # all three views are required
assert raises(lambda: CR.d1_final({'D1': {}, 'KP': {}, 'BC': {}, 'X': {}}, RULES))

# ------------------------------------------------------------------ colour advice = union(use) - union(avoid); avoid colours are never returned
def advice_for(signs):
    return CR.advise(CR.d1_final(all_views(signs), RULES), RULES)

a = advice_for({'Sun': 'Taurus'})['Taurus']                                         # rule 1 alone
assert a['pure_colours'] == ['blue'] and a['avoid_union'] == ['orange'] and a['n_negatives'] == 1 and not a['blend_needed'] and a['blends'] == []
assert a['recommended'] == [{'colours': ['blue'], 'result': 'blue'}]
a = advice_for({'Sun': 'Taurus', 'Uranus': 'Taurus'})['Taurus']                    # rules 1 + 11: use blue, yellow; avoid orange, red
assert sorted(a['pure_colours']) == ['blue', 'yellow'] and sorted(a['avoid_union']) == ['orange', 'red']
a = advice_for({'Venus': 'Cancer', 'Mercury': 'Cancer'})['Cancer']                 # rules 6 + 4: green is used by Venus but avoided by Mercury -> not returned
assert 'green' in a['use_union'] and 'green' in a['avoid_union'] and 'green' not in a['pure_colours'] and sorted(a['pure_colours']) == ['blue', 'grey', 'yellow']
a = advice_for({'Rahu': 'Sagittarius'})['Sagittarius']                              # rule 9: yellow, green, black; not brown or blue
assert a['pure_colours'] == ['yellow', 'green', 'black'] and all(c not in a['pure_colours'] for c in ('brown', 'blue'))
a = advice_for({'Jupiter': 'Aquarius'})['Aquarius']                                 # rule 5: black, red; not yellow or golden
assert a['pure_colours'] == ['black', 'red'] and a['avoid_union'] == ['yellow', 'golden']

# fuzz: 3000 random charts (12 planets, a random sign map per view, random D9): no returned colour is ever an avoid colour; blend table respected
rnd = random.Random(20261123)
seen_blend = seen_unavailable = seen_anti = 0
for _ in range(3000):
    views = {v: {p: SIGNS[rnd.randrange(12)] for p in ASP} for v in CR.VIEW_WEIGHTS}
    d9 = {p: rnd.randrange(12) for p in ASP}
    adv = CR.advise(CR.d1_final(views, RULES), RULES)
    d9v = CR.validate_d9(adv, d9, RULES)
    for z, a in adv.items():
        assert a['pure_colours'] == [c for c in a['use_union'] if c not in a['avoid_union']]
        for o in a['recommended']:
            assert o['result'] not in a['avoid_union'], (z, o, a['avoid_union'])
        for b in a['blends']:
            assert BLEND_TABLE[frozenset(b['components'])] == b['result'] and b['result'] not in a['avoid_union'] and set(b['components']) <= set(a['use_union'])
        if a['n_negatives'] >= 2:                                                  # two or more negatives on one zodiac: blends come first, or are reported unavailable
            assert (a['blends'] and a['recommended'][0]['colours'] == a['blends'][0]['components']) or a['blend_unavailable']
            seen_blend += bool(a['blends']); seen_unavailable += a['blend_unavailable']
        d = d9v[z]
        for o in d['final_recommended']:
            assert o['result'] not in a['avoid_union'] and o['result'] not in d['d9_avoid'], (z, o)
        seen_anti += bool(d['anti_colours'])
assert seen_blend > 50 and seen_unavailable > 50 and seen_anti > 50, (seen_blend, seen_unavailable, seen_anti)   # the fuzz really exercised all three paths

# ------------------------------------------------------------------ two negatives in one zodiac force a blend
f = advice_for({'Mars': 'Cancer', 'Venus': 'Cancer'})['Cancer']                    # rules 3 + 6: use blue, yellow, green; avoid red, white, silver
assert f['n_negatives'] == 2 and f['blend_needed'] and f['rules'] == [3, 6]
assert f['blends'] == [{'components': ['blue', 'yellow'], 'result': 'green', 'uses_avoided_component': False}]
assert f['recommended'][0] == {'colours': ['blue', 'yellow'], 'result': 'green'}     # the blend is offered first (owner: use a combination)
assert [o['result'] for o in f['recommended'][1:]] == ['blue', 'yellow', 'green']     # then the pure single colours
f = advice_for({'Mars': 'Cancer', 'Mercury': 'Cancer'})['Cancer']                  # rules 3 + 4: blue+yellow=green but Mercury avoids green -> rejected
assert f['n_negatives'] == 2 and f['blends'] == [] and f['blend_unavailable'] and sorted(f['pure_colours']) == ['blue', 'grey', 'yellow']
f = advice_for({'Mars': 'Cancer'})['Cancer']                                         # one negative: no blend needed, none offered
assert f['n_negatives'] == 1 and not f['blend_needed'] and f['blends'] == [] and not f['blend_unavailable']
f = advice_for({'Moon': 'Aries', 'Saturn': 'Aries', 'Pluto': 'Aries'})['Aries']      # three negatives (rules 2, 7, 14): use red, yellow, grey; avoid white, black
assert f['n_negatives'] == 3 and f['rules'] == [2, 7, 14] and f['blend_needed']
assert {b['result'] for b in f['blends']} == {'orange'}                              # red+yellow only; black+white=grey not possible (both avoided and not in use)
# a zodiac hit by a planet's ASPECT only (weight 0.5) plus another's placement also counts as two negatives
f = advice_for({'Mars': 'Cancer', 'Saturn': 'Taurus'})['Cancer']                     # Saturn in Taurus looks at Cancer with its 3rd (rule 8)
assert f['n_negatives'] == 2 and f['weight_total'] == 1.5 and f['rules'] == [3, 8]

# nothing pure remains (synthetic rules; the real table never empties a zodiac). Every use colour is avoided by the other rule, so only blends are left.
# red+yellow=orange is rejected because orange is an avoid colour; blue+yellow=green and red+blue=purple land on free colours and are kept.
SYN_A = {'rule_no': 1, 'planet': 'Sun', 'trigger_signs': ['Aries'], 'use_colours': ['blue', 'yellow'], 'avoid_colours': ['red', 'orange']}
SYN_B = {'rule_no': 2, 'planet': 'Moon', 'trigger_signs': ['Aries'], 'use_colours': ['red'], 'avoid_colours': ['blue', 'yellow']}
sa = CR.zodiac_advice([SYN_A, SYN_B])
assert sa['pure_colours'] == [] and sa['blend_needed'] and sa['n_negatives'] == 2
assert [(b['components'], b['result']) for b in sa['blends']] == [(['blue', 'yellow'], 'green'), (['red', 'blue'], 'purple')]
assert all(b['uses_avoided_component'] for b in sa['blends'])                                  # ingredients are avoided colours: flagged, owner question (e)
assert [o['result'] for o in sa['recommended']] == ['green', 'purple']
# a single negative with nothing pure left also gets blends (rule avoids its own ingredients' result only)
SYN_ONE = {'rule_no': 9, 'planet': 'Sun', 'trigger_signs': ['Aries'], 'use_colours': ['red', 'yellow'], 'avoid_colours': ['black']}
assert CR.zodiac_advice([SYN_ONE])['blends'] == [] and CR.zodiac_advice([SYN_ONE])['pure_colours'] == ['red', 'yellow']   # pure remains -> no blend for one negative
# every blend landing on an avoid colour is rejected, whatever the avoid set
for pair, res in BLEND_TABLE.items():
    a_, b_ = sorted(pair)
    assert CR.blend_options([a_, b_], [res]) == [] and len(CR.blend_options([a_, b_], [])) == 1

# ------------------------------------------------------------------ D9 validation
# real rules: Venus alone in Cancer (rule 6: blue, green; avoid white, silver) in D1 Final; Mercury in Cancer in D9 (rule 4 avoids green) -> green is anti
adv = advice_for({'Venus': 'Cancer'})
d = CR.validate_d9(adv, {'Sun': SIGNS.index('Leo')}, RULES)['Cancer']                 # D9 with nothing on Cancer
assert d['status'] == 'approved' and d['anti_colours'] == [] and d['mix'] == [] and [o['result'] for o in d['final_recommended']] == ['blue', 'green']
d = CR.validate_d9(adv, {'Mercury': SIGNS.index('Cancer')}, RULES)['Cancer']
assert d['anti_colours'] == ['green'] and d['status'] == 'adjusted' and [o['result'] for o in d['kept']] == ['blue']
assert d['mix'] == [] and [o['result'] for o in d['final_recommended']] == ['blue']     # blue+yellow=green would land on D9's avoid colour -> no mix
assert [h['rule_no'] for h in d['d9_hits']] == [4] and d['d9_avoid'] == ['green', 'brown', 'red']
# D9 aspect also counts: Mercury in Capricorn in D9 looks at Cancer with its 7th (weight 0.5) and still makes green anti
d = CR.validate_d9(adv, {'Mercury': SIGNS.index('Capricorn')}, RULES)['Cancer']
assert d['anti_colours'] == ['green'] and d['d9_hits'][0]['kind'] == 'aspect' and d['d9_hits'][0]['weight'] == 0.5
# a D9 rule on a DIFFERENT zodiac does not matter
d = CR.validate_d9(adv, {'Mercury': SIGNS.index('Pisces')}, RULES)
assert d['Cancer']['status'] == 'approved'

# conflict that a mix resolves (synthetic rules): D1 Final says use blue (avoid orange); D9 says avoid blue, use yellow -> blue+yellow=green satisfies both
D1R = {'rule_no': 1, 'planet': 'Sun', 'trigger_signs': ['Aries'], 'use_colours': ['blue'], 'avoid_colours': ['orange']}
D9R = {'rule_no': 2, 'planet': 'Moon', 'trigger_signs': ['Aries'], 'use_colours': ['yellow'], 'avoid_colours': ['blue']}
syn = [D1R, D9R]
adv = CR.advise(CR.d1_final(all_views({'Sun': 'Aries'}), syn), syn)
assert adv['Aries']['rules'] == [1] and adv['Aries']['pure_colours'] == ['blue']
d = CR.validate_d9(adv, {'Moon': 0}, syn)['Aries']                                  # D9: Moon in Aries (index 0)
assert d['status'] == 'adjusted' and d['anti_colours'] == ['blue'] and d['kept'] == []
assert d['mix'] == [{'components': ['blue', 'yellow'], 'result': 'green', 'uses_avoided_component': True}]
assert d['final_recommended'] == [{'colours': ['blue', 'yellow'], 'result': 'green'}]
assert 'green' not in adv['Aries']['avoid_union'] and 'green' not in d['d9_avoid']          # the mix is acceptable in D1 Final and in D9
# if D9 also avoids the only possible result, nothing is left: unresolved
D9R2 = dict(D9R, avoid_colours=['blue', 'green'])
d = CR.validate_d9(adv, {'Moon': 0}, [D1R, D9R2])['Aries']
assert d['status'] == 'unresolved' and d['final_recommended'] == [] and d['mix'] == []
# the mix must use at least one D1 Final colour: a blend of D9 colours only is not offered. Here red+yellow=orange is free of avoid colours but has no D1 Final colour.
D1R2 = dict(D1R, avoid_colours=['white'])
D9R3 = {'rule_no': 2, 'planet': 'Moon', 'trigger_signs': ['Aries'], 'use_colours': ['red', 'yellow'], 'avoid_colours': ['blue']}
adv2 = CR.advise(CR.d1_final(all_views({'Sun': 'Aries'}), [D1R2]), [D1R2, D9R3])      # D1 Final fires rule 1 only (Sun); the Moon rule is evaluated in D9 only
d = CR.validate_d9(adv2, {'Moon': 0}, [D1R2, D9R3])['Aries']
assert [m['components'] for m in d['mix']] == [['blue', 'yellow'], ['red', 'blue']] and [m['result'] for m in d['mix']] == ['green', 'purple']
assert 'orange' not in [m['result'] for m in d['mix']]

# ------------------------------------------------------------------ longitudes -> views (Bhav Chalit, KP, effective sign)
assert [CR.navamsha_sign(x) for x in (0.0, 3.33, 3.34, 30.0, 359.99)] == [0, 0, 1, 9, 11]      # 9 x longitude: Aries start, 3 deg 20 min is the 2nd navamsha (Taurus), Taurus 0 deg = Capricorn, Pisces end
assert CR.navamsha_sign(-0.01) == 11 and CR.navamsha_sign(360.0) == 0
# Bhav Chalit: lagna 100 deg (Cancer). House 1 spans 85 to 115, house 2 115 to 145, house 12 55 to 85
for lon, h in ((85.0, 1), (100.0, 1), (114.99, 1), (115.0, 2), (84.99, 12), (55.0, 12), (54.99, 11), (354.0, 9), (100.0 + 180, 7), (265.0, 7)):
    assert CR.bhav_chalit_house(lon, 100.0) == h, (lon, h, CR.bhav_chalit_house(lon, 100.0))
assert CR.bhav_chalit_house(5.0, 350.0) == 2 and CR.bhav_chalit_house(334.9, 350.0) == 12 and CR.bhav_chalit_house(335.0, 350.0) == 1      # wrap round 360
# effective sign = lagna sign + (house - 1)
assert CR.effective_sign(3, 1) == 3 and CR.effective_sign(3, 2) == 4 and CR.effective_sign(3, 12) == 2 and CR.effective_sign(11, 2) == 0
# KP houses from explicit (unequal) cusps, cusp 1 = lagna = 100
CUSPS = [100, 118, 142, 175, 212, 250, 280, 298, 322, 355, 32, 68]
for lon, h in ((100.0, 1), (117.99, 1), (118.0, 2), (99.99, 12), (68.0, 12), (67.99, 11), (354.9, 9), (355.0, 10), (31.9, 10), (32.0, 11), (250.0, 6)):
    assert CR.kp_house(lon, CUSPS) == h, (lon, h)
assert raises(lambda: CR.kp_house(10.0, CUSPS[:11])) and raises(lambda: CR.kp_house(10.0, CUSPS[::-1])) and raises(lambda: CR.kp_house(float('nan'), CUSPS))
# build_views: D1 sign, KP / BC effective sign, moved planets
B = CR.build_views(100.0, {'Sun': 116.0, 'Moon': 100.5, 'Saturn': 84.0, 'Indra': 200.0}, CUSPS)
assert B['houses']['D1'] == {'Sun': 1, 'Moon': 1, 'Saturn': 12, 'Uranus': 4}              # lagna sign Cancer (index 3): Cancer 1 ... Gemini 12; 200 deg = Libra = 4th
assert B['views']['D1'] == {'Sun': 3, 'Moon': 3, 'Saturn': 2, 'Uranus': 6}
assert B['houses']['KP'] == {'Sun': 1, 'Moon': 1, 'Saturn': 12, 'Uranus': 4} and B['houses']['BC'] == {'Sun': 2, 'Moon': 1, 'Saturn': 12, 'Uranus': 4}   # Sun 116: BC house 2 (115 to 145), KP house 1 (100 to 118)
assert B['views']['BC']['Sun'] == 4 and B['views']['KP']['Sun'] == 3                      # BC house 2 -> Leo (index 4)
assert B['moved'] == ['Sun'] and B['d9']['Sun'] == CR.navamsha_sign(116.0)
assert raises(lambda: CR.build_views(100.0, {'Sun': 10.0}, [101] + CUSPS[1:]))             # KP cusp 1 must equal the lagna
assert raises(lambda: CR.build_views(100.0, {'Sun': 10.0, 'Lagna': 100.0}, CUSPS))         # unknown planet name is an error, not skipped
assert raises(lambda: CR.build_views(100.0, {'Uranus': 10.0, 'Indra': 20.0}, CUSPS))       # alias given twice
# KP / Bhav Chalit moves change the zodiac that gets hit: Sun at 116 deg is Cancer in D1 (no Sun rule) and Leo in BC (no Sun rule) -> no hits; Sun at 54 deg:
B = CR.build_views(100.0, {'Sun': 54.0}, CUSPS)                                            # D1 Taurus (index 1); BC house 11 (from lagna Cancer: Taurus is house 11, 54 is in 25..55 = house 11)
assert B['views']['D1']['Sun'] == 1 and B['houses']['BC']['Sun'] == 11 and B['views']['BC']['Sun'] == 1
assert B['houses']['KP']['Sun'] == 11 and B['views']['KP']['Sun'] == 1 and B['moved'] == []

# ------------------------------------------------------------------ the full pipeline on a synthetic chart (explicit KP cusps, no ephemeris)
LON = {'Sun': 54.0, 'Moon': 190.0, 'Mars': 96.0, 'Mercury': 70.0, 'Jupiter': 280.0, 'Venus': 101.0, 'Saturn': 262.0, 'Rahu': 255.0, 'Ketu': 75.0, 'Uranus': 40.0, 'Neptune': 335.0, 'Pluto': 15.0}
res = CR.analyse(100.0, LON, kp_cusp_list=CUSPS)
json.dumps(res)                                                                              # the whole report is plain data
assert res['lagna_sign'] == 'Cancer' and res['view_weights'] == {'D1': 0.5, 'KP': 0.25, 'BC': 0.25} and res['aspect_hit_weight'] == 0.5
assert set(res['views']) == {'D1', 'KP', 'BC'} and set(res['d9_validation']) == set(res['zodiacs'])
assert res['views']['D1']['Sun'] == 'Taurus' and res['views']['D1']['Mars'] == 'Cancer' and res['views']['D1']['Venus'] == 'Cancer'   # 90 to 120 deg is Cancer
canc = {h['rule_no']: h for h in res['zodiacs']['Cancer']['hits']}
assert canc[3]['by_view']['D1'] == 1.0 and canc[6]['by_view']['D1'] == 1.0 and res['zodiacs']['Cancer']['n_negatives'] >= 2   # Mars (3) and Venus (6) sit in Cancer in D1
assert res['zodiacs']['Cancer']['blend_needed'] and res['zodiacs']['Cancer']['weight_total'] == sum(h['weight'] for h in canc.values())
assert raises(lambda: CR.analyse(100.0, LON))                                               # neither cusps nor jd/lat/lon
assert CR.analyse(100.0, {}, kp_cusp_list=CUSPS)['zodiacs'] == {}                         # no planets given -> nothing evaluated

# ------------------------------------------------------------------ Placidus (KP) cusps. Needs pyswisseph; the check is independent of Swiss Ephemeris' own Placidus routine.
try:
    import swisseph as swe
except ImportError:
    swe = None
    print('SKIPPED Placidus checks: pyswisseph not installed')


def placidus_cusps_independent(armc, eps, lat):
    """Tropical Placidus cusps 11, 12, 2, 3 by the semi-arc method (degrees), solved by iteration. Cusps 5, 6, 8, 9 are opposite. Written for this test only."""
    rad, deg = math.radians, math.degrees

    def lon_of_ra(ra):                         # ecliptic longitude of the ecliptic point with right ascension ra
        return deg(math.atan2(math.sin(rad(ra)), math.cos(rad(ra)) * math.cos(rad(eps)))) % 360

    def dsa(lam):                              # diurnal semi-arc of the ecliptic point at longitude lam
        d = math.asin(math.sin(rad(eps)) * math.sin(rad(lam)))
        return deg(math.acos(-math.tan(rad(lat)) * math.tan(d)))

    def solve(start, f):
        ra = (armc + start) % 360
        for _ in range(200):
            ra = (armc + f(dsa(lon_of_ra(ra)))) % 360
        return lon_of_ra(ra)
    return {11: solve(30, lambda h: h / 3), 12: solve(60, lambda h: 2 * h / 3),
            2: solve(120, lambda h: h + (180 - h) / 3), 3: solve(150, lambda h: h + 2 * (180 - h) / 3)}


def adiff(a, b):
    return abs((a - b + 180) % 360 - 180)


if swe is not None:
    # synthetic charts: (julian day UT, latitude, east longitude), no real person's data
    for jd, lat, lon in ((2451545.0, 28.0, 77.0), (2458000.25, 19.0, 73.0), (2460000.6, -33.9, 18.4), (2455000.1, 51.5, -0.1), (2459000.9, 12.9, 77.6)):
        for ay in ('lahiri', 'kp'):
            cu = CR.kp_cusps(jd, lat, lon, ay)
            assert len(cu) == 12
            swe.set_sid_mode(swe.SIDM_LAHIRI if ay == 'lahiri' else swe.SIDM_KRISHNAMURTI, 0, 0)
            ayan = swe.get_ayanamsa_ex_ut(jd, swe.FLG_SIDEREAL)[1]
            trop_cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', 0)
            eps = swe.calc_ut(jd, swe.ECL_NUT)[0][0]
            ind = placidus_cusps_independent(ascmc[2], eps, lat)
            for h, t in ind.items():
                assert adiff(cu[h - 1], t - ayan) < 1e-5, (jd, lat, ay, h, cu[h - 1], t - ayan)       # sidereal cusp = independent tropical cusp - ayanamsa
            assert adiff(cu[0], ascmc[0] - ayan) < 1e-6 and adiff(cu[9], ascmc[1] - ayan) < 1e-6        # cusp 1 = sidereal ascendant, cusp 10 = sidereal MC
            for h in range(6):
                assert adiff(cu[h + 6], cu[h] + 180) < 1e-6                                           # opposite cusps are 180 apart
            CR.kp_house(10.0, cu)                                                                      # a real Placidus cusp list is accepted by the house finder
        a1, a2 = CR.kp_cusps(jd, lat, lon, 'lahiri'), CR.kp_cusps(jd, lat, lon, 'kp')
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0); l1 = swe.get_ayanamsa_ex_ut(jd, swe.FLG_SIDEREAL)[1]
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0); l2 = swe.get_ayanamsa_ex_ut(jd, swe.FLG_SIDEREAL)[1]
        assert all(adiff(x - y, l2 - l1) < 1e-6 for x, y in zip(a1, a2)) and abs(l2 - l1) > 0.05        # the ayanamsa parameter really moves the cusps (Lahiri vs KP differ)
    assert raises(lambda: CR.kp_cusps(2451545.0, 70.0, 20.0)) and raises(lambda: CR.kp_cusps(2451545.0, -67.0, 20.0))   # Placidus undefined in the polar circles: refused
    assert raises(lambda: CR.kp_cusps(2451545.0, 28.0, 77.0, "tropical"))
    # navamsha formula agrees with core/influence.py (the engine's D9)
    import influence
    for x in [i * 0.37 for i in range(0, 973)]:
        assert CR.navamsha_sign(x) == influence.navamsha_sign(x), x
    # full pipeline with computed Placidus cusps: lagna from the same sidereal frame
    jd, lat, lon = 2451545.0, 28.0, 77.0
    cu = CR.kp_cusps(jd, lat, lon, 'lahiri')
    res = CR.analyse(cu[0], LON, jd_ut=jd, lat=lat, lon=lon, ayanamsa='lahiri')
    assert res['ayanamsa'] == 'lahiri' and res['lagna_sign'] == SIGNS[int(cu[0] // 30)] and set(res['views']['KP']) == set(LON)
    json.dumps(res)

# ------------------------------------------------------------------ loader checks
head = open(os.path.join(ROOT, 'data', 'owner_colour_rules.csv'), encoding='utf-8').read().split('\n')
rows = [r for r in head[1:] if r]
header = head[0]


def load_text(txt):
    with tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False, encoding='utf-8', newline='') as f:
        f.write(txt)
    try:
        return CR.load_rules(f.name)
    finally:
        os.unlink(f.name)


def mutated(i, old, new):
    assert old in rows[i], (i, old)
    return '\n'.join([header] + rows[:i] + [rows[i].replace(old, new, 1)] + rows[i + 1:]) + '\n'


assert len(load_text('\n'.join([header] + rows) + '\n')) == 15
assert len(rows) == 15 and rows[0].startswith('1,Sun,') and rows[14].startswith('15,Pluto,')
assert raises(lambda: load_text('\n'.join([header] + rows + [rows[0]]) + '\n'))                         # duplicate rule_no
assert raises(lambda: load_text('\n'.join([header.replace('note', 'comment')] + rows) + '\n'))          # wrong columns
assert raises(lambda: load_text(mutated(0, '"[""Taurus"",""Libra""]"', '"[""Taurs"",""Libra""]"')))       # unknown sign
assert raises(lambda: load_text(mutated(0, '"[""blue""]"', '"[""bluee""]"')))                           # unknown colour
assert raises(lambda: load_text(mutated(0, '"[""blue""]","[""orange""]"', '"[""blue""]","[""blue""]"')))  # colour both used and avoided
assert raises(lambda: load_text(mutated(0, '1,Sun,', 'x,Sun,')))                                       # bad rule number
assert raises(lambda: load_text(mutated(0, '1,Sun,', '1,sun,')))                                        # non-canonical planet name
assert raises(lambda: load_text(mutated(0, '1,Sun,', '1,Chiron,')))                                     # planet with no aspect list
assert raises(lambda: load_text(header + '\n' + '1,Sun,"[""Aries""]"\n'))                               # too few cells
assert raises(lambda: load_text('\n'.join([header] + [rows[0] + ',extra'] + rows[1:]) + '\n'))         # too many cells
assert raises(lambda: load_text(mutated(0, '"[""orange""]"', '[]')))                                    # empty avoid list
assert raises(lambda: CR.hits_in_view({'Sun': 'Aeries'}, RULES)) and raises(lambda: CR.hits_in_view({'Sun': 12}, RULES))
assert raises(lambda: CR.hits_in_view({'Lagna': 'Aries'}, RULES))

# ------------------------------------------------------------------ the verbatim owner text is kept as received (typos included), and the engine does not read the doc
doc = open(os.path.join(ROOT, 'docs', 'OWNER_RULES_2026-11-23.md'), encoding='utf-8').read()
for frag in ('aquarious', 'sagitarius', 'scropio', 'While or Black', '1st, 3th, 7th and 10th', 'KP nad 25% is Bhav Chalit', 'Or do not use Yellow or golden',
             'use blue . And in this case do not use Orange', 'do not use Green or Brown or Red in this condition,', 'than in that zodiac', 'neptune is in cancer',
             'the 100% main effect is when that planet is sitting in that zodiac', 'satisfies the D1 FINAL and D9 both'):
    assert frag in doc, frag
assert doc.count('condition - if') == 9 and sum(1 for ln in doc.split('\n') if ln[:3] in ('10.', '11.', '12.', '13.', '14.', '15.')) == 6

print('test_colour_rules ok')
