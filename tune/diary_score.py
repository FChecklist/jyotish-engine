"""Measure the engine against a diary. rows: [(date, person, rating 1-5)]; grades: {(date, person): net score}. Permutation test: shuffled ratings give the chance baseline.
Report correlation and the share of shuffles that did at least as well. No percentages are shown to users until this passes on >= 90 days per person."""
import random
def pearson(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    sx = sum((a - mx) ** 2 for a in x) ** .5; sy = sum((b - my) ** 2 for b in y) ** .5
    return 0.0 if sx == 0 or sy == 0 else sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)
def score(rows, grades, n_shuffle=2000, seed=0):
    pairs = [(grades[(d, p)], r) for d, p, r in rows if (d, p) in grades]
    x = [a for a, _ in pairs]; y = [b for _, b in pairs]; obs = pearson(x, y); rnd = random.Random(seed); ge = 0
    for _ in range(n_shuffle):
        yy = y[:]; rnd.shuffle(yy); ge += pearson(x, yy) >= obs
    return {'n_days': len(pairs), 'correlation': round(obs, 3), 'p_one_sided': round((ge + 1) / (n_shuffle + 1), 4)}
