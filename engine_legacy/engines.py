"""Four engines on top of jyotish.py:  events/timing -> windows(),  do-dont -> dos_donts(),  remedies -> remedies(),  report -> report()
All statements carry the technique name. Nothing here is a guarantee; see BACKTEST note printed on every report."""
import sys, glob, json, re
sys.path.insert(0, '/home/claude/astro/engine')
from jyotish import *

BACKTEST_NOTE = ("Backtest note: v1 scoring was tested on 158 dated events of 19 public figures and was NOT better than chance "
                 "(avg rank 49 vs 50). Treat every window below as a pattern to examine, not a forecast.")

THEME = {  # what a planet's period tends to emphasise (traditional), with simple practical advice
 'Sun': ('authority, career standing, father, government, ego', 'Do: take visible responsibility, keep health routine. Don\'t: pick fights with bosses or elders.'),
 'Moon': ('mind, mother, home, public, emotions', 'Do: protect sleep and routine, spend time with family. Don\'t: take big decisions in a low mood.'),
 'Mars': ('energy, property, siblings, conflict, speed', 'Do: channel energy into exercise and building. Don\'t: argue, drive fast, or start legal fights.'),
 'Mercury': ('trade, skill, writing, study, communication', 'Do: learn, write, negotiate, document everything. Don\'t: sign without reading; avoid scattered effort.'),
 'Jupiter': ('growth, teachers, children, wealth, advice', 'Do: study, mentor, invest slowly. Don\'t: overpromise or over-spend on optimism.'),
 'Venus': ('relationships, comfort, money, arts, vehicles', 'Do: nurture relationships, enjoy in moderation. Don\'t: overspend on comfort or luxury.'),
 'Saturn': ('work, discipline, delay, duty, long-term results', 'Do: do the slow dependable work, keep commitments. Don\'t: take shortcuts or expect fast rewards.'),
 'Rahu': ('ambition, foreign, technology, sudden change, confusion', 'Do: verify facts twice, be careful with contracts and online dealings. Don\'t: chase get-rich-quick offers.'),
 'Ketu': ('detachment, research, endings, spirituality, loss of interest', 'Do: finish old work, simplify, research. Don\'t: start many new ventures.'),
}
AREA_ACT = {
 'career':   ('Push work visibility: proposals, launches, job or client moves.', 'Avoid quitting or switching in a hurry without a signed alternative.'),
 'status':   ('Take public roles, publish, present, ask for recognition.', 'Avoid ego fights and over-exposure of unfinished work.'),
 'marriage': ('Give time to the partner/relationship, plan formal steps if single.', 'Avoid ultimatums and major relationship decisions in anger.'),
 'children': ('Focus on children\'s needs, education and family planning talks.', 'Avoid pressure on children; avoid health shortcuts.'),
 'property': ('Research, compare and document property or vehicle purchases.', 'Avoid buying without verified papers or beyond a safe loan limit.'),
 'education':('Start or intensify courses, exams and certifications.', 'Avoid scattered learning; pick one path.'),
 'foreign':  ('Prepare passport, visas, remote/overseas work and contacts.', 'Avoid agents who promise guaranteed visas or placements.'),
 'setback':  ('Build buffers: cash, health check-up, backups, insurance review.', 'Avoid big risks, new debts, and ignoring symptoms or legal notices.'),
}

def windows(c, start, end, z_min=1.0, step=10):
    S, _, _ = life_stats(c, step=step)
    t = start; pts = []
    while t <= end:
        pts.append((t, zscore(c.tech_scores(t), S))); t += timedelta(days=step)
    out = []
    for d in DOM:
        cur = None
        for t, z in pts:
            if z[d]['all'] >= z_min:
                if cur is None: cur = [t, t, t, z[d]['all'], z[d]]
                cur[1] = t
                if z[d]['all'] > cur[3]: cur[2], cur[3], cur[4] = t, z[d]['all'], z[d]
            elif cur: out.append((d, cur)); cur = None
        if cur: out.append((d, cur))
    res = []
    for d, (a, b, pk, zz, zd) in out:
        agree = [k for k in W_TECH if zd[k] >= 0.5]
        pr = c.promise[d]
        conf = 'High' if len(agree) >= 3 and pr > 0.2 else ('Medium' if len(agree) >= 2 else 'Low')
        res.append(dict(area=d, start=a, end=b + timedelta(days=step), peak=pk, z=round(zz, 2), agree=agree, promise=round(pr, 2), confidence=conf,
                        dasha=c.dasha(pk)['vim']))
    return sorted(res, key=lambda r: r['start'])

