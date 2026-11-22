# House-to-body-part table and avoid-colours tables (KNOWLEDGE doc)

Version: 0.2.0 (see CHANGELOG.md, version.json). Owner order: P1 checklist points 44-46. Every row is a tradition claim, not a measured fact. No accuracy is claimed. No medical diagnosis: the body-part table only says which body area a house or sign is traditionally linked to.

## Status of every choice
The owner's notes (Q1-Q5 in docs/PLANET_SIGN_NEGATIVES.md, PR #1 description) do not decide anything in this change. The owner did not supply either table's content in the repo. So every row below is `DEFAULT, owner to confirm` (the same words are in the `status` column of every row, in the CSVs and in D1).
No source book text was available when these were written; the tables were entered from the standard classical rules as the author knows them. The auditors and the owner must check them against the books.

## Files
- Data (source of truth): `data/house_body_parts.csv` (12 rows), `data/lagna_avoid_colours.csv` (19 rows, all 12 lagnas), `data/planet_avoid_colours.csv` (11 rows).
- Code: `core/body_parts.py`, `core/avoid_colours.py` (plain if/then, no AI, no chart maths; they only read signs).
- Database: `migrations/0002_body_parts_avoid_colours_schema.sql` (3 tables: ref_house_body_part, ref_lagna_avoid_colour, ref_planet_avoid_colour) and `migrations/0003_body_parts_avoid_colours_seed.sql` (generated from the CSVs by `tune/build_seed_sql.py`; do not edit by hand). Numbered 0002 and 0003 because PR #2 owns `0001_verified_charts.sql`. NOT applied to any live database (D1 `jyotish-rules` has no such tables yet).
- Tests: `tests/test_body_parts_avoid_colours.py` (in `tests/run_all.sh`).

## 1. House to body part (Kalapurusha)
The zodiac is read as a body: house 1 / Aries is the head, then down to house 12 / Pisces, the feet.
| House | Natural sign | Primary part (classical limb) | Extended (common organ list) |
|---|---|---|---|
| 1 | Aries | head | brain, skull, forehead |
| 2 | Taurus | face | neck, throat, mouth, teeth, tongue |
| 3 | Gemini | chest | shoulders, arms, hands, lungs, collarbone |
| 4 | Cancer | heart | breast, upper stomach, ribs |
| 5 | Leo | stomach | upper abdomen, spine, upper back |
| 6 | Virgo | waist | intestines, digestive tract, lower abdomen |
| 7 | Libra | lower abdomen | kidneys, bladder, lumbar region |
| 8 | Scorpio | private parts | reproductive organs, anus, excretory system |
| 9 | Sagittarius | thighs | hips, hip joints |
| 10 | Capricorn | knees | joints, bones |
| 11 | Aquarius | calves | shins, ankles, blood circulation in legs |
| 12 | Pisces | feet | toes, soles |

How the engine uses it (`body_parts.body_parts_for_chart(lagna, house_shares=None)`):
- Two readings, returned side by side, never merged: by house number (house n = n-th limb) and by sign (each sign that sits in the house gives its own limb).
- MAIN PART: if the caller passes house shares (`core/influence.house_sign_shares`), every sign in the house is reported with its share. The largest share is `major`, the others `minor`; a tie keeps both `major`. Without shares, the house holds its one whole-sign sign (share 1.0).
- Other functions: `body_part_of_house(n)`, `body_part_of_sign(sign)`, `load_table(conn=...)` (reads D1/sqlite instead of the CSV).

## 2. Avoid colours
Colours come from the owner's planet-colour table (`core/planet_colors.py`): Sun Orange, Moon White, Mars Red, Mercury Green, Jupiter Yellow, Venus Off white, Saturn Black.
- Lagna table (`lagna_avoid_colours`): for each of the 12 lagnas, the colour of each functional malefic planet. Rule: the planet lords the 6th, 8th or 12th house and does not lord the 1st, 5th or 9th. Exception: Sun or Moon whose only dusthana house is the 8th is not counted. Rahu and Ketu own no sign, so they are not in this table.
- Planet table (`planet_avoid_colours`): for each planet, the colours of its natural enemies (same enmity table as `core/dignity.py`: Sun - Venus, Saturn; Mars - Mercury; Mercury - Moon; Jupiter - Mercury, Venus; Venus - Sun, Moon; Saturn - Sun, Moon, Mars). Moon, Rahu and Ketu have no rows.
- `avoid_colours.avoid_colours_for_chart(lagna)` returns the lagna list, the lagna lord's enemy colours, and the combined sorted colour list. `avoid_colours_for_planet(planet)` returns one planet's enemy colours. Neither is ranked or merged with the owner's remedy colours (`planet_negatives`).
- Not wired into the daily 3 DO + 3 DONT (output shape is the owner's decision; same as Q4 in PLANET_SIGN_NEGATIVES.md). Existing `core/colour.py` already avoids a colour by chart score; the two are not combined.

## DEFAULT, owner to confirm (list)
1. Body parts: the primary column follows the classical Parashari limb list (head, face, chest, heart, stomach, waist, lower abdomen, private parts, thighs, knees, calves, feet). Some modern books move heart to Leo and chest/stomach to Cancer; the extended column is the common organ list and mixes both. Confirm the primary list and the extended list.
2. Body parts: the house-number reading and the sign reading are both returned. No rule picks one. Confirm if one should win.
3. Body parts: right/left side (for example right and left eye for houses 2 and 12) is not included.
4. Body parts: if shares are given, "major" = largest share, "minor" = the rest. The owner has not set a cut-off.
5. Avoid colours: "avoid colour of a planet" = that planet's own colour from the owner's table. The repo notes (DECISIONS 2026-11-15) record a school conflict: some schools wear a weak planet's colour, others avoid it. This table follows "avoid the colour of a functional malefic".
6. Avoid colours, lagna table: functional malefic = lord of 6, 8 or 12, not lord of 1, 5 or 9; Sun/Moon 8th-lord exception. Lords of 3 and 11 are not counted; kendra lordship does not cancel. Rahu/Ketu left out of this table.
7. Avoid colours, planet table: natural enemies (BPHS) only, no temporary or compound friendship. Rahu and Ketu get no enemies (schools differ).
8. Avoid colours: the lagna lord's enemy colours are reported in addition to the functional-malefic colours; the combined list is the union. Nothing is ranked.
9. Avoid colours per planet is by planet, not by sign or house; no avoid colours for Uranus, Neptune, Pluto (no classical enmity table).
10. Database: tables are named `ref_*`, migrations numbered 0002 and 0003 (0001 is PR #2's). Owner to confirm naming before any live apply.

## Not done in this change
- Nothing deployed, no migration applied to D1, not merged.
- Not wired into guide.py / daily output.
- Not run on divisional charts (the functions take a lagna sign, so a D9 lagna can be passed, but no D9 caller exists).
- The ledger (docs/CALCULATION_LEDGER.md) is not re-measured; these tables are owner/classical reference tables, not rules from the DB.
