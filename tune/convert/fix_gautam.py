"""Mechanical repair of derived examples. Usage: fix_gautam.py IN OUT
Recomputes every 'lagna X' label from the example's (house, sign) cell, and reports dignity slips (exalted/debilitated/own sign claims that do not match the sign)."""
import sys, json, re
SG = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
EX = {'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn','Mercury':'Virgo','Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
DB = {p: SG[(SG.index(s)+6) % 12] for p, s in EX.items()}
OWN = {'Sun':['Leo'],'Moon':['Cancer'],'Mars':['Aries','Scorpio'],'Mercury':['Gemini','Virgo'],'Jupiter':['Sagittarius','Pisces'],'Venus':['Taurus','Libra'],'Saturn':['Capricorn','Aquarius']}
fixed = 0; flags = []; rows = []
for l in open(sys.argv[1], encoding='utf8'):
    if not l.strip(): continue
    r = json.loads(l)
    if r.get('type') == 'stmt':
        for d in r['derived_examples']:
            h, s = d['cell']; lag = SG[(SG.index(s) - (int(h) - 1)) % 12]; t = d['reading']
            t2 = re.sub(r'lagna (%s)' % '|'.join(SG), 'lagna ' + lag, t)
            if t2 != t: fixed += 1; d['reading'] = t2
            for p in EX:
                if re.search(p + r'[^.]{0,40}exalted', t2) and s != EX[p]: flags.append((r['id'], 'exalted', p, s))
                if re.search(p + r'[^.]{0,40}debilitat', t2) and s != DB[p]: flags.append((r['id'], 'debilitated', p, s))
                if re.search(p + r'[^.]{0,30}own sign', t2) and s not in OWN[p]: flags.append((r['id'], 'own', p, s))
    rows.append(r)
with open(sys.argv[2], 'w', encoding='utf8') as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('lagna labels fixed', fixed, '| dignity flags', len(flags), flags[:5])