def flags(c, t):
    """transit situation at time t"""
    T = c.tpos(t); ms = c.P['Moon']['sign']; sat = T['Saturn']['sign']; jup = T['Jupiter']['sign']
    hs = (sat - ms) % 12 + 1; hj = (jup - ms) % 12 + 1
    f = []
    if hs in (12, 1, 2): f.append(('Sade Sati (Saturn %s from Moon)' % {12: 'in 12th', 1: 'over', 2: 'in 2nd'}[hs], 'saturn_ss', hs))
    if hs == 8: f.append(('Saturn in 8th from Moon (Ashtama Shani)', 'saturn_8', hs))
    if hs == 4: f.append(('Saturn in 4th from Moon (Kantaka Shani)', 'saturn_4', hs))
    if hj in (2, 5, 7, 9, 11): f.append(('Jupiter in %dth from Moon (supportive gochar)' % hj, 'jup_good', hj))
    if hj in (6, 8, 12): f.append(('Jupiter in %dth from Moon (weak gochar)' % hj, 'jup_weak', hj))
    for n in ('Rahu', 'Ketu'):
        if T[n]['sign'] == c.lag: f.append(('%s over the lagna sign' % n, 'node_lag', 1))
        if T[n]['sign'] == ms: f.append(('%s over the Moon sign' % n, 'node_moon', 1))
    return f

def dos_donts(c, t):
    da = c.dasha(t); v = da['vim']; out = []
    names = ['Mahadasha', 'Antardasha', 'Pratyantar']
    for nm, p in zip(names, v):
        th, adv = THEME[p]
        if nm != 'Pratyantar':
            out.append(('context', f'{nm} {p}: themes - {th}', 'Parashari dasha'))
            out.append(('dodont', adv, f'Parashari: {p} period themes'))
    for txt, key, h in flags(c, t):
        if key == 'saturn_ss': out.append(('dodont', f'{txt}: Do keep routine, finish pending duties, save a buffer. Don\'t start risky ventures or sign large long-term debts hurriedly.', 'Gochar (Saturn over Moon)'))
        if key == 'saturn_8': out.append(('dodont', f'{txt}: Do health check-ups and keep backups. Don\'t take legal/financial risks.', 'Gochar'))
        if key == 'saturn_4': out.append(('dodont', f'{txt}: Do check home and vehicle upkeep. Don\'t postpone repairs.', 'Gochar'))
        if key == 'jup_good': out.append(('dodont', f'{txt}: Do use this window for growth steps - study, expansion, family/child matters.', 'Gochar (Jupiter)'))
        if key == 'jup_weak': out.append(('dodont', f'{txt}: Don\'t over-expand or lend freely; keep plans conservative.', 'Gochar (Jupiter)'))
        if key.startswith('node'): out.append(('dodont', f'{txt}: Do double-check facts and documents. Don\'t trust hype or rush.', 'Gochar (nodes)'))
    S, _, _ = life_stats(c, step=30)
    z = zscore(c.tech_scores(t), S)
    act = sorted(((z[d]['all'], d) for d in DOM), reverse=True)[:3]
    for zz, d in act:
        if zz >= 0.8:
            out.append(('dodont', f'Area "{d}" is active now (z={zz:.1f}). Do: {AREA_ACT[d][0]}', 'Dasha + KP + transit score'))
            out.append(('dodont', f'Area "{d}" - Don\'t: {AREA_ACT[d][1]}', 'Dasha + KP + transit score'))
    return out

# ---- remedies
_LK = None; _GB = None
def _load():
    global _LK, _GB
    if _LK is None:
        _LK = []
        for f in glob.glob('/home/claude/astro/db/raw/SRC_lalkitab_*.jsonl'): _LK += [json.loads(l) for l in open(f)]
        _GB = [json.loads(l) for l in open('/home/claude/astro/db/gautam_final_v2.jsonl')]
        _GB = [x for x in _GB if x.get('remedy') and x.get('status') != 'flagged_unreliable']
_PW = {'Sun': ('Sunday', 'offer water to the Sun at sunrise; respect father/elders'), 'Moon': ('Monday', 'serve milk/water to those in need; keep mother content'),
 'Mars': ('Tuesday', 'donate lentils or help a sibling; keep anger in check'), 'Mercury': ('Wednesday', 'feed green fodder to cattle; speak truthfully'),
 'Jupiter': ('Thursday', 'respect teachers; donate books/yellow foods to a needy student'), 'Venus': ('Friday', 'respect women of the family; keep home clean'),
 'Saturn': ('Saturday', 'help workers/elderly; be punctual and keep promises'), 'Rahu': ('Saturday', 'keep surroundings clean; avoid intoxicants'), 'Ketu': ('Tuesday/Thursday', 'feed stray dogs; simple meditation')}
