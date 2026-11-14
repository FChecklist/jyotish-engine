"""BCP (Bhrigu Chakra Paddhati) as stated by teacher: house activated in a year = completed age mod 12 counted from lagna (age 0 -> 1st).
Variant A: activated house in domain houses. Variant B: A and (Saturn or Jupiter transit sign aspects/occupies activated house sign, Parashari aspects). Pre-registered, no tuning."""
import sys, numpy as np
sys.path.insert(0,'/home/claude/astro/engine'); sys.path.insert(0,'/home/claude/astro')
from jyotish import *
from features import pct
import people_loader as L
from datetime import timedelta
rng=np.random.default_rng(3)
def act_house(c,t):
    b=c.local-timedelta(hours=c.tz); age=int((t-b).days/365.2422); return age%12+1
def score(c,t,d,var):
    spec=DOM[d]; hs=spec['h']; wts=[1.0 if i==0 else .7 for i in range(len(hs))]; ah=act_house(c,t)
    if spec['pos']: a=sum(w for h,w in zip(hs,wts) if h==ah)/sum(wts)
    else: a=1.0 if ah in hs else 0.0
    if var=='A': return a
    T=c.tpos(t); H=(c.lag+ah-1)%12; tr=0
    for p,off in (('Jupiter',(0,4,6,8)),('Saturn',(0,2,6,9))):
        if (H-T[p]['sign'])%12 in off: tr+=.5
    return a*(0.5+tr)   # activation amplified when Jupiter/Saturn also touch the house
res={'A':[],'B':[]}; by={'A':{},'B':{}}
for p in L.load_all():
    c=Chart(p['name'],p['local'],p['tz'],p['lat'],p['lon']); b=p['local']-timedelta(hours=p['tz']); last=max(e[0] for e in p['events'])
    t0,t1=b+timedelta(days=365.25*12),min(last+timedelta(days=730),b+timedelta(days=365.25*85)); g=grid(c,t0,t1,10)
    for var in 'AB':
        G={d:np.array([score(c,t,d,var) for t in g]) for d in DOM}
        for ed,dom,lab in p['events']:
            if ed<t0 or dom not in DOM: continue
            v=pct(G[dom],score(c,ed,dom,var)); res[var].append((p['name'],dom,v)); by[var].setdefault(p['name'],[]).append(v)
for var in 'AB':
    v=np.array([x[2] for x in res[var]]); ms=np.array([np.mean(a) for a in by[var].values()])
    bs=[ms[rng.integers(0,len(ms),len(ms))].mean() for _ in range(3000)]
    print(var,'n',len(v),'mean',round(v.mean(),1),'CI',round(np.percentile(bs,2.5),1),round(np.percentile(bs,97.5),1),'top20',round((v>=80).mean()*100,1))
    for d in sorted(set(x[1] for x in res[var])):
        w=[x[2] for x in res[var] if x[1]==d]
        if len(w)>=10: print('   ',d,len(w),round(np.mean(w),1))
