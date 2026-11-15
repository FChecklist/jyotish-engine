"""Extract nakshatra age statements from the paraphrased book rules (nakshatra_books_v1.jsonl) into nakshatra_ages_v1.jsonl.
Usage: python make_nak_ages.py RULES.jsonl OUT.jsonl. A rule is kept only if it names exactly one nakshatra and has an age number. Kind is a keyword guess (labelled); the text is kept as evidence."""
import sys, json, re, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import nakshatra as K
ALIAS = {'moola': 'Mula', 'jyestha': 'Jyeshtha', 'jyeshta': 'Jyeshtha', 'satabhisha': 'Shatabhisha', 'shatabisha': 'Shatabhisha', 'mrigasira': 'Mrigashira', 'aslesha': 'Ashlesha', 'sravana': 'Shravana', 'dhanista': 'Dhanishta', 'visakha': 'Vishakha', 'kritika': 'Krittika', 'ashvini': 'Ashwini', 'aswini': 'Ashwini', 'p. phalguni': 'Purva Phalguni', 'u. phalguni': 'Uttara Phalguni'}
names = sorted(set([n for n in K.NAMES] + [a for a in ALIAS]), key=lambda s: -len(s))
AGE = re.compile(r'(?:until|till|before|after|upto|up to)\s+(?:about |around |the age of |age )?(\d{1,2})|(?:ages?|age of)\s+(\d{1,2})(?:\s*(?:to|and|-|–)\s*(\d{1,2}))?|between\s+(\d{1,2})\s*(?:and|to|-)\s*(\d{1,2})|from\s+(\d{1,2})\s+to\s+(\d{1,2})|(\d{1,2})(?:st|nd|rd|th)\s+year', re.I)
KIND = [('golden', r'golden|best period|prosper|success|peak|rise'), ('struggle', r'struggle|trouble|difficult|hardship|suffer|obstacle|instab'), ('marriage', r'marri|spouse|wife|husband'), ('career', r'job|career|profession|business|promotion|status|power'), ('health', r'health|disease|illness|surgery|danger|accident'), ('children', r'child|son|daughter')]
out = []; seen = 0
for l in open(sys.argv[1]):
    r = json.loads(l); t = r['input'] + ' ' + r['outcome']
    if re.search(r'ratti|gemstone|mantra|finger|metal', t, re.I): continue
    found = set()
    for n in names:
        if re.search(r'\b' + re.escape(n) + r'\b', t, re.I): found.add(ALIAS.get(n.lower(), n if n in K.NAMES else n.title()))
    found = {f for f in found if f in K.NAMES}
    # overlap guard: Purva/Uttara forms contain no plain names, but 'Phalguni' alone is ignored
    ages = [int(x) for m in AGE.finditer(t) for x in m.groups() if x]
    if len(found) != 1 or not ages or any(a < 1 or a > 100 for a in ages): continue
    kinds = [k for k, p in KIND if re.search(p, t, re.I)] or ['other']
    out.append({'id': r['id'], 'nakshatra': found.pop(), 'ages': ages, 'kinds': kinds, 'text': r['input'] + ((': ' + r['outcome']) if r['outcome'] else ''), 'source': r['source'], 'confidence': 'book-claim (paraphrase); kind is a keyword guess'})
with open(sys.argv[2], 'w') as f:
    for o in out: f.write(json.dumps(o) + '\n')
print(len(out), 'age rules; nakshatras covered', len({o['nakshatra'] for o in out}), 'of 27')
