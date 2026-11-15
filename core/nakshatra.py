"""Nakshatra identity table and per-person nakshatra signals (docs/NAKSHATRA_METHOD.md steps 1, 4, 6).
Plain code, no AI. Table values are the common textbook ones; tune/nak_facts_check.py compares them with the book facts and lists disagreements.
Signals are tradition claims, unmeasured."""
NAMES = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishta','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati']
LORDS = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']          # Vimshottari order, repeats 3 times
PLN = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']
GANA_DEVA = {1,5,7,8,13,15,17,22,27}; GANA_RAK = {3,9,10,14,16,18,19,23,24}
YONI = ['Horse','Elephant','Sheep','Serpent','Serpent','Dog','Cat','Sheep','Cat','Rat','Rat','Cow','Buffalo','Tiger','Buffalo','Tiger','Deer','Deer','Dog','Monkey','Mongoose','Monkey','Lion','Horse','Lion','Cow','Elephant']
NADI_ADI = {1,6,7,12,13,18,19,24,25}; NADI_MADHYA = {2,5,8,11,14,17,20,23,26}
TARA = {1: ('Janma', 'mixed'), 2: ('Sampat', 'good'), 3: ('Vipat', 'bad'), 4: ('Kshema', 'good'), 5: ('Pratyari', 'bad'), 6: ('Sadhaka', 'good'), 7: ('Vadha', 'bad'), 8: ('Mitra', 'good'), 9: ('Parama Mitra', 'good')}
CHANDRA_GOOD = {1, 3, 6, 7, 10, 11}
def ident(n):
    """n = 1..27 -> dict of table facts."""
    g = 'Deva' if n in GANA_DEVA else 'Rakshasa' if n in GANA_RAK else 'Manushya'
    nd = 'Adi' if n in NADI_ADI else 'Madhya' if n in NADI_MADHYA else 'Antya'
    return {'n': n, 'name': NAMES[n - 1], 'lord': LORDS[(n - 1) % 9], 'gana': g, 'yoni': YONI[n - 1], 'nadi': nd}
def of_lon(lon):
    """sidereal longitude -> (nakshatra 1..27, pada 1..4)"""
    lon %= 360; u = 360 / 27; n = int(lon // u); p = int((lon - n * u) // (u / 4)) + 1
    return n + 1, min(p, 4)
def natal_signals(rep):
    """Per-person natal nakshatra facts from the D1 report."""
    d1 = rep['chart']['divisional']['D1']; out = {'planets': {}}
    for i, p in enumerate(PLN):
        e = d1[p]; n, pd = of_lon(e['sign0'] * 30 + e['deg']); out['planets'][p] = {**ident(n), 'pada': pd, 'sign0': e['sign0']}
    lg = d1['Lagna']; n, pd = of_lon(lg['sign0'] * 30 + lg['deg']); out['lagna'] = {**ident(n), 'pada': pd}
    jn = out['planets']['Moon']['n']; out['janma'] = out['planets']['Moon']
    out['anu_janma'] = ident((jn - 1 + 9) % 27 + 1); out['trijanma'] = ident((jn - 1 + 18) % 27 + 1)
    out['taras'] = {t: [NAMES[(jn - 1 + (t - 1) + 9 * k) % 27] for k in range(3)] for t in range(1, 10)}
    return out
def day_signals(natal_moon_nak, natal_moon_sign0, day_moon_nak, day_moon_sign0, dasha_lord_nak=None):
    """Per-day signals: tara bala and chandra bala of the day's Moon (GR-D tara rules already use tara; this keeps the numbers for the engine JSON)."""
    count = (day_moon_nak - natal_moon_nak) % 27 + 1; t = count % 9 or 9
    h = (day_moon_sign0 - natal_moon_sign0) % 12 + 1
    s = {'tara_no': t, 'tara': TARA[t][0], 'tara_nature': TARA[t][1], 'day_nak': NAMES[day_moon_nak - 1], 'moon_house_from_natal_moon': h,
         'chandra_bala': 'good' if h in CHANDRA_GOOD else 'weak', 'janma_day': count == 1, 'anu_janma_day': count == 10, 'trijanma_day': count == 19}
    if dasha_lord_nak: s['day_nak_lord_is_dasha_lord'] = LORDS[(day_moon_nak - 1) % 9] == dasha_lord_nak
    return s
