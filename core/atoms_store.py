"""Validator and loader for AI-converted rule atoms (docs/CALCULATION_LEDGER.md step 3). Strict: anything not in the vocabulary is rejected."""
import json, glob
PL = {'Sun': 0, 'Moon': 1, 'Mars': 2, 'Mercury': 3, 'Jupiter': 4, 'Venus': 5, 'Saturn': 6, 'Rahu': 7, 'Ketu': 8}
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
GROUPS = ('kendra', 'trikona', 'dusthana', 'upachaya'); DIG = ('exalted', 'debilitated', 'own', 'friend', 'enemy', 'neutral')
import yogas
NAKN = {n.lower(): i + 1 for i, n in enumerate(['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishta','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati'])}
BEN = ('benefic', 'malefic')
class Bad(Exception): pass
def _p(x, seven=False):
    if x not in PL or (seven and PL[x] > 6): raise Bad(f'planet {x}')
    return PL[x]
def _hs(x):
    if not isinstance(x, list) or not x or any(not isinstance(i, int) or not 1 <= i <= 12 for i in x): raise Bad(f'houses {x}')
    return tuple(sorted(set(x)))
def atom(a, depth=0):
    """JSON atom -> engine atom tuple. Raises Bad."""
    if not isinstance(a, dict) or 't' not in a: raise Bad('not an atom')
    t = a['t']
    if t == 'planet_in_house': return ('planet_in_house', _p(a['p']), _hs(a['h']))
    if t == 'planet_in_sign':
        if a['sign'] not in SIGNS: raise Bad('sign')
        return ('planet_in_sign', _p(a['p']), SIGNS.index(a['sign']))
    if t == 'lord_in_house':
        if not isinstance(a['n'], int) or not 1 <= a['n'] <= 12: raise Bad('n')
        return ('lord_in_house', a['n'], _hs(a['h']))
    if t == 'conj':
        if a['p'] == a['q']: raise Bad('conj self')
        return ('conj', _p(a['p']), _p(a['q']))
    if t == 'planet_in_group':
        if a['g'] not in GROUPS: raise Bad('group')
        return ('planet_in_group', _p(a['p']), a['g'])
    if t == 'dignity':
        if a['s'] not in DIG: raise Bad('dignity')
        return ('dignity', _p(a['p'], True), a['s'])
    if t == 'aspects_house': return ('aspects_house', _p(a['p']), _hs(a['h']))
    if t == 'aspects_planet':
        if a['p'] == a['q']: raise Bad('aspect self')
        return ('aspects_planet', _p(a['p']), _p(a['q']))
    if t == 'dasha':
        if a['level'] not in ('maha', 'antar'): raise Bad('level')
        return ('dasha', _p(a['p']), a['level'])
    if t == 'dasha_house_lord':
        if not isinstance(a['n'], int) or not 1 <= a['n'] <= 12: raise Bad('n')
        return ('dasha_house_lord', a['n'])
    if t == 'planet_from':
        if a['p'] == a['ref']: raise Bad('from self')
        return ('planet_from', _p(a['p']), _p(a['ref']), _hs(a['h']))
    if t == 'planet_in_nak':
        ns = a['nak']
        if not isinstance(ns, list) or not ns: raise Bad('nak')
        out = []
        for n in ns:
            n = NAKN.get(n.lower()) if isinstance(n, str) else n
            if not isinstance(n, int) or not 1 <= n <= 27: raise Bad('nak')
            out.append(n)
        return ('planet_in_nak', _p(a['p']), tuple(sorted(set(out))))
    if t == 'lagna_sign':
        v = a['sign']; v = [v] if isinstance(v, str) else v
        if not isinstance(v, list) or not v or any(x not in SIGNS for x in v): raise Bad('lagna sign')
        return ('lagna_sign', tuple(sorted({SIGNS.index(x) for x in v})))
    if t == 'group_in_house':
        if a['g'] not in BEN: raise Bad('group')
        return ('group_in_house', a['g'], _hs(a['h']))
    if t == 'planet_with_group':
        if a['g'] not in BEN: raise Bad('group')
        return ('planet_with_group', _p(a['p']), a['g'])
    if t in ('planet_aspected_by', 'lord_aspected_by'):
        by = a['by']
        if isinstance(by, str):
            if by not in BEN: raise Bad('by group')
            by = ('group', by)
        else:
            if not isinstance(by, list) or not by: raise Bad('by planets')
            by = ('planets', tuple(sorted({_p(x) for x in by})))
        if t == 'planet_aspected_by':
            if by[0] == 'planets' and _p(a['p']) in by[1] and len(by[1]) == 1: raise Bad('aspect self')
            return (t, _p(a['p']), by)
        if not isinstance(a['n'], int) or not 1 <= a['n'] <= 12: raise Bad('n')
        return (t, a['n'], by)
    if t == 'lord_with_group':
        if a['g'] not in BEN or not isinstance(a['n'], int) or not 1 <= a['n'] <= 12: raise Bad('lord group')
        return ('lord_with_group', a['n'], a['g'])
    if t == 'strength':
        if _p(a['p']) not in (0, 1, 2, 3, 4, 5, 6) or a.get('s') not in ('strong', 'weak'): raise Bad('strength')
        return ('strength', PL[a['p']], a['s'])
    if t == 'retro':
        if _p(a['p']) not in (2, 3, 4, 5, 6): raise Bad('retro planet')
        return ('retro', PL[a['p']])
    if t == 'combust':
        if _p(a['p']) not in (1, 2, 3, 4, 5, 6): raise Bad('combust planet')
        return ('combust', PL[a['p']])
    if t == 'yoga':
        if a['name'] not in yogas.NAMES: raise Bad('yoga name')
        return ('yoga', a['name'])
    if depth >= 2: raise Bad('nesting too deep')
    if t == 'any':
        subs = a['of']
        if not isinstance(subs, list) or len(subs) < 2: raise Bad('any needs 2+')
        return ('any', tuple(atom(x, depth + 1) for x in subs))
    if t == 'not': return ('not', atom(a['of'], depth + 1))
    raise Bad(f'unknown atom {t}')
def entry(e):
    """One JSONL entry -> (id, atoms tuple) if valid and complete, else raises Bad."""
    if not e.get('complete'): raise Bad('incomplete')
    atoms = e.get('atoms')
    if not isinstance(atoms, list) or not atoms: raise Bad('no atoms')
    return e['id'], tuple(atom(a) for a in atoms)
def load(globs):
    """{rule_id: atoms} for all valid complete entries; plus counts. Duplicate ids with different atoms are dropped (disagreement)."""
    out, seen, cnt = {}, {}, {'valid': 0, 'rejected': 0, 'incomplete': 0, 'conflict': 0}
    for g in ([globs] if isinstance(globs, str) else globs):
        for pth in sorted(glob.glob(g)):
            for l in open(pth):
                e = json.loads(l)
                try: i, at = entry(e)
                except Bad as x:
                    cnt['incomplete' if str(x) in ('incomplete', 'no atoms') else 'rejected'] += 1; continue
                except (KeyError, TypeError): cnt['rejected'] += 1; continue
                if i in seen and seen[i] != at: out.pop(i, None); cnt['conflict'] += 1; seen[i] = None; continue
                if seen.get(i, 0) is None: continue
                seen[i] = at; out[i] = at; cnt['valid'] += 1
    return out, cnt
