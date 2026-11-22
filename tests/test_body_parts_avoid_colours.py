"""Tests for core/body_parts.py, core/avoid_colours.py, their CSV tables, the D1 migrations 0002/0003 and tune/build_seed_sql.py.
Expected values are TYPED BY HAND here (not read from the CSV or computed by the engine). Uses sqlite3 in memory; touches no live database."""
import sys, os, json, csv, shutil, sqlite3, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'core'))
import body_parts as B
import avoid_colours as A
import planet_colors as PC
from zodiac import SIGNS

STATUS = 'DEFAULT, owner to confirm'

# ---- hand-typed expectations -------------------------------------------------------------------------------
PRIMARY = ['head', 'face', 'chest', 'heart', 'stomach', 'waist', 'lower abdomen', 'private parts', 'thighs', 'knees', 'calves', 'feet']
EXTENDED_SAMPLE = {1: 'brain', 2: 'throat', 3: 'shoulders', 4: 'ribs', 5: 'spine', 6: 'intestines', 7: 'kidneys', 8: 'reproductive organs',
                   9: 'hips', 10: 'joints', 11: 'ankles', 12: 'toes'}
COLOUR = {'Sun': 'Orange', 'Moon': 'White', 'Mars': 'Red', 'Mercury': 'Green', 'Jupiter': 'Yellow', 'Venus': 'Off white', 'Saturn': 'Black'}
# lagna -> planets to avoid (functional malefics: lord of 6/8/12, not lord of 1/5/9, Sun/Moon 8th-only exempt), worked out by hand
LAGNA_AVOID = {
    'Aries': ['Mercury'], 'Taurus': ['Jupiter', 'Mars'], 'Gemini': ['Mars'], 'Cancer': ['Saturn', 'Mercury'],
    'Leo': ['Saturn', 'Moon'], 'Virgo': ['Mars', 'Sun'], 'Libra': ['Jupiter'], 'Scorpio': ['Mercury', 'Venus'],
    'Sagittarius': ['Venus'], 'Capricorn': ['Jupiter'], 'Aquarius': ['Moon'], 'Pisces': ['Sun', 'Venus', 'Saturn'],
}
LAGNA_LORD = {'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus',
              'Scorpio': 'Mars', 'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'}
# planet -> natural enemies (Parashari, BPHS ch.3); Moon, Rahu, Ketu none
ENEMY = {'Sun': ['Venus', 'Saturn'], 'Moon': [], 'Mars': ['Mercury'], 'Mercury': ['Moon'], 'Jupiter': ['Mercury', 'Venus'],
         'Venus': ['Sun', 'Moon'], 'Saturn': ['Sun', 'Moon', 'Mars'], 'Rahu': [], 'Ketu': []}

# ---- body-part table ---------------------------------------------------------------------------------------
bt = B.load_table()
assert sorted(bt) == list(range(1, 13)), 'must cover all 12 houses'                      # 12-houses-covered check
for h in range(1, 13):
    r = bt[h]
    assert r['natural_sign'] == SIGNS[h - 1], (h, r['natural_sign'])
    assert r['primary_part'] == PRIMARY[h - 1], (h, r['primary_part'])
    assert EXTENDED_SAMPLE[h] in r['extended_parts'], (h, r['extended_parts'])
    assert r['status'] == STATUS and r['basis']
assert len({r['primary_part'] for r in bt.values()}) == 12 and len({r['natural_sign'] for r in bt.values()}) == 12   # no repeats

# by house number / by sign
for h in range(1, 13):
    assert B.body_part_of_house(h)['primary'] == PRIMARY[h - 1]
    assert B.body_part_of_sign(SIGNS[h - 1])['primary'] == PRIMARY[h - 1]
    assert B.body_part_of_sign(h - 1)['primary'] == PRIMARY[h - 1]
assert B.body_part_of_sign('  leo ')['primary'] == 'stomach'
for bad in (0, 13, -1, True, 1.0, None, '1'):
    try: B.body_part_of_house(bad); raise SystemExit('house %r accepted' % (bad,))
    except ValueError: pass
for bad in (12, -1, True, 1.0, None, 'Aires'):
    try: B.body_part_of_sign(bad); raise SystemExit('sign %r accepted' % (bad,))
    except ValueError: pass
r1 = B.body_part_of_house(1); r1['extended'].append('x'); assert 'x' not in B.body_part_of_house(1)['extended']   # fresh copies

