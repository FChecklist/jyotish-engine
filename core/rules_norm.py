"""Rule normaliser v1: turns the free-text `input` of a rule into checkable atoms.
Atoms (all positions in D1; house = whole-sign from Lagna unless frame says otherwise):
  ('planet_in_house', P, (h,...))    ('planet_in_sign', P, sign0)     ('lord_in_house', n, (h,...))
  ('conj', P, Q)                     ('planet_in_kendra'|'trikona'|'dusthana'|'upachaya', P)
Status: 'parsed' = every word of the input is explained by atoms; 'partial' = some atoms but leftover words (qualifiers such as 'weak',
'aspected by', 'if ...'), NOT evaluated; 'unparsed' = nothing recognised. Unparsed/partial rules stay in the database, untouched.
Frame: 'lagna' by default; 'aries_fixed' for Lal Kitab rules (houses numbered from Aries) -- see docs/DECISIONS.md."""
import re
import dignity
PL = {'sun': 0, 'moon': 1, 'mars': 2, 'mercury': 3, 'jupiter': 4, 'venus': 5, 'saturn': 6, 'rahu': 7, 'ketu': 8}
SIGNS = ['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces']
P = '(sun|moon|mars|mercury|jupiter|venus|saturn|rahu|ketu)'
H = r'(\d{1,2})(?:st|nd|rd|th)?'
GROUPS = {'kendra': (1, 4, 7, 10), 'trikona': (1, 5, 9), 'dusthana': (6, 8, 12), 'upachaya': (3, 6, 10, 11)}
CLAUSES = [
    (re.compile(rf'\b{P} (?:is |are )?(?:placed )?in (?:the )?(?:house |bhava )?{H}(?: house| bhava)?(?:(?:,| or |/)\s*{H})*\b', re.I), 'planet_in_house'),
    (re.compile(rf'\b{P} (?:is |are )?in (?:the )?(?:house )?{H}(?: house)? from lagna\b', re.I), 'planet_in_house'),
    (re.compile(rf'\b{P} (?:is |are )?in (aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces)\b', re.I), 'planet_in_sign'),
    (re.compile(rf'\b{H} lord (?:is |are )?(?:placed )?in (?:the )?{H}(?: house)?(?:(?:,| or |/)\s*{H})*\b', re.I), 'lord_in_house'),
    (re.compile(rf'\b{P} (?:and|with|conjunct(?:ed)?(?: with)?) {P}\b', re.I), 'conj'),
    (re.compile(rf'\b{P} in (kendra|trikona|dusthana|upachaya)s?\b', re.I), 'planet_in_group'),
]
_DIG = {'exalted': 'exalted', 'exaltation': 'exalted', 'uchcha': 'exalted', 'debilitated': 'debilitated', 'debilitation': 'debilitated', 'neecha': 'debilitated',
        'own': 'own', 'swakshetra': 'own', 'friend': 'friend', 'enemy': 'enemy', 'neutral': 'neutral'}
CLAUSES += [
    (re.compile(rf"\b(sun|moon|mars|mercury|jupiter|venus|saturn) (?:is |are )?(?:in |placed in )?(?:its |his |her |an |a |the )*(exalted|exaltation|debilitated|debilitation|own sign|own house|friend(?:ly|s|'s)? (?:sign|house)|enemy(?:'s)? (?:sign|house)|neutral sign|swakshetra|neecha|uchcha)\b", re.I), 'dignity'),
    (re.compile(rf'\b{P} (?:aspects|aspecting|casts (?:its )?(?:drishti|aspect) (?:on|to)) (?:the )?{H}(?: house)?(?:(?:,| or |/)\s*{H})*\b', re.I), 'aspects_house'),
    (re.compile(rf'\b{P} (?:aspects|aspecting) (?:the )?{P}\b', re.I), 'aspects_planet'),
    (re.compile(rf'\b{P} (?:is |are )?aspected by {P}\b', re.I), 'aspected_by'),
]
FILLER = set('lal kitab the a an in is are of and or with house houses from lagna bhava placed to'.split())

