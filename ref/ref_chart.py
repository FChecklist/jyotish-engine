import sys, json
from jhora.panchanga import drik
from jhora import utils
y,m,d,H,M=[int(x) for x in sys.argv[1:6]]; tz,lat,lon=[float(x) for x in sys.argv[6:9]]
drik.set_ayanamsa_mode('LAHIRI')
place=drik.Place('p',lat,lon,tz)
jd=utils.julian_day_number(drik.Date(y,m,d),(H,M,0))
a=drik.ascendant(jd,place); out={'asc':a[0]*30+a[1]}
for chart in (1,9):
    pp=drik.dhasavarga(jd,place,divisional_chart_factor=chart)
    for r in pp:
        k='asc' if r[0]=='L' else int(r[0])
        out[f'D{chart}_{k}']=r[1][0]*30+r[1][1]
print(json.dumps(out))
