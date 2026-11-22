"""House / sign -> body part table (Kalapurusha, the natural zodiac as a body) and engine function. Tradition claim, not a measured fact.
Spec: docs/BODY_PARTS_AVOID_COLOURS.md. Table: data/house_body_parts.csv, also in D1 as ref_house_body_part (migrations/0002 and 0003).
No medical diagnosis: this only says which body area a house or sign is traditionally linked to (CLAUDE.md: no medical diagnoses).

Two readings are returned side by side, never merged:
- BY HOUSE NUMBER (house n = n-th limb): house 1 = head ... house 12 = feet, whatever sign sits there.
- BY SIGN (sign = its natural limb): Aries = head ... Pisces = feet, for every sign that touches the house.
MAIN PART (CLAUDE.md): a house is touched by 2+ signs. If house shares are given (core/influence.house_sign_shares), every sign
gets its body part and its share; the largest share is 'major', the rest 'minor', and both are reported."""
import csv
import json
import os
from zodiac import SIGNS, sign_at_house

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'house_body_parts.csv')
COLUMNS = ['house_no', 'natural_sign', 'primary_part', 'extended_parts', 'basis', 'status']
STATUS = 'DEFAULT, owner to confirm'


def load_table(path=None, conn=None):
    """12 rows keyed by house_no 1..12. conn = sqlite3 connection holding ref_house_body_part, else the CSV."""
    if conn is not None:
        cur = conn.execute('SELECT house_no, natural_sign, primary_part, extended_parts, basis, status FROM ref_house_body_part ORDER BY house_no')
        rows = [dict(zip(COLUMNS, r)) for r in cur.fetchall()]
    else:
        with open(path or DATA_PATH, newline='', encoding='utf-8') as f:
            rd = csv.DictReader(f)
            if rd.fieldnames != COLUMNS:
                raise ValueError('house_body_parts columns are %r, expected %r' % (rd.fieldnames, COLUMNS))
            rows = list(rd)
    out = {}
    for r in rows:
        r['house_no'] = int(r['house_no'])
        r['extended_parts'] = json.loads(r['extended_parts']) if isinstance(r['extended_parts'], str) else list(r['extended_parts'])
        h = r['house_no']
        if not 1 <= h <= 12 or h in out:
            raise ValueError('bad or duplicate house_no %r' % h)
        if r['natural_sign'] != SIGNS[h - 1]:
            raise ValueError('house %d natural_sign must be %s, got %r' % (h, SIGNS[h - 1], r['natural_sign']))
        if not r['primary_part']:
            raise ValueError('house %d has no primary_part' % h)
        out[h] = r
    if sorted(out) != list(range(1, 13)):
        raise ValueError('body part table must cover all 12 houses, has %r' % sorted(out))
    return out


def _sign_index(sign):
    if isinstance(sign, bool):
        raise ValueError('bad sign %r' % (sign,))
    if isinstance(sign, int):
        if 0 <= sign <= 11:
            return sign
        raise ValueError('sign index %r outside 0..11' % (sign,))
    if isinstance(sign, str) and sign.strip().capitalize() in SIGNS:
        return SIGNS.index(sign.strip().capitalize())
    raise ValueError('unknown sign %r' % (sign,))


def _part(row):
    return {'primary': row['primary_part'], 'extended': list(row['extended_parts'])}


def body_part_of_sign(sign, table=None):
    t = load_table() if table is None else table
    return _part(t[_sign_index(sign) + 1])


def body_part_of_house(house, table=None):
    if isinstance(house, bool) or not isinstance(house, int) or not 1 <= house <= 12:
        raise ValueError('house must be an int 1..12, got %r' % (house,))
    t = load_table() if table is None else table
    return _part(t[house])


def body_parts_for_chart(lagna, house_shares=None, table=None):
    """lagna = sign name or index (0 = Aries). house_shares = optional {house: {sign: share}} or {house: {'shares': {sign: share}}}
    (the shape core/influence.house_sign_shares returns). Without it, each house holds its one whole-sign sign (share 1.0).
    Returns {'lagna', 'status', 'houses': {1..12: {'by_house_number': {...}, 'signs': [{'sign','share','role','body_part': {...}}]}}}."""
    s0 = _sign_index(lagna)
    t = load_table() if table is None else table
    out = {'lagna': SIGNS[s0], 'status': STATUS, 'houses': {}}
    for h in range(1, 13):
        if house_shares is None:
            shares = {SIGNS[sign_at_house(s0, h)]: 1.0}
        else:
            raw = house_shares.get(h, house_shares.get(str(h)))
            if raw is None:
                raise ValueError('house_shares has no house %d' % h)
            shares = raw.get('shares', raw) if isinstance(raw, dict) else None
            if not shares:
                raise ValueError('house %d has no sign shares' % h)
        top = max(shares.values())
        signs = []
        for sg, sh in sorted(shares.items(), key=lambda kv: (-kv[1], _sign_index(kv[0]))):
            signs.append({'sign': SIGNS[_sign_index(sg)], 'share': sh, 'role': 'major' if sh == top else 'minor',
                          'body_part': _part(t[_sign_index(sg) + 1])})
        out['houses'][h] = {'by_house_number': _part(t[h]), 'signs': signs}
    return out
