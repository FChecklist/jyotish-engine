# Changelog
Owner rule: every change bumps the version and updates this file, version.json and the knowledge doc in the same PR. Versions: MAJOR.MINOR.PATCH.

## 0.1.0 - 2026-11-21
- First tracked version (CHANGELOG.md and version.json created).
- Added owner table of planet-in-sign and planet-aspect negatives with colour remedies: `data/planet_sign_negatives.csv` (13 rows).
- Added `core/planet_negatives.py`: flags a planet negative by placement or by its listed aspects, returns remedy colours (single or combination) for body, house, office.
- Added `tests/test_planet_negatives.py` (all 13 rules x 12 signs, every aspect case, no-false-positive, input handling, loader checks) and wired it into `tests/run_all.sh`.
- Knowledge doc: `docs/PLANET_SIGN_NEGATIVES.md` (table, readings chosen, questions for the owner).
