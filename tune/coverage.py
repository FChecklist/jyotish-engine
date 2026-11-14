"""Calculation ledger: classify EVERY rule (books DB + Gautam transcripts) by the calculation it needs, and say what the engine does with it.
Counts only; no personal data. Usage: python coverage.py OUT.json RULEGLOB [RULEGLOB ...]"""
import sys, os, re, json, glob, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import apply_rules, rules_norm as N
KINDS = [  # (kind, regex on input+outcome+timing, engine status, module or note)
 ('transit',        r'transit|gochar|ingress|sankranti|transiting|moves? into|enters', 'partial', 'core/gochara.py (BK13 gochara rules only); free-text transit rules not parsed'),
 ('dasha',          r'dasha|dasa|bhukti|antar|mahadasha|vimshottari|yogini|chara dasha|narayana', 'partial', 'vimshottari dates only; no rule-to-period linking; no other dashas'),
 ('ashtakavarga',   r'ashtakavarga|ashtakvarga|bindu|bhinna|sarva|sarvashtak|prastara', 'partial', 'core/ashtakavarga.py (tables); bindu rules only in gochara'),
 ('divisional',     r'navamsa|navamsha|d-?9\b|dashamsa|dasamsa|saptamsa|varga|amsa|vargottama|d-?\d{1,2}\b', 'partial', 'core/charts.py computes D1-D60; rules on them not applied'),
 ('aspect',         r'aspect|drishti|drishti|sees|aspected|aspecting', 'partial', 'aspect atoms in rules_norm (whole-house drishti, per house view); many phrasings and conditions unread'),
 ('dignity',        r'exalt|debilit|own sign|moolatrikona|mooltrikona|friend|enemy|neecha|uchcha|swakshetra|combust|retrograde|vakri|vargottam', 'partial', 'dignity atom (sign-based, 7 planets); nodes, degrees, retro and combust not built'),
 ('conjunction',    r'conjunct|conjoin|together with|with (?:sun|moon|mars|mercury|jupiter|venus|saturn|rahu|ketu)|yuti|association', 'partial', 'conj atom (two planets in one sign)'),
 ('placement',      r'\bin (?:the )?(?:\d+(?:st|nd|rd|th)|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth) house|\bin (?:aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces)\b|lord of', 'built', 'rules_norm + influence.fit (weighted)'),
 ('panchang',       r'tithi|nakshatra|vara\b|weekday|karana|panchang|tarabala|chandrabala|muhurta|rahu ?kal|choghadiya|hora\b', 'partial', 'core/panchang.py + daily.py (Tara, Chandra, tithi, nak class, yoga, Bhadra, Rahu Kaal, Abhijit); rest not built'),
 ('yoga_named',     r'\byoga\b|raja yoga|dhana|gajakesari|neechabhanga|viparita|kemadruma|pancha ?mahapurusha|ruchaka|bhadra|hamsa|malavya|sasa|budhaditya|chandra.?mangal', 'not_built', 'no named-yoga detector'),
 ('jaimini',        r'karaka|atmakaraka|amatya|arudha|upapada|karakamsha|chara|jaimini|pada\b|argala|rashi drishti', 'not_built', 'no Jaimini engine (karakas, arudha, argala)'),
 ('kp',             r'sub.?lord|star.?lord|cuspal|kp\b|krishnamurti|significator|ruling planet', 'partial', 'core/kp.py lords; significators and cusp rules not built'),
 ('strength',       r'shadbala|bhava bala|ishta|kashta|strong|weak|strength|avastha|baladi|jagradadi', 'not_built', 'no shadbala or avastha'),
 ('annual_tajika',  r'varshaphal|muntha|tajika|annual|solar return|saham|sahams|varsha', 'not_built', 'no annual chart engine'),
 ('lalkitab_state', r'blind|sleeping|dharmi|pakka|kayam|rin|debt of|masnui|rashi phal|teva|andhe|soya|khana', 'not_built', 'Lal Kitab states and debts not built'),
 ('nodes_eclipse',  r'eclipse|kala sarpa|kaal sarp|pitra dosh|mangal dosh|manglik|kuja dosha|sade ?sati|dhaiya|panoti', 'not_built', 'no dosha detectors, no Sade Sati helper'),
 ('upagraha_other', r'gulika|mandi|maandi|upagraha|yamaghanta|kaala|mrityu|gandanta|pushkara|sarvatobhadra|kota chakra', 'not_built', 'no upagraha or special-degree engine'),
]
def classify(r):
    t = (r.get('input', '') + ' ' + r.get('outcome', '') + ' ' + r.get('timing', '')).lower(); got = [k for k, rx, *_ in KINDS if re.search(rx, t)]
    return got or ['other_text']
def run(globs, out):
    rows = apply_rules.load(globs); cnt = collections.Counter(); sysc = collections.Counter(); only = collections.Counter(); parsed = collections.Counter()
    for r in rows:
        ks = classify(r); sysc[r['system']] += 1
        for k in ks: cnt[k] += 1
        if len(ks) == 1: only[ks[0]] += 1
        parsed[N.parse(r['input'], r['system'])['status']] += 1
    res = {'total_rules': len(rows), 'by_system_top': sysc.most_common(8), 'parser_status': dict(parsed), 'kinds': {}}
    for k, rx, st, note in KINDS: res['kinds'][k] = {'rules_touching': cnt[k], 'only_this_kind': only[k], 'engine_status': st, 'engine_note': note}
    res['kinds']['other_text'] = {'rules_touching': cnt['other_text'], 'only_this_kind': only['other_text'], 'engine_status': 'not_built', 'engine_note': 'free text; needs reading, not keyword'}
    json.dump(res, open(out, 'w'), indent=1); return res
if __name__ == '__main__':
    r = run(sys.argv[2:], sys.argv[1]); print(json.dumps(r, indent=1))
