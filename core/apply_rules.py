"""Apply normalised rules to a chart (Step 1 of the report). Reads rule JSONL files, parses them (core/rules_norm),
computes the weighted fit (core/influence) and returns fired rules grouped by engine role. Everything returned is a TRADITION CLAIM
with its source; no probability is attached (calibration none)."""
import glob, json
import rules_norm as N, influence as I
def _norm_row(r):
    """Books rows already have the shape. Gautam transcript rows (system 'gautam') lack some fields: fill defaults."""
    r.setdefault('engine_role', 'remedy' if r.get('remedy') else 'rule'); r.setdefault('life_area', r.get('category', ''))
    r.setdefault('timing', ''); r.setdefault('remedy', ''); r.setdefault('confidence', ''); r.setdefault('outcome', '')
    r.setdefault('source', r.get('source_file', '') + ' ' + str(r.get('timestamp', '')))
    return r
def load(paths):
    """paths: one glob or a list of globs (books rules, Gautam transcript rules)."""
    rows = []
    for g in ([paths] if isinstance(paths, str) else paths):
        for pth in sorted(glob.glob(g)):
            rows += [_norm_row(json.loads(l)) for l in open(pth)]
    return rows
def apply(rows, views, sign_of_planet, min_fit=0.5):
    fired = []
    for r in rows:
        n = N.parse(r['input'], r['system'])
        if n['status'] != 'parsed': continue
        f = I.fit(n, views, sign_of_planet)
        if f is not None and f >= min_fit:
            fired.append({'id': r['id'], 'system': r['system'], 'engine_role': r['engine_role'], 'life_area': r['life_area'], 'fit': f,
                          'input': r['input'], 'outcome': r['outcome'], 'timing': r['timing'], 'remedy': r['remedy'], 'source': r['source'][:90], 'confidence': r['confidence']})
    return sorted(fired, key=lambda x: (-x['fit'], x['id']))
