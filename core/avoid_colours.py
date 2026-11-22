"""Avoid-colours tables and engine functions. Tradition claim, not a measured fact. Spec: docs/BODY_PARTS_AVOID_COLOURS.md.
Colours are the owner's planet-colour table (core/planet_colors.py). Nothing here is measured; every row is `DEFAULT, owner to confirm`.

Two tables (data/*.csv, also in D1 as ref_lagna_avoid_colour / ref_planet_avoid_colour, see migrations/0002 and 0003):
- LAGNA table: for each of the 12 lagnas, the planets that are functional malefics, and the colour of each planet to avoid.
  Rule (classical Parashari default): a planet is a functional malefic for a lagna if it lords the 6th, 8th or 12th house
  AND does not lord the 1st, 5th or 9th (lagna and trikona lords are kept clear). Exception: Sun or Moon whose only dusthana
  lordship is the 8th is not counted (BPHS 8th-lord exception). Rahu and Ketu own no sign, so they are not in this table.
- PLANET table: for each planet, the colours of its natural enemies (Parashari natural enmity, same table as core/dignity.py).
  Use: colours to avoid when you are strengthening that planet (for example the lagna lord's colour).
  Moon has no natural enemies; Rahu and Ketu are not given enemies (schools differ, same as core/dignity.py), so they have no rows."""
import csv
import json
import os
import sqlite3
from zodiac import SIGNS, SIGN_LORD
from dignity import ENEMIES

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
LAGNA_CSV = os.path.join(DATA_DIR, 'lagna_avoid_colours.csv')
PLANET_CSV = os.path.join(DATA_DIR, 'planet_avoid_colours.csv')
LAGNA_COLUMNS = ['lagna_sign', 'avoid_planet', 'avoid_colour', 'houses_lorded', 'reason', 'status']
PLANET_COLUMNS = ['planet', 'enemy_planet', 'avoid_colour', 'reason', 'status']
STATUS = 'DEFAULT, owner to confirm'
PNAME = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']   # engine ids 0..6 (same order as core/dignity.py)
DUSTHANA = (6, 8, 12)
TRIKONA = (1, 5, 9)


def derive_lagna_avoid(lagna_index):
    """The classical-default rule above, computed. Returns [(planet, [houses it lords])] in planet order of first appearance (house 6, 8, 12)."""
    lords = {}   # planet -> houses lorded
    for h in range(1, 13):
        lords.setdefault(SIGN_LORD[(lagna_index + h - 1) % 12], []).append(h)
    out = []
    for h in DUSTHANA:
        p = SIGN_LORD[(lagna_index + h - 1) % 12]
        if any(x[0] == p for x in out):
            continue
        houses = lords[p]
        if any(t in houses for t in TRIKONA):
            continue
        if p in ('Sun', 'Moon') and [d for d in houses if d in DUSTHANA] == [8]:
            continue
        out.append((p, houses))
    return out


def _decode(r, cols):
    for c in cols:
        r[c] = json.loads(r[c])
    return r


def _read_csv(path, columns, json_cols=()):
    with open(path, newline='', encoding='utf-8') as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != columns:
            raise ValueError('%s columns are %r, expected %r' % (os.path.basename(path), rd.fieldnames, columns))
        return [_decode(r, json_cols) for r in rd]


def load_lagna_table(path=None, conn=None):
    """Rows {lagna_sign, avoid_planet, avoid_colour, houses_lorded, reason, status}. conn = sqlite3/D1-export connection, else the CSV."""
    if conn is not None:
        cur = conn.execute('SELECT lagna_sign, avoid_planet, avoid_colour, houses_lorded, reason, status FROM ref_lagna_avoid_colour ORDER BY lagna_no, avoid_order')
        rows = [dict(zip(LAGNA_COLUMNS, r)) for r in cur.fetchall()]
        rows = [_decode(r, ('houses_lorded',)) for r in rows]
    else:
        rows = _read_csv(path or LAGNA_CSV, LAGNA_COLUMNS, ('houses_lorded',))
    seen = set()
    for r in rows:
        if r['lagna_sign'] not in SIGNS:
            raise ValueError('bad lagna_sign %r' % r['lagna_sign'])
        if (r['lagna_sign'], r['avoid_planet']) in seen:
            raise ValueError('duplicate lagna row %r' % ((r['lagna_sign'], r['avoid_planet']),))
        seen.add((r['lagna_sign'], r['avoid_planet']))
        if not r['avoid_colour']:
            raise ValueError('empty avoid_colour for %r' % ((r['lagna_sign'], r['avoid_planet']),))
    missing = [s for s in SIGNS if s not in {r['lagna_sign'] for r in rows}]
    if missing:
        raise ValueError('lagna table does not cover %r' % missing)
    return rows