def remedies(c, t, max_per=2):
    _load(); da = c.dasha(t)['vim']; picks = []
    for p in da[:2]: picks.append((p, 'running dasha lord'))
    for p, v in c.P.items():
        if p in ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn') and v['sign'] == DEBIL[p]: picks.append((p, 'debilitated'))
    if any(k == 'saturn_ss' for _, k, _ in flags(c, t)): picks.append(('Saturn', 'Sade Sati running'))
    seen = set(); out = []
    for p, why in picks:
        if (p, why) in seen: continue
        seen.add((p, why)); day, tr = _PW[p]
        item = dict(planet=p, why=why, traditional=f'{p} ({day}): {tr}. Free or low-cost only.')
        lkh = c.P[p]['sign'] + 1      # Lal Kitab fixed house = sign number
        lk = [x for x in _LK if x['category'] == 'upay' and x['topic'] == f'{p} house {lkh}'][:max_per]
        item['lal_kitab'] = [dict(house=lkh, remedy=x['remedy'], note=x.get('conditions_cancellation', '')) for x in lk]
        pat = re.compile(rf'\b{p}\b', re.I); hp = re.compile(rf'\b(house {c.hp[p]}|{c.hp[p]}(st|nd|rd|th) house)\b', re.I)
        gb = [x for x in _GB if pat.search(x['input']) and hp.search(x['input'])][:max_per]
        item['gautam'] = [dict(rid=x['rid'], when=x['input'][:100], remedy=x['remedy'][:160]) for x in gb]
        out.append(item)
    return out

def report(c, start, end, path=None):
    L = []
    L.append(f'JYOTISH REPORT - {c.name}  window {start.date()} to {end.date()}')
    L.append(BACKTEST_NOTE); L.append('')
    L.append(f'Lagna {SIGNS[c.lag]} {c.asc%30:.1f} deg | Moon {SIGNS[c.P["Moon"]["sign"]]} / {NAK[c.P["Moon"]["nak"]]}')
    L.append('Natal promise per area (-1..+1, higher = better supported): ' + ', '.join(f'{d} {v:+.2f}' for d, v in c.promise.items()))
    L.append('')
    L.append('1. EVENT + TIMING ENGINE  (areas that are "hot": own-life z>=1.0; agree = techniques with z>=0.5)')
    for w in windows(c, start, end):
        L.append(f'  {w["start"].date()} -> {w["end"].date()} | {w["area"]:9s} | peak {w["peak"].date()} z={w["z"]} | agree={",".join(w["agree"]) or "-"} | promise {w["promise"]:+.2f} | confidence {w["confidence"]} | dasha {"-".join(w["dasha"])}')
    mid = start + (end - start) / 2
    L.append(''); L.append('2. DO / DON\'T ENGINE  (as of window start)')
    for kind, txt, src in dos_donts(c, start):
        L.append(f'  [{kind}] {txt}   <{src}>')
    L.append(''); L.append('3. REMEDIES ENGINE  (optional, free/low-cost, never a substitute for medical, legal, financial action; untested)')
    for r in remedies(c, start):
        L.append(f'  {r["planet"]} - {r["why"]}: {r["traditional"]}')
        for x in r['lal_kitab']: L.append(f'     Lal Kitab (house {x["house"]}): {x["remedy"]}')
        for x in r['gautam']: L.append(f'     Gautam {x["rid"]}: {x["remedy"]}')
    txt = '\n'.join(L)
    if path: open(path, 'w').write(txt)
    return txt

if __name__ == '__main__':
    import argparse
    a = argparse.ArgumentParser()
    a.add_argument('--name'); a.add_argument('--dob'); a.add_argument('--tob'); a.add_argument('--tz', type=float, default=5.5)
    a.add_argument('--lat', type=float); a.add_argument('--lon', type=float)
    a.add_argument('--start'); a.add_argument('--end'); a.add_argument('--out')
    x = a.parse_args()
    y, m, d = map(int, x.dob.split('-')); hh, mm, *ss = map(int, x.tob.split(':'))
    c = Chart(x.name, D(y, m, d, hh, mm, *(ss or [0])), x.tz, x.lat, x.lon)
    s = D(*map(int, x.start.split('-'))); e = D(*map(int, x.end.split('-')))
    print(report(c, s, e, x.out))
