"""Unified rule table. Loads Gautam, Parashari/KP/Jaimini/K.N.Rao/Lal Kitab modules and the book rules into ONE schema.
Weights are source-strength LABELS (how well the source is documented), not measured accuracy. Backtest decides later."""
import json, glob, re, os
BASE = os.environ.get('ASTRO_DB', '/home/claude/astro/db')

AREA_KW = [  # first match wins; order matters
 ('marriage', r'marri|spouse|wife|husband|wedd|betroth|conjugal|widow|divorce|love affair|\bmate\b|co-wife|2nd wife'),
 ('children', r'\bson\b|sons\b|child|progeny|issue\b|offspring|barren|pregnan|daughter|abortion|\bno sons'),
 ('education', r'educat|learn|scholar|knowledge|study|studies|intellig|exam|degree|teacher|wisdom|eloquen'),
 ('foreign', r'foreign|abroad|travel|journey|migrat|settle(?:s|d)? away|distant land|another country'),
 ('property', r'propert|\bland\b|building|vehicle|conveyance|estate|home\b|residence|fields|cattle|agricultur'),
 ('career', r'career|profession|job\b|employ|business|trade|occupation|livelihood|promotion|boss'),
 ('wealth', r'wealth|rich|money|income|gain|poor|poverty|finance|debt|prosper|riches|fortune|treasure|loss of wealth'),
 ('status', r'fame|famous|honou?r|king|ruler|raja|rank|power|authority|govern|minister|reputation|status|renown|leader|rises?'),
 ('health', r'health|disease|illness|sick|body|ailment|eye|disorder|pain|surgery|fever|wound|weak\b|longevity|accident|injur'),
 ('setback', r'death|die[sd]?\b|loss|danger|enem|litigat|imprison|obstacle|misery|grief|sorrow|ruin|fail|calamit|separation|quarrel|trouble|delay|fear|theft|thief'),
]
POS = r'wealth|rich|happy|happiness|success|gain|fame|famous|king|good|benefit|prosper|honou?r|learned|comfort|victor|raja|fortunate|long life|lucky|wise|beautiful|virtuous|respected|powerful|auspicious|blessed|enjoy|increase|rise|support|get(?:s)? (?:married|children|job)|many sons|fortune'
NEG = r'poor|poverty|loss|lose|death|die|disease|sorrow|enem|danger|fail|trouble|misery|quarrel|separat|obstacle|delay|accident|debt|grief|imprison|illness|injur|no sons|barren|widow|ruin|fear|theft|anxiet|unhappy|disgrace|humiliat|sickness|suffer|difficult|hurdle|break|hardship|worry|wound|dispute|legal'

def area_of(text, hint=''):
    t = (text + ' ' + hint).lower()
    if hint in ('career','marriage','children','property','education','foreign','health','status','wealth','setback'): return hint
    for a, kw in AREA_KW:
        if re.search(kw, t): return a
    return 'general'

def polarity(text):
    t = text.lower(); p = len(re.findall(POS, t)); n = len(re.findall(NEG, t))
    return (p > n) - (p < n)

def _load(path):
    for l in open(path, encoding='utf-8'):
        l = l.strip()
        if l:
            try: yield json.loads(l)
            except Exception: pass

W = dict(classical=1.0, textual=0.9, gautam=0.7, lalkitab=0.7, commentary=0.6, jaimini=0.5, kp=0.5, notes=0.5, knrao=0.3)

def load_all(include=None):
    R = []
    def add(**k):
        k.setdefault('remedy', ''); k.setdefault('timing', ''); k.setdefault('src', '')
        k['area'] = area_of(k.get('outcome', ''), k.get('hint', ''))
        k['pol'] = polarity(k.get('outcome', ''))
        R.append(k)
    # 1. books v2
    f = BASE + '/books_master_v8.jsonl'
    for r in _load(f):
        sysn = r.get('system', 'other'); src = r.get('source', '')
        cls = 'classical' if re.search(r'Brihat Jataka|Phaladeepika|Saravali|Parijata|Uttara|Jaimini|Prasna', src, re.I) else 'notes'
        add(id=r['id'], family='book', system=sysn, role=r.get('engine_role', 'event'), input=r.get('input', ''), outcome=r.get('outcome', ''),
            remedy=r.get('remedy', ''), timing=r.get('timing', ''), hint=r.get('life_area', ''), src=src, w=W[cls])
    # 2. Gautam
    for r in _load(BASE + '/gautam_final_v2.jsonl'):
        if r.get('status') == 'flagged_unreliable': continue
        out = (r.get('outcome') or r.get('interpretation') or '').strip()
        role = 'remedy' if r.get('remedy') else ('do_dont' if r.get('category') in ('avoid', 'prohibition') else 'event')
        add(id=r.get('rid') or r['id'], family='gautam', system='gautam', role=role, input=r.get('input', ''), outcome=out, remedy=r.get('remedy', ''),
            src='Brajesh Gautam ' + str(r.get('source_file', '')), w=W['gautam'], hint='')
    # 3. SRC modules
    for fn in sorted(glob.glob(BASE + '/raw/SRC_*.jsonl')):
        for r in _load(fn):
            s = r.get('system', ''); cat = r.get('category', '')
            conf = r.get('confidence', '')
            w = W['lalkitab'] if s == 'lalkitab' else W['jaimini'] if s == 'jaimini' else W['kp'] if s == 'kp' else W['knrao'] if s == 'knrao' else (W['textual'] if conf == 'textual' else W['commentary'])
            out = (r.get('outcome') or r.get('interpretation') or '').strip()
            role = 'remedy' if (r.get('remedy') and cat in ('upay',)) else 'do_dont' if cat in ('avoid',) else 'event'
            add(id=r['id'], family='src', system=s, role=role, input=r.get('input', ''), outcome=out, remedy=r.get('remedy', '') if cat in ('upay', 'avoid') else '',
                src=r.get('source', ''), w=w, hint='')
    return R
