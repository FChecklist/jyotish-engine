# Planet sign negatives + colour remedies (owner table, 21 Nov 2026)

Version: 0.1.0 (see CHANGELOG.md, version.json). Source: owner, 21 Nov 2026. This is a tradition claim, not a measured fact. No accuracy is claimed.

## What it is
- For each planet the owner lists signs where the planet is negative.
- A planet is also negative if it aspects one of those signs with one of its own listed aspects.
- For each flagged sign the owner gives colours that cancel it. Any ONE listed colour works, or the full combination.
- The colour is used in that zodiac area (the flagged sign) on 3 scopes: body, house, office.

## Files
- Table: `data/planet_sign_negatives.csv` (13 rows, one per planet and sign group; Neptune has two groups, A and B).
- Code: `core/planet_negatives.py` (plain if/then, no AI, no chart maths; it only reads signs).
- Tests: `tests/test_planet_negatives.py` (in `tests/run_all.sh`).

## Columns
- planet, rule_group (A, or A and B for Neptune)
- negative_signs: placement signs
- aspect_numbers: the planet's own aspects. The planet's sign is 1. So 7th = 6 signs ahead.
- aspect_target_signs: same list as negative_signs (owner: "aspecting them")
- remedy_colours: single colours, each works alone
- remedy_combination: all together as one set. Empty when the owner gave one colour only.
- remedy_scopes: body, house, office
- source: "owner 21 Nov 2026"; notes: owner rule number
- List columns are JSON arrays inside the CSV cell.

## The table
| # | planet | group | negative in (placement) | also negative when aspecting those signs by | single colours | combination |
|---|---|---|---|---|---|---|
| 1 | Sun | A | Taurus, Virgo | 7th | blue | (none) |
| 2 | Moon | A | Scorpio, Aries | 7th | yellow, red | yellow + red |
| 3 | Mars | A | Cancer | 4th, 7th, 8th | blue, yellow | blue + yellow |
| 4 | Mercury | A | Pisces, Cancer | 7th | blue, yellow, grey | blue + yellow + grey |
| 5 | Jupiter | A | Capricorn, Aquarius | 5th, 7th, 9th | black, red | black + red |
| 6 | Venus | A | Gemini, Virgo, Cancer | 7th | blue, green | blue + green |
| 7 | Saturn | A | Aries, Scorpio, Cancer | 3rd, 7th, 10th | red, yellow, grey | red + yellow + grey |
| 8 | Rahu | A | Sagittarius | 7th | yellow, green, black | yellow + green + black |
| 9 | Ketu | A | Gemini | 7th | green, purple | green + purple |
| 10 | Uranus (Indra) | A | Cancer, Taurus, Libra | 7th | yellow | (none) |
| 11 | Neptune (Varun) | A | Aries, Scorpio, Cancer | 7th | red, yellow | red + yellow |
| 12 | Neptune (Varun) | B | Gemini | 7th | green | (none) |
| 13 | Pluto (Yum) | A | Aries, Scorpio, Cancer, Leo | 7th | red, yellow | red + yellow |

In every rule: colour goes in that zodiac area on body, house and office.

## How the engine reads a chart
- Call `planet_negatives.evaluate({planet: sign})`. Sign = name (any case) or index 0..11 (0 = Aries). `from_engine_chart()` converts core/charts.py output. Aliases Indra, Varun/Varuna, Yum/Yama are accepted.
- For each planet and each of its rule groups:
  - Placement: planet's sign is in negative_signs -> flag, flagged sign = planet's own sign.
  - Aspect: for each listed aspect number n, sign = n-th from the planet's sign (own = 1). If it is in aspect_target_signs -> flag, flagged sign = that sign.
- Each flag carries its remedy: the zodiac area, the single colours, the combination, `options` (each single colour, then the combination) and `by_scope` (the same options for body, house, office).
- Output also has `planets` (per planet: sign, negative yes/no, flags), `negative_planets`, `by_sign` (flags grouped by flagged sign) and `flags`.
- Unknown planet names (e.g. Lagna) raise an error unless `ignore_unknown=True`. Nothing is silently dropped.
- Example: Saturn in Libra -> 7th aspect hits Aries, 10th hits Cancer -> two flags, each with red / yellow / grey / (red + yellow + grey).

## Readings chosen (most literal) - please confirm
1. "Zodiac area" = the flagged sign itself. Not converted to a compass direction or body part. The engine returns the sign name. (The repo has an Astro-Vastu sign-to-direction table, data/astro_vastu_zodiac_directions.csv; it is NOT used here.)
2. Aspects are counted by sign, forward only, own sign = 1 (whole-sign). No degree orb. No retrograde or conjunction rule.
3. Aspect numbers are exactly the ones the owner lists per planet. Rahu and Ketu: 7th only (other repo notes assume 5/7/9 for nodes; this table follows the owner and does not change those).
4. Where the owner gave one colour (Sun, Uranus, Neptune group B) the combination column is empty; no invented combination.
5. "A or B or (A + B)" = three options, no ranking. The engine lists all.
6. If two planets flag the same sign, both flags are kept with their own remedies. Remedies are not merged or ranked.
7. A planet can give several flags (placement and aspects). Each flagged sign is reported once per flag.
8. Sign positions come from the chart given (D1 as the calculator returns it, Lahiri). Outer planets come from core/outer.py. Divisional charts (D9 etc.) are not run.

## Questions for the owner
- Q1. Should "this zodiac area" be shown as the Astro-Vastu direction of the sign too?
- Q2. Rahu and Ketu: confirm 7th aspect only.
- Q3. Should the rules also be run on D9 and other divisional charts? (Repo rule: MAIN PART applies to every chart.)
- Q4. Should a flag change the daily 3 DO + 3 DONT output, or stay in the engine JSON only? Right now it is stand-alone and not wired into guidance.
- Q5. When two flags point at the same sign with different remedy colours, which to show first?

## Not done in this change
- Not loaded to Cloudflare D1, nothing deployed.
- Not added to the rules DB or to docs/CALCULATION_LEDGER.md counts (these 13 rules are an owner table, not DB rules); re-measure the ledger only when it is decided where they count.
