"""Technique engine. A technique = JSON spec: steps (primitive ops) -> named values -> fire conditions.
Software decides which techniques fire for a chart+time; output is structured evidence for AI inference (see INFERENCE_PROMPT.md)."""
import sys, json, glob, os
sys.path.insert(0, '/home/claude/astro'); sys.path.insert(0, '/home/claude/astro/engine'); sys.path.insert(0, '/home/claude/astro/tune')
from datetime import timedelta
from jyotish import *
from ac import SLORD, jaim_aspects
from newfeat import bav
PAR = {'Jupiter': (1, 5, 7, 9), 'Saturn': (1, 3, 7, 10), 'Mars': (1, 4, 7, 8)}   # house offsets counted from planet incl. itself(1)
def _birth(c): return c.local - timedelta(hours=c.tz)
class Ctx:
    def __init__(s, c, t, area):
        s.c, s.t, s.area = c, t, area; s.T = c.tpos(t); s.da = c.dasha(t); s.spec = DOM[area]
        s.bav = getattr(c, '_bav', None) or bav(c); c._bav = s.bav
def _sign_house(c, sign): return (sign - c.lag) % 12 + 1
OPS = {}
def op(f): OPS[f.__name__] = f; return f
@op
def age(x): return int((x.t - _birth(x.c)).days / 365.2422)
@op
def age_house(x, age): return age % 12 + 1
@op
def area_houses(x): return list(x.spec['h'])
@op
def vim_lords(x, level=2): return x.da['vim'][:level]
@op
def lords_link(x, planets, houses):
    c = x.c; return any((h in c.owns[p]) or c.hp[p] == h for p in planets for h in houses)
@op
def lords_own(x, planets, houses):
    c = x.c; return any(h in c.owns[p] for p in planets for h in houses)
@op
def transit_house(x, planet, frm='lagna'):
    base = x.c.lag if frm == 'lagna' else x.c.P['Moon']['sign']; return (x.T[planet]['sign'] - base) % 12 + 1
@op
def transit_touches(x, planet, houses, frm='lagna'):
    base = x.c.lag if frm == 'lagna' else x.c.P['Moon']['sign']; ps = x.T[planet]['sign']
    return any(((base + h - 1 - ps) % 12 + 1) in PAR[planet] for h in houses)
@op
def bav_transit(x, planet): return x.bav[planet][x.T[planet]['sign']]
@op
def jaimini_karaka_sign(x, rank):
    ks = sorted(['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'], key=lambda p: -x.c.P[p]['deg']); return x.c.P[ks[rank]]['sign']
@op
def chara_links(x, sign):
    if not x.da['chara']: return False
    return any(sg == sign or sign in jaim_aspects(sg) for (sg, a, b) in x.da['chara'])
@op
def contains(x, value, items): return value in items
@op
def at_least(x, value, n): return value >= n
@op
def both(x, a, b): return bool(a) and bool(b)
@op
def either(x, a, b): return bool(a) or bool(b)
@op
def negate(x, a): return not a
def _res(env, v):
    return env[v[1:]] if isinstance(v, str) and v.startswith('$') else v
def run_spec(spec, x):
    env = {}
    for st in spec['steps']:
        args = {k: _res(env, v) for k, v in st.get('args', {}).items()}
        env[st['as']] = OPS[st['op']](x, **args)
    ok = all(env[f['ref']] == f['equals'] if 'equals' in f else env[f['ref']] for f in spec['fire'])
    return ok, env
def load_specs(d='/home/claude/astro/tech/specs'):
    out = []
    for fn in sorted(glob.glob(d + '/*.json')):
        for s in json.load(open(fn)):
            for area in s['areas']:
                t = dict(s); t['id'] = f"{s['id']}@{area}"; t['area'] = area; out.append(t)
    return out
def fired(c, t, specs=None, areas=None):
    specs = specs or load_specs(); res = []; cache = {}
    for s in specs:
        if areas and s['area'] not in areas: continue
        x = cache.get(s['area']) or Ctx(c, t, s['area']); cache[s['area']] = x
        ok, env = run_spec(s, x)
        if ok: res.append(dict(id=s['id'], area=s['area'], polarity=s['polarity'], source=s['source'], steps=s['text'], evidence={k: v for k, v in env.items() if not isinstance(v, (list, dict)) or len(str(v)) < 60}))
    return res
