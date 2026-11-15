"""Numerology 'energies' (Rajat's list, image of 2026-11-15): DOB, month of birth, sum of DOB, name, house no., self age, year no., vehicle no., office no.,
student roll no., exam date. Each item is a number reduced to 1-9 (11/22/33 kept as master flag). The image gives the list only, NOT what each number means,
so this module computes the numbers and links each to a planet; meaning is decided by the chart (see colour.score), never by this table alone.
HYPOTHESES (schools differ, to be confirmed by Rajat): number->planet (Indian/Vedic numerology: 1 Sun 2 Moon 3 Jupiter 4 Rahu 5 Mercury 6 Venus 7 Ketu 8 Saturn 9 Mars);
letters use the Chaldean table (no 9 assigned to a letter); self age = completed years; year no. = digits of the calendar year."""
import datetime
NUM_PLANET = {1: 0, 2: 1, 3: 4, 4: 7, 5: 3, 6: 5, 7: 8, 8: 6, 9: 2}          # engine planet ids (Sun 0 .. Ketu 8)
CHALDEAN = {c: n for n, cs in {1: 'AIJQY', 2: 'BKR', 3: 'CGLS', 4: 'DMT', 5: 'EHNX', 6: 'UVW', 7: 'OZ', 8: 'FP'}.items() for c in cs}
def digits_sum(x):
    return sum(int(ch) for ch in str(x) if ch.isdigit()) + sum(CHALDEAN.get(ch, 0) for ch in str(x).upper() if ch.isalpha())
def reduce(n):
    """-> (single digit 1-9, master flag). 0 stays 0 (nothing to reduce)."""
    master = n in (11, 22, 33)
    while n > 9: n = sum(int(c) for c in str(n))
    return n, master
def energy(x):
    s = digits_sum(x); r, m = reduce(s); return {'input': str(x), 'raw_sum': s, 'number': r, 'master': m, 'planet': NUM_PLANET.get(r)}
def energies(dob, today, name=None, house=None, vehicle=None, office=None, roll=None, exam_date=None):
    """dob, today, exam_date: datetime.date. Items without input are None (never invented)."""
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    out = {'dob': energy(dob.day), 'month_of_birth': energy(dob.month), 'sum_of_dob': energy(f'{dob.day}{dob.month}{dob.year}'),
           'self_age': energy(age), 'year_no': energy(today.year), 'personal_year': energy(f'{dob.day}{dob.month}{today.year}')}
    for k, v in (('name', name), ('house_no', house), ('vehicle_no', vehicle), ('office_no', office), ('roll_no', roll)): out[k] = energy(v) if v not in (None, '') else None
    out['exam_date'] = energy(f'{exam_date.day}{exam_date.month}{exam_date.year}') if exam_date else None
    return out