# chart function: whole-sign default, all 12 houses, every lagna
for li, lg in enumerate(SIGNS):
    ch = B.body_parts_for_chart(lg)
    assert sorted(ch['houses']) == list(range(1, 13)) and ch['lagna'] == lg and ch['status'] == STATUS
    for h in range(1, 13):
        hh = ch['houses'][h]
        assert hh['by_house_number']['primary'] == PRIMARY[h - 1]
        sg = SIGNS[(li + h - 1) % 12]
        assert [s['sign'] for s in hh['signs']] == [sg] and hh['signs'][0]['share'] == 1.0 and hh['signs'][0]['role'] == 'major'
        assert hh['signs'][0]['body_part']['primary'] == PRIMARY[SIGNS.index(sg)]
assert B.body_parts_for_chart(0)['houses'][1]['signs'][0]['sign'] == 'Aries'
# Leo lagna by hand: house 1 = Leo (stomach) but house-number reading says head
ch = B.body_parts_for_chart('Leo')
assert ch['houses'][1]['by_house_number']['primary'] == 'head' and ch['houses'][1]['signs'][0]['body_part']['primary'] == 'stomach'
assert ch['houses'][8]['signs'][0]['sign'] == 'Pisces' and ch['houses'][8]['signs'][0]['body_part']['primary'] == 'feet'

# multi-sign houses (MAIN PART): both major and minor signs reported
shares = {h: {'shares': {SIGNS[(4 + h - 1) % 12]: 1.0}} for h in range(1, 13)}
shares[1] = {'shares': {'Virgo': 0.3, 'Leo': 0.7}}
shares[2] = {'Libra': 0.5, 'Virgo': 0.5}            # plain {sign: share} shape, tie
ch = B.body_parts_for_chart('Leo', house_shares=shares)
s1 = ch['houses'][1]['signs']
assert [(s['sign'], s['role'], s['body_part']['primary']) for s in s1] == [('Leo', 'major', 'stomach'), ('Virgo', 'minor', 'waist')]
s2 = ch['houses'][2]['signs']
assert [(s['sign'], s['role']) for s in s2] == [('Virgo', 'major'), ('Libra', 'major')]   # tie keeps both major, zodiac order
assert ch['houses'][1]['by_house_number']['primary'] == 'head'
short = dict(shares); del short[5]
empty5 = dict(shares); del empty5[5]; empty5['5'] = {'shares': {}}
for bad in (short, empty5):
    try: B.body_parts_for_chart('Leo', house_shares=bad); raise SystemExit('bad house_shares accepted')
    except ValueError: pass
try: B.body_parts_for_chart('Nope'); raise SystemExit('bad lagna accepted')
except ValueError: pass

# loader rejects bad tables
tmp = tempfile.mkdtemp()
def write_body(rows, name='b.csv', header=None):
    p = os.path.join(tmp, name)
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(header or B.COLUMNS); w.writerows(rows)
    return p
good = [[h, SIGNS[h - 1], PRIMARY[h - 1], '[]', 'b', STATUS] for h in range(1, 13)]
assert len(B.load_table(write_body(good))) == 12
for label, rows, hdr in [('missing house', good[:11], None), ('dup house', good[:11] + [good[0]], None),
                         ('wrong sign', [good[0][:1] + ['Taurus'] + good[0][2:]] + good[1:], None),
                         ('empty part', good[:5] + [[6, 'Virgo', '', '[]', 'b', STATUS]] + good[6:], None), ('bad header', good, ['a'])]:
    try: B.load_table(write_body(rows, header=hdr)); raise SystemExit(label + ' accepted')
    except ValueError: pass

# ---- avoid-colours: lagna table ----------------------------------------------------------------------------
lt = A.load_lagna_table()
assert {r['lagna_sign'] for r in lt} == set(SIGNS), 'all 12 lagnas covered'
for lg in SIGNS:
    got = [r['avoid_planet'] for r in lt if r['lagna_sign'] == lg]
    assert got == LAGNA_AVOID[lg], (lg, got)
    for r in lt:
        if r['lagna_sign'] == lg:
            assert r['avoid_colour'] == COLOUR[r['avoid_planet']]
            assert r['status'] == STATUS and r['reason']
