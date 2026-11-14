"""Fine-tuning with honest validation.
Protocol (fixed before running):
 - parameters: 9 non-negative weights (5 techniques + 4 rule groups), normalised to sum 1
 - objective: mean percentile of the event date among the person's own life windows (50 = chance)
 - search: random Dirichlet samples + local refinement, on TRAIN people only
 - validation: K-fold cross-validation BY PERSON (a person is never in train and test together), repeated with several seeds
 - the number to believe is the OUT-OF-FOLD mean percentile, with a bootstrap interval over people
 - baseline a-priori weights are the v1 technique weights (rules weight 0)"""
import sys, json, random
sys.path.insert(0, '/home/claude/astro/tune')
import numpy as np
from features import *
W0 = np.array([.30, .25, .30, .075, .075, 0, 0, 0, 0])

def fit(train, n=1500, seed=0):
    rng = np.random.default_rng(seed)
    best, bs = W0.copy(), mean_pct(train, W0)
    cands = [rng.dirichlet(np.ones(len(FEATS)) * a) for a in (0.3, 1.0) for _ in range(n // 2)]
    for w in cands:
        s = mean_pct(train, w)
        if s > bs: best, bs = w, s
    step = 0.15
    for it in range(400):                         # local refinement
        w = np.clip(best + rng.normal(0, step, len(FEATS)), 0, None)
        if w.sum() == 0: continue
        w /= w.sum(); s = mean_pct(train, w)
        if s > bs: best, bs = w, s
        if it % 100 == 99: step *= 0.5
    return best, bs

def cv(people, k=5, seeds=(0, 1, 2)):
    res = []; oof = {s: [] for s in seeds}; base = []
    for s in seeds:
        idx = list(range(len(people))); random.Random(s).shuffle(idx)
        folds = [idx[i::k] for i in range(k)]
        for f in range(k):
            te = [people[i] for i in folds[f]]; tr = [people[i] for i in idx if i not in folds[f]]
            w, ins = fit(tr, seed=s * 10 + f)
            oof[s] += [(p['name'], x[1], x[2]) for p in te for x in [(None,) + t[1:] for t in evaluate([p], w)]]
            res.append((s, f, ins, mean_pct(te, w), mean_pct(te, W0), w))
    return res, oof

def summarize(people, res, oof):
    ins = np.mean([r[2] for r in res]); out = np.mean([r[3] for r in res]); base = np.mean([r[4] for r in res])
    per = {}
    for s, L in oof.items():
        for n, d, p in L: per.setdefault(n, []).append(p)
    pm = np.array([np.mean(v) for v in per.values()])
    rng = np.random.default_rng(1); boots = [rng.choice(pm, len(pm)).mean() for _ in range(2000)]
    W = np.mean([r[5] for r in res], axis=0)
    return dict(n_people=len(people), n_events=sum(len(p['ev']) for p in people), in_sample=round(ins, 1), out_of_fold=round(out, 1), a_priori_same_folds=round(base, 1),
                oof_ci95=[round(float(np.percentile(boots, 2.5)), 1), round(float(np.percentile(boots, 97.5)), 1)], mean_weights={f: round(float(x), 3) for f, x in zip(FEATS, W)})

if __name__ == '__main__':
    from people_loader import load_all
    ps = [build(p) for p in load_all()]
    res, oof = cv(ps)
    out = summarize(ps, res, oof); print(json.dumps(out, indent=1))
    json.dump(out, open('/home/claude/astro/tune/cv_result.json', 'w'), indent=1)
