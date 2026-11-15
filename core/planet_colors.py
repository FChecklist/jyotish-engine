"""Planet -> colour table. SOURCE: image supplied by Rajat on 2026-11-15 (12 rows, Hindi/English). A tradition claim, not a measured fact.
Planets 0..8 use the engine ids (Sun 0 .. Ketu 8); Uranus, Neptune, Pluto are listed in the source but the engine does not compute them (outer planets, not in Vimshottari/Lahiri charts)."""
PLANET_COLORS = [
    # (no, engine_id, name, hindi, colour_en, colour_hi, note)
    (1, 0, 'Sun', 'Surya', 'Orange', 'Kesariya', ''),
    (2, 1, 'Moon', 'Chandra', 'White', 'Safed', ''),
    (3, 2, 'Mars', 'Mangal', 'Red', 'Laal', ''),
    (4, 3, 'Mercury', 'Budh', 'Green', 'Hara', ''),
    (5, 4, 'Jupiter', 'Guru', 'Yellow', 'Peela', ''),
    (6, 5, 'Venus', 'Shukra', 'Off white', 'Off white (cream / milky white)', 'cream / milky white'),
    (7, 6, 'Saturn', 'Shani', 'Black', 'Kaala', ''),
    (8, 7, 'Rahu', 'Rahu', 'Blue', 'Neela', ''),
    (9, 8, 'Ketu', 'Ketu', 'Gray', 'Bhura', ''),
    (10, None, 'Uranus', 'Indra', 'Opal white', 'Opal white', 'lightening colour'),
    (11, None, 'Neptune', 'Varun', 'Ocean colour', 'Aqua-marine', ''),
    (12, None, 'Pluto', 'Yum', 'Dark black', 'Gehra kaala', ''),
]
BY_ENGINE_ID = {r[1]: r[4] for r in PLANET_COLORS if r[1] is not None}
BY_NAME = {r[2]: r[4] for r in PLANET_COLORS}
