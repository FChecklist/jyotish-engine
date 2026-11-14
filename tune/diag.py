import pickle,glob,numpy as np,random
from features import *
P=[pickle.load(open(f,'rb')) for f in sorted(glob.glob('cache/*.pkl'))]
rng=np.random.default_rng(1)
def res(w,sub=None):
    r=evaluate(P,w); return [x for x in r if (sub is None or sub(x))]
def summ(r):
    v=np.array([x[2] for x in r]); 
    byp={}
    for n,d,p in r: byp.setdefault(n,[]).append(p)
    ms=np.array([np.mean(a) for a in byp.values()])
    bs=[ms[rng.integers(0,len(ms),len(ms))].mean() for _ in range(2000)]
    return len(v),v.mean(),np.percentile(bs,2.5),np.percentile(bs,97.5),(v>=80).mean()*100
print('n people',len(P))
print('\n== single technique / group (mean pct, CI over people, top20% hit)')
for i,f in enumerate(FEATS):
    w=np.zeros(9);w[i]=1;n,m,lo,hi,h=summ(res(w));print(f'{f:7s} n={n} mean={m:5.1f} [{lo:5.1f},{hi:5.1f}] top20={h:4.1f}%')
for name,w in [('equal all',np.ones(9)),('apriori tech',[.3,.25,.3,.075,.075,0,0,0,0]),('rules only',[0,0,0,0,0,1,1,1,1]),('tech equal',[1,1,1,1,1,0,0,0,0])]:
    n,m,lo,hi,h=summ(res(w));print(f'{name:12s} mean={m:5.1f} [{lo:5.1f},{hi:5.1f}] top20={h:4.1f}%')
print('\n== by domain (equal-all)')
doms=sorted(set(x[1] for x in res(np.ones(9))))
for d in doms:
    r=res(np.ones(9),lambda x:x[1]==d); 
    if len(r)>=5: n,m,lo,hi,h=summ(r);print(f'{d:10s} n={n:3d} mean={m:5.1f} top20={h:4.1f}%')
print('\n== by data grade (equal-all)')
gr={p['name']:p['grade'] for p in P}
for g in sorted(set(gr.values())):
    r=res(np.ones(9),lambda x:gr[x[0]]==g)
    if r: n,m,lo,hi,h=summ(r);print(g,n,round(m,1))
print('\n== permutation null: shuffle event dates among that person\'s own grid (random dates), equal-all')
w=np.ones(9);null=[]
for _ in range(300):
    ms=[]
    for p in P:
        for e in p['ev']:
            sg=p['G'][e['dom']]@w; ms.append(100*rng.random())  # placeholder uniform
    null.append(np.mean(ms))
# better null: pick random grid point as the 'event'
null=[]
for _ in range(500):
    ms=[]
    for p in P:
        for e in p['ev']:
            G=p['G'][e['dom']]; sg=G@w; k=rng.integers(len(sg)); ms.append(pct(sg,sg[k]))
    null.append(np.mean(ms))
obs=np.mean([x[2] for x in res(w)])
print('observed',round(obs,2),'null mean',round(np.mean(null),2),'null sd',round(np.std(null),2),'p(one-sided)',(np.array(null)>=obs).mean())
print('\n== wrong-domain control: score each event with a DIFFERENT domain\'s grid (equal-all)')
ms=[]
for p in P:
    for e in p['ev']:
        others=[d for d in p['G'] if d!=e['dom']]; d2=random.choice(others)
        sg=p['G'][d2]@w; ms.append(pct(sg,float(e['x']@w)))
print('wrong-domain mean pct',round(np.mean(ms),1),'(should be ~chance if domain logic matters; if same as right-domain, domain logic adds nothing)')
