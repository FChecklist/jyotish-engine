import subprocess, json, sys
sys.path.insert(0,'/home/claude/astro/tune')
from newfeat import div_sign
CH=[('Delhi1990',1990,6,15,14,20,5.5,28.6139,77.2090),('Quito1975',1975,9,23,6,0,-5.0,-0.18,-78.47),('Sydney1985',1985,12,1,3,5,11.0,-33.87,151.21),
    ('Delhi1947',1947,8,15,0,0,5.5,28.6139,77.2090),('Nixon1913',1913,1,9,21,35,-8.0,33.883,-117.817),('Einstein1879',1879,3,14,11,30,0.6657,48.4,9.99)]
PL=['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']
def d(a,b): return ((a-b+180)%360)-180
rows=[]
for name,*a in CH:
    args=[str(x) for x in a]
    mine=json.loads(subprocess.check_output(['python3','/home/claude/astro/ref/mine_chart.py']+args,text=True))
    ref=json.loads(subprocess.check_output(['/home/claude/astro/ref/venv/bin/python','/home/claude/astro/ref/ref_chart.py']+args,text=True))
    res={'asc':d(mine['asc'],ref['asc'])}
    d9ok=0; bad=[]
    for i,p in enumerate(PL):
        res[p]=d(mine[p],ref[f'D1_{i}'])
        ok=div_sign(mine[p],9)==int(ref[f'D9_{i}']//30); d9ok+=ok
        if not ok: bad.append(p)
    rows.append((name,res,d9ok,bad))
for name,res,d9,bad in rows:
    big={k:round(v,4) for k,v in res.items() if k not in('Rahu','Ketu') and abs(v)>0.002}
    print(f"{name:13s} asc diff {res['asc']*3600:7.1f}\"  max planet diff {max(abs(res[p]) for p in PL[:7])*3600:6.1f}\"  nodes diff {res['Rahu']:.3f}deg  D9 sign matches {d9}/9 mismatch:{bad}")
