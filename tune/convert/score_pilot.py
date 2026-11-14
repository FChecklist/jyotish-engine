"""Score the AI conversion pilot. GOLD: exact match with the parser's atoms. HARD: agreement between two independent passes (A, B).
Usage: python score_pilot.py PILOT_DIR"""
import sys, os, json, glob, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
import atoms_store as S
def canon(a):
    k = a[0]
    if k == 'conj': return ('conj',) + tuple(sorted((a[1], a[2])))
    if k in ('planet_in_house', 'aspects_house', 'lord_in_house'): return (k, a[1], tuple(sorted(set(a[2]))))
    if k == 'any': return ('any', frozenset(canon(x) for x in a[1]))
    if k == 'not': return ('not', canon(a[1]))
    return tuple(a)
def listify(a):   # parser atoms saved through JSON: lists -> tuples again
    return tuple(tuple(x) if isinstance(x, list) else x for x in a)
def read(path):
    return [json.loads(l) for l in open(path)] if os.path.exists(path) else []
def ai(e):
    try: return frozenset(canon(a) for a in S.entry(e)[1])
    except (S.Bad, KeyError, TypeError): return None
def run(d):
    gold = json.load(open(f'{d}/gold_answers.json')); res = {'gold': {'n': len(gold), 'exact': 0, 'wrong_complete': 0, 'incomplete': 0, 'invalid': 0, 'missing_line': 0}, 'hard': {}}
    outs = {}
    for p in glob.glob(f'{d}/gold_*.outA.jsonl'):
        for e in read(p): outs[e['id']] = e
    wrong = []
    for i, ans in gold.items():
        e = outs.get(i)
        if e is None: res['gold']['missing_line'] += 1; continue
        if not e.get('complete'): res['gold']['incomplete'] += 1; continue
        a = ai(e)
        if a is None: res['gold']['invalid'] += 1; continue
        want = frozenset(canon(listify(x)) for x in ans['atoms'])
        if a == want: res['gold']['exact'] += 1
        else: res['gold']['wrong_complete'] += 1; wrong.append((i, sorted(map(str, a)), sorted(map(str, want))))
    g = res['gold']; done = g['exact'] + g['wrong_complete']
    g['precision_when_complete'] = round(g['exact'] / done, 3) if done else None; g['recall'] = round(g['exact'] / g['n'], 3)
    A = {}; B = {}
    for p in glob.glob(f'{d}/hard_*.outA.jsonl'):
        for e in read(p): A[e['id']] = e
    for p in glob.glob(f'{d}/hard_*.outB.jsonl'):
        for e in read(p): B[e['id']] = e
    h = {'n': len(set(A) | set(B)), 'both_complete_same': 0, 'both_complete_different': 0, 'one_complete_only': 0, 'both_incomplete': 0, 'invalid_any': 0}; agreed = []
    for i in set(A) & set(B):
        a, b = ai(A[i]), ai(B[i]); ca, cb = bool(A[i].get('complete')), bool(B[i].get('complete'))
        if (ca and a is None) or (cb and b is None): h['invalid_any'] += 1
        elif ca and cb: (agreed.append((i, a)) if a == b else None); h['both_complete_same' if a == b else 'both_complete_different'] += 1
        elif ca or cb: h['one_complete_only'] += 1
        else: h['both_incomplete'] += 1
    comp = h['both_complete_same'] + h['both_complete_different'] + h['one_complete_only']
    h['agreement_among_rules_either_called_complete'] = round(h['both_complete_same'] / comp, 3) if comp else None
    res['hard'] = h; res['wrong_gold_examples'] = wrong[:12]; res['agreed_ids'] = [i for i, _ in agreed]
    return res
if __name__ == '__main__':
    r = run(sys.argv[1]); print(json.dumps({k: v for k, v in r.items() if k != 'agreed_ids'}, indent=1, default=str))
