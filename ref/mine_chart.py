import sys, json
sys.path.insert(0,'/home/claude/astro/engine')
from datetime import datetime
from jyotish import Chart
y,m,d,H,M,tz,lat,lon=[float(x) if '.' in x else int(x) for x in sys.argv[1:9]]
c=Chart('t',datetime(y,m,d,H,M,0),tz,lat,lon)
out={'asc':c.asc}
for p,v in c.P.items(): out[p]=v['lon']
print(json.dumps(out))
