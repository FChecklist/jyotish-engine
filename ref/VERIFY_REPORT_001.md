# Verification report 001 (2026-11-14): our engine vs PyJHora 5.0.0 (open-source Python port of Jagannatha Hora; Lahiri)
Method: same inputs (date, local time, explicit UTC offset, lat, lon) given to both; positions, ascendant, D9 signs compared. Offsets given explicitly, so time-zone HISTORY is NOT tested here.
Charts: Delhi 1990, Quito 1975, Sydney 1985, Delhi 1947, Yorba Linda 1913, Ulm 1879 (LMT). Polar chart (Tromso) crashed our old engine (see bug 1).
Results
- Ascendant: identical to 0.0 arc-seconds in 5 of 6; 5.9" in the 1879 chart.
- Planets (Sun to Saturn): all within 51 arc-seconds. Cause found: PyJHora asks Swiss Ephemeris for TRUE (geometric) positions (flag TRUEPOS); our engine uses the standard apparent positions. Reproduced exactly: Sun 60.27625 (apparent) vs 60.28185 (geometric = PyJHora value).
- Rahu/Ketu: differ by 0.7 to 1.6 degrees. Cause: PyJHora default is TRUE node; our engine uses MEAN node. Not an error, a setting.
- D9 sign: 54 of 54 non-node placements agree; the only mismatches are Rahu and Ketu (node setting), in 2 of 6 charts.
Decisions needed from owner: (a) planet positions: apparent (current) or geometric (PyJHora style), (b) node: mean or true as default. Until answered both are kept.
Bugs found
1. Old engine (engine/jyotish.py Chart) crashes at latitude above about 66 degrees (Placidus houses undefined). New core/houses.py refuses explicitly instead. Old engine to be retired or patched with an explicit refusal.
Not yet verified: dasha dates, divisional charts beyond D9, KP sub lords, panchang, transit, Ashtakavarga, time-zone history, JHora desktop itself.
