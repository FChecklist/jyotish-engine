"""Planet-in-sign and planet-aspect negatives with colour remedies (owner table, 21 Nov 2026).
Plain if/then code, no AI. Table: data/planet_sign_negatives.csv. Spec: docs/PLANET_SIGN_NEGATIVES.md. Tradition claim, not a measured fact.

Rule per (planet, rule_group):
- PLACEMENT: the planet sits in a sign listed in negative_signs -> negative; flagged sign = the planet's own sign.
- ASPECT: for each number n in aspect_numbers the planet aspects the sign n-th from its own sign (own sign = 1, so 7th = 6 signs ahead,
  forward count only). If that sign is listed in aspect_target_signs -> negative; flagged sign = the aspected sign.
- REMEDY for each flagged sign: any ONE colour in remedy_colours, OR the whole remedy_combination together (if the owner gave one),
  applied in that zodiac area on every scope in remedy_scopes (body, house, office).
Input signs only (the calculator already gives the chart); nothing is recalculated here."""
import csv
import json
import numbers
import os
from zodiac import SIGNS

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'planet_sign_negatives.csv')
COLUMNS = ['planet', 'rule_group', 'negative_signs', 'aspect_numbers', 'aspect_target_signs',
           'remedy_colours', 'remedy_combination', 'remedy_scopes', 'source', 'notes']
LIST_COLUMNS = ('negative_signs', 'aspect_numbers', 'aspect_target_signs', 'remedy_colours', 'remedy_combination', 'remedy_scopes')
# Owner's alternative names for the outer planets (docs: Indra, Varun, Yum). core/outer.py spells them Indra, Varuna, Yama.
PLANET_ALIASES = {'indra': 'Uranus', 'varun': 'Neptune', 'varuna': 'Neptune', 'yum': 'Pluto', 'yama': 'Pluto'}
ENGINE_IDS = {0: 'Sun', 1: 'Moon', 2: 'Mars', 3: 'Mercury', 4: 'Jupiter', 5: 'Venus', 6: 'Saturn', 7: 'Rahu', 8: 'Ketu'}  # core/charts.py ids


def load_rules(path=None):
    """Read and validate the table. Returns a list of rule dicts (list columns decoded from JSON). Raises ValueError on a bad row."""
    path = path or DATA_PATH
    with open(path, newline='', encoding='utf-8') as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != COLUMNS:
            raise ValueError('planet_sign_negatives columns are %r, expected %r' % (rd.fieldnames, COLUMNS))
        rows = list(rd)
    out, seen = [], set()
    for i, r in enumerate(rows, start=2):  # line 1 is the header
        if None in r or any(r.get(c) is None for c in COLUMNS):  # DictReader: missing cells are None, extra cells go under key None
            raise ValueError('line %d: row must have exactly %d cells' % (i, len(COLUMNS)))
        for c in LIST_COLUMNS:
            r[c] = json.loads(r[c])
        key = (r['planet'], r['rule_group'])
        if key in seen:
            raise ValueError('line %d: duplicate (planet, rule_group) %r' % (i, key))
        seen.add(key)
        if r['planet'] != canonical_planet(r['planet']):
            raise ValueError('line %d: planet %r is not a canonical name' % (i, r['planet']))
        for c in ('negative_signs', 'aspect_target_signs'):
            if not r[c] or any(s not in SIGNS for s in r[c]):
                raise ValueError('line %d: bad %s %r' % (i, c, r[c]))
        if not r['aspect_numbers'] or any((not isinstance(n, int)) or isinstance(n, bool) or n < 2 or n > 12 for n in r['aspect_numbers']):
            raise ValueError('line %d: bad aspect_numbers %r (need ints 2..12; 1 would be the planet\'s own sign)' % (i, r['aspect_numbers']))
        if not r['remedy_colours'] or not r['remedy_scopes']:
            raise ValueError('line %d: remedy_colours and remedy_scopes must not be empty' % i)
        if r['remedy_combination'] and set(r['remedy_combination']) != set(r['remedy_colours']):
            raise ValueError('line %d: remedy_combination must use exactly the listed colours' % i)
        out.append(r)
    return out


