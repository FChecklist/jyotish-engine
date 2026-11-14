"""Guidance view: ONLY do / don't / precautions, from a Step-1 report. Plain code, no AI.
Umbrella idea: say what to carry and avoid in the current window. Probability stays null until calibrated on measured cases.
Mapping (hypothesis, v1): remedy rules -> DO; donot rules -> DON'T; event rules with a harmful outcome -> PRECAUTION.
No death dates, no medical diagnosis, no investment advice: such items are dropped, not shown."""
import datetime
NEG = ('loss', 'death', 'disease', 'illness', 'accident', 'danger', 'poor', 'quarrel', 'separat', 'sorrow', 'grief', 'theft', 'debt', 'trouble', 'failure', 'injur', 'obstacle', 'litigation', 'cheat')
POS = ('destroy', 'fearless', 'good', 'wealthy', 'rich', 'happy', 'famous', 'king', 'victor', 'success', 'gain', 'learned', 'excellent', 'prosper')
BLOCK = ('death', 'die', 'dies', 'cancer', 'tumour', 'tumor', 'disease', 'diabetes', 'heart', 'invest', 'shares', 'stock', 'speculat', 'lottery')
def _now_window(report, asof):
    rows = report['timing']['vimshottari']; cur = None
    for r in rows:
        if datetime.datetime(*[int(x) for x in r['start_local'][:3]]) <= asof: cur = r
        else: break
    return cur
def _blocked(f): return any(w in (f['outcome'] + ' ' + f['input'] + ' ' + f['remedy']).lower() for w in BLOCK)
def _item(f, window):
    return {'text': f['remedy'] or f['outcome'], 'basis': f['input'], 'rule_id': f['id'], 'system': f['system'], 'source': f['source'], 'fit': round(f['fit'], 3),
            'window': window, 'label': 'tradition claim', 'probability': None, 'calibration': 'none'}
def guidance(report, asof):
    cur = _now_window(report, asof)
    window = {'type': 'current vimshottari antardasha (not yet linked to the rule; natal rule + running period shown together)',
              'maha': cur['maha'] if cur else None, 'antar': cur['antar'] if cur else None, 'starts': cur['start_local'][:3] if cur else None}
    out = {'asof': asof.date().isoformat(), 'window': window, 'dos': [], 'donts': [], 'precautions': [], 'dropped_by_safety_filter': 0,
           'status': 'built_unvalidated', 'note': 'Tradition claims. No probability: none measured yet. Not medical, legal or investment advice.'}
    for f in report['remedies']['items']:
        if _blocked(f): out['dropped_by_safety_filter'] += 1; continue
        if f['remedy'] or f['outcome']: out['dos'].append(_item(f, window))
    for f in report['donts']['items']:
        if _blocked(f): out['dropped_by_safety_filter'] += 1; continue
        out['donts'].append(_item(f, window))
    for f in report['events']['items']:
        t = f['outcome'].lower()
        neg = sum(w in t for w in NEG); pos = sum(w in t for w in POS)
        if neg > pos:   # v1 word count; hypothesis, not validated
            if _blocked(f): out['dropped_by_safety_filter'] += 1; continue
            it = _item(f, window); it['text'] = 'Watch for: ' + f['outcome']; out['precautions'].append(it)
    for k in ('dos', 'donts', 'precautions'): out[k].sort(key=lambda x: -x['fit'])
    return out
