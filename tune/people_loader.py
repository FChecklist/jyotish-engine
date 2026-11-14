import sys, json, glob
sys.path.insert(0, '/home/claude/astro/engine')
from datetime import datetime as D
def load_all():
    from bt_data import P
    people = [dict(name=n, grade=g, local=loc, tz=tz, lat=la, lon=lo, events=evs, src='bt1') for n, g, loc, tz, la, lo, evs in P]
    for f in sorted(glob.glob('/home/claude/astro/bt2/D*/people.jsonl')):
        for l in open(f):
            l = l.strip()
            if not l: continue
            try:
                r = json.loads(l)
                ev = [(D.strptime(e['date'], '%Y-%m-%d'), e['domain'], e['label']) for e in r['events']]
                people.append(dict(name=r['name'], grade=r.get('rodden', '?'), local=D.strptime(r['birth_local'], '%Y-%m-%d %H:%M:%S'), tz=float(r['utc_offset_hours']),
                                   lat=float(r['lat']), lon=float(r['lon']), events=ev, src=f))
            except Exception as ex: print('skip', f, ex)
    import os
    if os.environ.get('DROP_APPROX'):
        for p in people: p['events']=[e for e in p['events'] if not (e[1]=='foreign' and (e[0].day==1 or 'honorary' in e[2].lower() or 'citizenship' in e[2].lower()))]
    seen=set(); out=[]
    for p in people:
        k=p['name'].lower().replace('_',' ').replace('.','')
        if k in seen: continue
        seen.add(k); out.append(p)
    return out