assert len(lt) == 19
for r in lt:   # houses lorded: re-derived by hand-free rule on zodiac: planet must lord a dusthana and none of 1/5/9
    li = SIGNS.index(r['lagna_sign'])
    lords = {h: ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter'][(li + h - 1) % 12] for h in range(1, 13)}
    mine = [h for h in range(1, 13) if lords[h] == r['avoid_planet']]
    assert r['houses_lorded'] == mine, r
    assert any(h in (6, 8, 12) for h in mine) and not any(h in (1, 5, 9) for h in mine)
# the derive function (rule) agrees with the hand table for every lagna, and applies the Sun/Moon 8th exception
for li, lg in enumerate(SIGNS):
    assert [p for p, _ in A.derive_lagna_avoid(li)] == LAGNA_AVOID[lg]
assert 'Moon' not in LAGNA_AVOID['Sagittarius'] and 'Sun' not in LAGNA_AVOID['Capricorn']   # Moon / Sun 8th-lord exception
assert 'Moon' in LAGNA_AVOID['Leo']                                                         # Moon 12th lord is not exempt

# ---- avoid-colours: planet table ---------------------------------------------------------------------------
pt = A.load_planet_table()
assert len(pt) == 11
for p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
    assert [r['enemy_planet'] for r in pt if r['planet'] == p] == ENEMY[p], p
for r in pt:
    assert r['avoid_colour'] == COLOUR[r['enemy_planet']] and r['status'] == STATUS
assert not [r for r in pt if r['planet'] in ('Rahu', 'Ketu')]
# colours agree with the owner's planet-colour table
for p, c in COLOUR.items():
    assert PC.BY_NAME[p] == c, (p, PC.BY_NAME[p])

# ---- engine functions --------------------------------------------------------------------------------------
for lg in SIGNS:
    res = A.avoid_colours_for_chart(lg)
    assert res['lagna'] == lg and res['lagna_lord'] == LAGNA_LORD[lg] and res['status'] == STATUS
    assert [x['planet'] for x in res['by_lagna']] == LAGNA_AVOID[lg]
    assert [x['enemy_planet'] for x in res['by_lagna_lord_enemies']] == ENEMY[LAGNA_LORD[lg]]
    want = sorted({COLOUR[p] for p in LAGNA_AVOID[lg]} | {COLOUR[p] for p in ENEMY[LAGNA_LORD[lg]]})
    assert res['avoid_colours'] == want, (lg, res['avoid_colours'], want)
res = A.avoid_colours_for_chart('pisces')                      # by hand: Sun/Venus/Saturn + lord Jupiter's enemies Mercury, Venus
assert res['avoid_colours'] == ['Black', 'Green', 'Off white', 'Orange']
assert A.avoid_colours_for_chart(0)['avoid_colours'] == ['Green']          # Aries: Mercury (lagna table), lord Mars enemy Mercury -> Green
assert A.avoid_colours_for_chart('Leo')['avoid_colours'] == ['Black', 'Off white', 'White']   # Saturn, Moon + Sun's enemies Venus, Saturn
for p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
    assert [x['enemy_planet'] for x in A.avoid_colours_for_planet(p)] == ENEMY[p], p
assert [x['colour'] for x in A.avoid_colours_for_planet('  saturn')] == ['Orange', 'White', 'Red']
for bad in ('Pluto', 'Lagna', None, 3):
    try: A.avoid_colours_for_planet(bad); raise SystemExit('planet %r accepted' % (bad,))
    except ValueError: pass
for bad in (12, -1, True, 1.5, None, 'Aires'):
    try: A.avoid_colours_for_chart(bad); raise SystemExit('lagna %r accepted' % (bad,))
    except ValueError: pass
a = A.avoid_colours_for_chart('Aries'); a['by_lagna'][0]['houses_lorded'].append(99)
assert 99 not in A.avoid_colours_for_chart('Aries')['by_lagna'][0]['houses_lorded']    # fresh copies

# loader rejects bad lagna / planet tables
def write_csv(cols, rows, name):
    p = os.path.join(tmp, name)
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(cols); w.writerows(rows)
    return p
base = [[r['lagna_sign'], r['avoid_planet'], r['avoid_colour'], json.dumps(r['houses_lorded']), r['reason'], r['status']] for r in lt]
assert len(A.load_lagna_table(write_csv(A.LAGNA_COLUMNS, base, 'l.csv'))) == 19
for label, rows in [('missing lagna', [r for r in base if r[0] != 'Leo']), ('duplicate', base + [base[0]]),
                    ('bad sign', [['Aires'] + base[0][1:]] + base[1:]), ('empty colour', [base[0][:2] + [''] + base[0][3:]] + base[1:])]:
    try: A.load_lagna_table(write_csv(A.LAGNA_COLUMNS, rows, 'l2.csv')); raise SystemExit(label + ' accepted')
    except ValueError: pass
pbase = [[r['planet'], r['enemy_planet'], r['avoid_colour'], r['reason'], r['status']] for r in pt]
assert len(A.load_planet_table(write_csv(A.PLANET_COLUMNS, pbase, 'p.csv'))) == 11
for label, rows in [('duplicate', pbase + [pbase[0]]), ('bad planet', [['Pluto'] + pbase[0][1:]] + pbase[1:]), ('empty colour', [pbase[0][:2] + [''] + pbase[0][3:]] + pbase[1:])]:
    try: A.load_planet_table(write_csv(A.PLANET_COLUMNS, rows, 'p2.csv')); raise SystemExit(label + ' accepted')
    except ValueError: pass
try: A.load_planet_table(write_csv(['a'], [], 'p3.csv')); raise SystemExit('bad header accepted')
except ValueError: pass

# ---- migrations 0002 + 0003 on in-memory sqlite (never a live database) -----------------------------------
conn = sqlite3.connect(':memory:')
for f in ('0002_body_parts_avoid_colours_schema.sql', '0003_body_parts_avoid_colours_seed.sql'):
    conn.executescript(open(os.path.join(ROOT, 'migrations', f), encoding='utf-8').read())
n = lambda t: conn.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0]
assert (n('ref_house_body_part'), n('ref_lagna_avoid_colour'), n('ref_planet_avoid_colour')) == (12, 19, 11)
assert conn.execute('SELECT COUNT(DISTINCT lagna_no) FROM ref_lagna_avoid_colour').fetchone()[0] == 12
assert conn.execute("SELECT COUNT(*) FROM (SELECT status FROM ref_house_body_part UNION ALL SELECT status FROM ref_lagna_avoid_colour UNION ALL SELECT status FROM ref_planet_avoid_colour) WHERE status != ?", (STATUS,)).fetchone()[0] == 0
# DB read path == CSV read path, for the tables and for the engine functions
assert B.load_table(conn=conn) == bt
assert A.load_lagna_table(conn=conn) == lt and A.load_planet_table(conn=conn) == pt
for lg in SIGNS:
    assert B.body_parts_for_chart(lg, table=B.load_table(conn=conn)) == B.body_parts_for_chart(lg)
    assert A.avoid_colours_for_chart(lg, A.load_lagna_table(conn=conn), A.load_planet_table(conn=conn)) == A.avoid_colours_for_chart(lg)
