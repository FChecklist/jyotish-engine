"""Validate Gautam lecture notes. Usage: python3 check_gautam.py OUTFILE INFILE
Checks: JSON per line, required keys, valid cells, unique ids and unique `says`, every input [timestamp] chunk has at least one row (nothing left out)."""
import sys, json, re
SIGNS = {'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces', '*'}
HOUSES = {str(i) for i in range(1, 13)} | {'*'}
STMT = ['id', 'type', 'ts', 'hindi', 'says', 'kind', 'scope', 'planets', 'cells_stated', 'cells_derived_method', 'derived_examples', 'charts', 'ambiguity', 'classical_check', 'effect_valence', 'confidence', 'tradition_claim']
SKIP = ['id', 'type', 'ts', 'reason', 'gist']
KINDS = {'rule', 'definition', 'remedy', 'timing', 'karaka', 'principle', 'other'}
REASONS = {'intro', 'story', 'joke', 'ad', 'audience', 'repeat', 'unreadable', 'opinion-not-astrology', 'other'}
PLANETS = {'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Uranus', 'Neptune', 'Pluto'}


def main():
    out, inp = sys.argv[1], sys.argv[2]
    err = []; ids = set(); says = {}; tss = set(); n_stmt = n_skip = n_low = 0
    try: lines = [l for l in open(out, encoding='utf8') if l.strip()]
    except Exception as e: print('ERROR cannot read', e); sys.exit(1)
    for i, l in enumerate(lines, 1):
        try: r = json.loads(l)
        except Exception as e: err.append(f'line {i}: bad JSON {str(e)[:60]}'); continue
        t = r.get('type')
        if t == 'stmt':
            n_stmt += 1
            for k in STMT:
                if k not in r: err.append(f"line {i}: missing {k}")
            if r.get('kind') not in KINDS: err.append(f"line {i}: bad kind {r.get('kind')}")
            if r.get('confidence') not in ('high', 'medium', 'low'): err.append(f'line {i}: bad confidence')
            if r.get('confidence') == 'low': n_low += 1
            if r.get('effect_valence') not in ('good', 'bad', 'mixed', 'neutral'): err.append(f'line {i}: bad effect_valence')
            for p in r.get('planets') or []:
                if p not in PLANETS: err.append(f'line {i}: bad planet {p}')
            cs = r.get('cells_stated')
            if not isinstance(cs, list) or not cs: err.append(f'line {i}: cells_stated must be a non-empty list')
            else:
                for c in cs:
                    if not (isinstance(c, list) and len(c) == 2 and str(c[0]) in HOUSES and c[1] in SIGNS): err.append(f'line {i}: bad cell {c}')
            for d in r.get('derived_examples') or []:
                c = d.get('cell') if isinstance(d, dict) else None
                if not (isinstance(c, list) and len(c) == 2 and str(c[0]) in HOUSES - {'*'} and c[1] in SIGNS - {'*'} and d.get('reading')): err.append(f'line {i}: bad derived example {str(d)[:60]}')
            s = (r.get('says') or '').strip().lower()
            if len(s) < 20: err.append(f'line {i}: says too short')
            if s in says: err.append(f'line {i}: same says as line {says[s]}')
            says[s] = i
        elif t == 'skip':
            n_skip += 1
            for k in SKIP:
                if k not in r: err.append(f'line {i}: missing {k}')
            if r.get('reason') not in REASONS: err.append(f"line {i}: bad reason {r.get('reason')}")
        else: err.append(f'line {i}: type must be stmt or skip')
        if r.get('id') in ids: err.append(f"line {i}: duplicate id {r.get('id')}")
        ids.add(r.get('id')); tss.add(r.get('ts'))
    want = re.findall(r'^\[(\d+:\d+(?::\d+)?)\]', open(inp, encoding='utf8').read(), re.M)
    miss = [w for w in want if w not in tss]
    if miss: err.append(f'timestamp chunks with no row: {miss[:12]}{"..." if len(miss) > 12 else ""}')
    if err:
        print('ERRORS:'); [print(' ', e) for e in err[:40]]; sys.exit(1)
    print(f'OK  stmt={n_stmt} skip={n_skip} low={n_low} chunks_covered={len(want)}/{len(want)}')


if __name__ == '__main__':
    main()
