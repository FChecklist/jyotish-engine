import swisseph as swe, itertools, sys
from zodiac import *
import houses as H
def jd(y,m,d,h,mi,tz): return swe.julday(y,m,d,h+mi/60-tz)
CH=[('Einstein',jd(1879,3,14,11,30,0.6657),48.4,9.99),('Delhi',jd(1990,6,15,14,20,5.5),28.6,77.2),
    ('Sydney',jd(1985,12,1,3,5,10),-33.9,151.2),('Tromso',jd(2001,12,21,12,0,1),69.65,18.96),('Equator',jd(1975,9,23,6,0,0),0.0,-78.5)]
PL=[swe.SUN,swe.MOON,swe.MARS,swe.MERCURY,swe.JUPITER,swe.VENUS,swe.SATURN,swe.MEAN_NODE]
fails=0
for name,j,lat,lon in CH:
    for ay in ('lahiri','kp','tropical'):
        fl=H._flags(ay)|swe.FLG_SWIEPH
        pl=[swe.calc_ut(j,p,fl)[0][0] for p in PL]
        moves={}
        for sy in H.SYSTEMS:
            try: c=H.build(j,lat,lon,sy,ay)
            except Exception as e:
                if sy=='placidus' and 'undefined' in str(e): print('expected refusal',name,sy,e); continue
                print('FAIL build',name,ay,sy,e); fails+=1; continue
            # invariants
            tot=sum(h['width'] for h in c['houses'])
            ok1=abs(tot-360)<1e-6
            ok2=all(abs(sum(d for _,d in h['spans'])-h['width'])<1e-5 for h in c['houses'])
            ok3=all(((c['houses'][i]['end']-c['houses'][i]['start'])%360)>0 for i in range(12))
            hp=[H.house_of(x,c) for x in pl]
            ok4=all(1<=h<=12 for h in hp)
            if not(ok1 and ok2 and ok3 and ok4): print('INVARIANT FAIL',name,ay,sy,ok1,ok2,ok3,ok4); fails+=1
            if sy=='whole' and not all(h['n_signs']==1 for h in c['houses']): print('whole not 1 sign',name); fails+=1
            if sy in('whole',): 
                lagsign=sign_of(c['asc'])
                if any(h['start_sign']!=(lagsign+h['h']-1)%12 for h in c['houses']): print('whole sign order bad'); fails+=1
            moves[sy]=(hp,[h['n_signs'] for h in c['houses']],c['asc'])
        if 'whole' in moves:
            w=moves['whole'][0]
            for sy in ('equal_asc','equal_mid','sripati','placidus'):
                if sy in moves:
                    diff=sum(1 for a,b in zip(w,moves[sy][0]) if a!=b)
                    multi=sum(1 for n in moves[sy][1] if n>1); skip=12-len({s for s in range(12)}) # placeholder
                    print(f'{name:9s} {ay:9s} {sy:10s} planets in other house vs whole-sign: {diff}/8   houses spanning >1 sign: {multi}')
print('FAILS',fails)

# hand-checkable unit tests of spans()
assert H.spans(205,235)==[(6,5.0),(7,25.0)], H.spans(205,235)   # 25 Libra -> 25 Scorpio
assert H.spans(205,265)==[(6,5.0),(7,30.0),(8,25.0)]            # a 60 degree stretch covers three signs, middle one whole
assert H.spans(0,30)==[(0,30.0)] and H.spans(330,360)==[(11,30.0)] and H.spans(350,20)==[(11,10.0),(0,20.0)]  # wrap-around
assert abs(sum(d for _,d in H.spans(10,100))-90)<1e-9
from zodiac import *
assert natural_sign_of_house(1)==0 and natural_house_of_sign(11)==12 and house_from(3,5)==3 and sign_at_house(3,3)==5 and house_from(5,3)==11
print('unit tests ok')

sys.exit(1 if fails else 0)