def load_planet_table(path=None, conn=None):
    if conn is not None:
        cur = conn.execute('SELECT planet, enemy_planet, avoid_colour, reason, status FROM ref_planet_avoid_colour ORDER BY planet_no, enemy_no')
        rows = [dict(zip(PLANET_COLUMNS, r)) for r in cur.fetchall()]
    else:
        rows = _read_csv(path or PLANET_CSV, PLANET_COLUMNS)
    seen = set()
    for r in rows:
        if r['planet'] not in PNAME or r['enemy_planet'] not in PNAME:
            raise ValueError('bad planet in %r' % (r,))
        if (r['planet'], r['enemy_planet']) in seen:
            raise ValueError('duplicate planet row %r' % ((r['planet'], r['enemy_planet']),))
        seen.add((r['planet'], r['enemy_planet']))
        if not r['avoid_colour']:
            raise ValueError('empty avoid_colour for %r' % (r,))
    return rows


def _lagna_index(lagna):
    if isinstance(lagna, bool):
        raise ValueError('bad lagna %r' % (lagna,))
    if isinstance(lagna, int):
        if 0 <= lagna <= 11:
            return lagna
        raise ValueError('lagna index %r outside 0..11' % (lagna,))
    if isinstance(lagna, str) and lagna.strip().capitalize() in SIGNS:
        return SIGNS.index(lagna.strip().capitalize())
    raise ValueError('unknown lagna %r' % (lagna,))


def avoid_colours_for_chart(lagna, lagna_table=None, planet_table=None):
    """lagna = sign name or index 0..11 (0 = Aries). Returns
    {'lagna', 'lagna_lord', 'by_lagna': [{planet, colour, houses_lorded, reason}], 'by_lagna_lord_enemies': [{enemy_planet, colour, reason}],
     'avoid_colours': sorted unique colour list from both, 'status': DEFAULT note}.
    Both lists are returned side by side; the engine does not rank or merge them. Not wired into the daily 3 DO + 3 DONT (owner decision pending)."""
    s0 = _lagna_index(lagna)
    sign = SIGNS[s0]
    lt = load_lagna_table() if lagna_table is None else lagna_table
    pt = load_planet_table() if planet_table is None else planet_table
    lord = SIGN_LORD[s0]
    by_lagna = [{'planet': r['avoid_planet'], 'colour': r['avoid_colour'], 'houses_lorded': list(r['houses_lorded']), 'reason': r['reason']}
                for r in lt if r['lagna_sign'] == sign]
    by_lord = [{'enemy_planet': r['enemy_planet'], 'colour': r['avoid_colour'], 'reason': r['reason']} for r in pt if r['planet'] == lord]
    colours = sorted({x['colour'] for x in by_lagna} | {x['colour'] for x in by_lord})
    return {'lagna': sign, 'lagna_lord': lord, 'by_lagna': by_lagna, 'by_lagna_lord_enemies': by_lord, 'avoid_colours': colours, 'status': STATUS}


def avoid_colours_for_planet(planet, planet_table=None):
    """Colours of the natural enemies of `planet` (a classical 7-planet name). Empty list for Moon, Rahu, Ketu."""
    if not isinstance(planet, str) or planet.strip().capitalize() not in PNAME + ['Rahu', 'Ketu']:
        raise ValueError('unknown planet %r' % (planet,))
    p = planet.strip().capitalize()
    pt = load_planet_table() if planet_table is None else planet_table
    return [{'enemy_planet': r['enemy_planet'], 'colour': r['avoid_colour'], 'reason': r['reason']} for r in pt if r['planet'] == p]