def parse(text, system=''):
    t = text.strip(); rest = t; atoms = []
    for rx, kind in CLAUSES:
        for m in list(rx.finditer(rest)):
            g = m.groups()
            if kind == 'planet_in_house':
                hs = tuple(int(x) for x in re.findall(r'\d{1,2}', m.group(0)) if 1 <= int(x) <= 12)
                if hs: atoms.append(('planet_in_house', PL[g[0].lower()], hs))
            elif kind == 'planet_in_sign': atoms.append(('planet_in_sign', PL[g[0].lower()], SIGNS.index(g[1].lower())))
            elif kind == 'lord_in_house':
                nums = [int(x) for x in re.findall(r'\d{1,2}', m.group(0)) if 1 <= int(x) <= 12]
                if len(nums) >= 2: atoms.append(('lord_in_house', nums[0], tuple(nums[1:])))
            elif kind == 'dignity':
                key = re.split(r"[ ']", g[1].lower())[0]
                if PL[g[0].lower()] <= 6 and key in _DIG: atoms.append(('dignity', PL[g[0].lower()], _DIG[key]))
                else: continue            # Rahu/Ketu: schools differ, no atom; the words stay as leftover so the rule is partial
            elif kind == 'aspects_house':
                hs = tuple(int(x) for x in re.findall(r'\d{1,2}', m.group(0)) if 1 <= int(x) <= 12)
                if hs: atoms.append(('aspects_house', PL[g[0].lower()], hs))
            elif kind == 'aspects_planet': atoms.append(('aspects_planet', PL[g[0].lower()], PL[g[1].lower()]))
            elif kind == 'aspected_by': atoms.append(('aspects_planet', PL[g[1].lower()], PL[g[0].lower()]))
            elif kind == 'conj': atoms.append(('conj', PL[g[0].lower()], PL[g[1].lower()]))
            elif kind == 'planet_in_group': atoms.append(('planet_in_group', PL[g[0].lower()], g[1].lower()))
        rest = rx.sub(' ', rest)
    words = [w for w in re.findall(r"[a-z']+", rest.lower()) if w not in FILLER]
    alt = len(atoms) > 1 and re.search(r'\s/\s|\bor\b|\beither\b|\bany\b|\bif\b|\bnot\b|\bunless\b', t, re.I)
    if alt: words = words + ['<alternation-or-condition>']
    status = 'unparsed' if not atoms else ('parsed' if not words else 'partial')
    return {'status': status, 'atoms': atoms, 'leftover': words[:8], 'frame': 'aries_fixed' if system == 'lalkitab' else 'lagna'}

def house_of(sign0, lagna0, frame='lagna'):
    return (sign0 - (0 if frame == 'aries_fixed' else lagna0)) % 12 + 1

def evaluate(norm, chart):
    """chart = {'asc': sign0, 'signs': {planet_id: sign0}}. Returns True/False for parsed rules, None if not evaluable."""
    if norm['status'] != 'parsed': return None
    fr = norm['frame']; lag = chart['asc']; sg = chart['signs']
    SIGN_LORD = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]
    ok = True
    for a in norm['atoms']:
        if a[0] == 'planet_in_house': ok &= house_of(sg[a[1]], lag, fr) in a[2]
        elif a[0] == 'planet_in_sign': ok &= sg[a[1]] == a[2]
        elif a[0] == 'lord_in_house':
            sign_n = (lag + a[1] - 1) % 12 if fr != 'aries_fixed' else a[1] - 1
            ok &= house_of(sg[SIGN_LORD[sign_n]], lag, fr) in a[2]
        elif a[0] == 'conj': ok &= sg[a[1]] == sg[a[2]]
        elif a[0] == 'dignity': ok &= a[2] in dignity.states(a[1], sg[a[1]])
        elif a[0] == 'aspects_house': ok &= bool(dignity.aspects_house(a[1], house_of(sg[a[1]], lag, fr)) & set(a[2]))
        elif a[0] == 'aspects_planet': ok &= dignity.aspects_planet(a[1], house_of(sg[a[1]], lag, fr), house_of(sg[a[2]], lag, fr))
        elif a[0] == 'planet_in_group': ok &= house_of(sg[a[1]], lag, fr) in GROUPS[a[2]]
    return bool(ok)