def canonical_planet(name):
    if not isinstance(name, str):
        raise ValueError('planet name must be text, got %r' % (name,))
    k = name.strip().lower()
    if k in PLANET_ALIASES:
        return PLANET_ALIASES[k]
    return k.capitalize()


def sign_index(sign):
    """Sign name (any case) or whole-number index 0..11 (0 = Aries) -> int index. Anything else raises ValueError."""
    if isinstance(sign, bool):
        raise ValueError('bad sign %r' % (sign,))
    if isinstance(sign, numbers.Integral):  # plain int and numpy integers
        if 0 <= sign <= 11:
            return int(sign)
        raise ValueError('sign index %r outside 0..11' % (sign,))
    if isinstance(sign, str):
        k = sign.strip().capitalize()
        if k in SIGNS:
            return SIGNS.index(k)
    raise ValueError('unknown sign %r' % (sign,))


def aspected_sign(sign0, n):
    """Sign index aspected with the n-th aspect by a planet in sign0 (own sign counted as 1)."""
    return (sign0 + n - 1) % 12


def from_engine_chart(chart):
    """Adapter for core/charts.py output ({0..8: (sign0, deg) or sign0, 'asc': ...}) -> {planet name: sign index}. Skips 'asc'."""
    out = {}
    for k, v in chart.items():
        if k in ENGINE_IDS:
            out[ENGINE_IDS[k]] = v[0] if isinstance(v, (tuple, list)) else v
    return out


def _remedy(rule, flagged_sign):
    singles = [[c] for c in rule['remedy_colours']]
    options = singles + ([list(rule['remedy_combination'])] if rule['remedy_combination'] else [])
    return {'zodiac_area': flagged_sign, 'single_colours': list(rule['remedy_colours']), 'combination': list(rule['remedy_combination']),
            'options': options, 'by_scope': {s: [list(o) for o in options] for s in rule['remedy_scopes']},
            'rule': 'use any one option; the colour goes in the zodiac area of ' + flagged_sign + ' on ' + ', '.join(rule['remedy_scopes'])}


def evaluate(chart, rules=None, ignore_unknown=False):
    """chart: {planet name: sign} (sign = name or index 0..11). Planet names may be Indra/Varun/Varuna/Yum/Yama aliases.
    Planets with no rule in the table (e.g. 'Lagna') raise ValueError unless ignore_unknown=True.
    Returns {'planets': {planet: {'sign', 'negative', 'flags'}}, 'negative_planets': [...], 'by_sign': {sign: [flag, ...]}, 'flags': [...]}.
    Each flag: planet, rule_group, kind ('placement' | 'aspect'), aspect_number (None for placement), from_sign, flagged_sign, remedy, source."""
    rules = load_rules() if rules is None else rules
    known = {r['planet'] for r in rules}
    signs = {}
    for k, v in chart.items():
        p = canonical_planet(k)
        if p not in known:
            if ignore_unknown:
                continue
            raise ValueError('no rule for planet %r' % (k,))
        if p in signs:
            raise ValueError('planet %r given twice (aliases count as the same planet)' % p)
        signs[p] = sign_index(v)
    res = {'planets': {}, 'negative_planets': [], 'by_sign': {}, 'flags': []}
    for p, s0 in signs.items():
        flags = []
        for r in rules:
            if r['planet'] != p:
                continue
            base = {'planet': p, 'rule_group': r['rule_group'], 'from_sign': SIGNS[s0], 'source': r['source']}
            if SIGNS[s0] in r['negative_signs']:
                flags.append(dict(base, kind='placement', aspect_number=None, flagged_sign=SIGNS[s0], remedy=_remedy(r, SIGNS[s0])))
            for n in r['aspect_numbers']:
                t = SIGNS[aspected_sign(s0, n)]
                if t in r['aspect_target_signs']:
                    flags.append(dict(base, kind='aspect', aspect_number=n, flagged_sign=t, remedy=_remedy(r, t)))
        res['planets'][p] = {'sign': SIGNS[s0], 'negative': bool(flags), 'flags': flags}
        if flags:
            res['negative_planets'].append(p)
        for fl in flags:
            res['flags'].append(fl)
            res['by_sign'].setdefault(fl['flagged_sign'], []).append(fl)
    return res