# seed twice is safe (INSERT OR REPLACE) and schema twice is safe (IF NOT EXISTS)
conn.executescript(open(os.path.join(ROOT, 'migrations', '0003_body_parts_avoid_colours_seed.sql'), encoding='utf-8').read())
conn.executescript(open(os.path.join(ROOT, 'migrations', '0002_body_parts_avoid_colours_schema.sql'), encoding='utf-8').read())
assert (n('ref_house_body_part'), n('ref_lagna_avoid_colour'), n('ref_planet_avoid_colour')) == (12, 19, 11)
# schema constraints hold
for sql in ("INSERT INTO ref_house_body_part VALUES (13,'X','x','[]','b','s')", "INSERT INTO ref_house_body_part VALUES (1,'Dup','x','[]','b','s')",
            "INSERT INTO ref_planet_avoid_colour VALUES (7,'X',0,'Sun','c','r','s')"):
    try: conn.execute(sql); raise SystemExit('constraint missed: ' + sql)
    except sqlite3.IntegrityError: pass
# the seed file is exactly what the generator builds from the CSVs; a hand edit would be caught
assert subprocess.call([sys.executable, os.path.join(ROOT, 'tune', 'build_seed_sql.py'), '--check']) == 0, 'seed SQL out of date: run tune/build_seed_sql.py'
# no birth data / personal names in the new files
for f in ('data/house_body_parts.csv', 'data/lagna_avoid_colours.csv', 'data/planet_avoid_colours.csv', 'migrations/0002_body_parts_avoid_colours_schema.sql', 'migrations/0003_body_parts_avoid_colours_seed.sql'):
    t = open(os.path.join(ROOT, f), encoding='utf-8').read().lower()
    for w in ('rajat', 'pallavi', 'eshani', 'pehu', '@gmail'):
        assert w not in t, (f, w)
shutil.rmtree(tmp)
print('test_body_parts_avoid_colours ok')
