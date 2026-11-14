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
def apply(rows, views, sign_of_planet, min_fit=0.5, ctx=None, stats=None, ai_atoms=None):
    """stats (optional dict) is filled with a full ledger: every rule is counted, none silently skipped."""
    fired = []; S = {'total': 0, 'unparsed': 0, 'partial': 0, 'parsed': 0, 'needs_date': 0, 'evaluated': 0, 'fired': 0, 'not_fired': 0, 'by_system': {}}
    for r in rows:
        n = N.parse(r['input'], r['system']); S['total'] += 1; S[n['status']] += 1
        if n['status'] != 'parsed' and ai_atoms and r['id'] in ai_atoms:   # validated AI-read atoms (core/atoms_store.py): kept separate by origin
            n = {'status': 'parsed', 'atoms': ai_atoms[r['id']], 'frame': 'aries_fixed' if r['system'] == 'lalkitab' else 'lagna', 'origin': 'ai_v1'}; S['ai_read'] = S.get('ai_read', 0) + 1
        sysd = S['by_system'].setdefault(r['system'], {'total': 0, 'evaluated': 0, 'fired': 0}); sysd['total'] += 1
        if n['status'] != 'parsed': continue
        f = I.fit(n, views, sign_of_planet, ctx)
        if f is None: S['needs_date'] += 1; continue
        S['evaluated'] += 1; sysd['evaluated'] += 1
        if f < min_fit: S['not_fired'] += 1
        if f is not None and f >= min_fit:
            S['fired'] += 1; sysd['fired'] += 1
            fired.append({'id': r['id'], 'system': r['system'], 'engine_role': r['engine_role'], 'life_area': r['life_area'], 'fit': f,
                          'input': r['input'], 'outcome': r['outcome'], 'timing': r['timing'], 'remedy': r['remedy'], 'source': r['source'][:90], 'dasha_linked': any(x[0].startswith('dasha') for x in n['atoms']), 'origin': n.get('origin', 'parser'), 'confidence': r['confidence']})
    if stats is not None: stats.update(S)
    return sorted(fired, key=lambda x: (-x['fit'], x['id']))
