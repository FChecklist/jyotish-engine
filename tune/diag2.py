import pickle,glob,numpy as np,random
from features import pct
from newfeat import NEW
P=[pickle.load(open(f,'rb')) for f in sorted(glob.glob('ncache/*.pkl'))]
rng=np.random.default_rng(2); random.seed(2)
def run(w,sub=lambda p,e:True,wrong=False):
    out=[]
    for p in P:
        for e in p['ev']:
            if not sub(p,e): continue
            d=e['dom']
            if wrong: d=random.choice([x for x in p['G'] if x!=d])
            sg=p['G'][d]@w; out.append((p['name'],e['dom'],pct(sg,float(e['x']@w))))
    return out
def ci(r):
    by={}
    for n,d,v in r: by.setdefault(n,[]).append(v)
    ms=np.array([np.mean(a) for a in by.values()]); bs=[ms[rng.integers(0,len(ms),len(ms))].mean() for _ in range(3000)]
    v=np.array([x[2] for x in r]); return v.mean(),np.percentile(bs,2.5),np.percentile(bs,97.5),(v>=80).mean()*100,len(v)
print('n people',len(P))
print('== single new technique')
for i,f in enumerate(NEW):
    w=np.zeros(5);w[i]=1;m,lo,hi,h,n=ci(run(w));wm=np.mean([x[2] for x in run(w,wrong=True)])
    print(f'{f:7s} n={n} mean={m:5.1f} [{lo:5.1f},{hi:5.1f}] top20={h:4.1f}%  wrong-domain={wm:5.1f}')
# z-score each feature per person-domain grid then equal-sum
def zrun(w):
    out=[]
    for p in P:
        zs={}
        for d,G in p['G'].items():
            mu=G.mean(0);sd=G.std(0);sd[sd==0]=1;zs[d]=(mu,sd)
        for e in p['ev']:
            mu,sd=zs[e['dom']];G=(p['G'][e['dom']]-mu)/sd;x=(e['x']-mu)/sd
            out.append((p['name'],e['dom'],pct(G@w,float(x@w))))
    return out
m,lo,hi,h,n=ci(zrun(np.ones(5)));print(f'all-new z-equal mean={m:.1f} [{lo:.1f},{hi:.1f}] top20={h:.1f}%')
print('== per domain (all-new z-equal)')
r=zrun(np.ones(5))
for d in sorted(set(x[1] for x in r)):
    v=[x[2] for x in r if x[1]==d]; print(d,len(v),round(np.mean(v),1))
print('== per technique x domain (mean pct)')
doms=sorted(set(x[1] for x in r)); print('       ',*[f'{d[:7]:>8s}' for d in doms])
for i,f in enumerate(NEW):
    w=np.zeros(5);w[i]=1;rr=run(w);print(f'{f:7s}',*[f'{np.mean([x[2] for x in rr if x[1]==d]):8.1f}' for d in doms])
# permutation null for best single & all-new
null=[]
for _ in range(500):
    ms=[]
    for p in P:
        for e in p['ev']:
            G=p['G'][e['dom']]@np.ones(5); ms.append(pct(G,G[rng.integers(len(G))]))
    null.append(np.mean(ms))
print('null sd',round(np.std(null),2),'-> chance band 50 +/-',round(1.96*np.std(null),1))
