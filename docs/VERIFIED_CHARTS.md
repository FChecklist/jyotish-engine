# Verified reference charts (jagannathahora.com) — 2026-11-22

What this is: the owner's four family charts (RAJAT, PALLAVI, ESHANI, PEHU) captured from his own
logged-in jagannathahora.com account, stored in the project's own Cloudflare D1 database
`jyotish-rules` as the **verified reference charts** (`vc_person.verified_source = 'jagannathahora.com'`).

**No birth data is in this repository.** CLAUDE.md rule: family birth data never goes in git. This repo
holds only the schema (`migrations/0001_verified_charts.sql`), the parser/loader (`core/verified_charts.py`)
and a synthetic-data test (`tests/test_verified_charts.py`). The captured files live in `data_private/`
(git-ignored) and in D1.

## How it was captured
- Read-only. Only saved charts were opened. Nothing was saved, shared, deleted or edited on the site; no
  password was typed. The site switches its active chart only when "Generate Horoscope" is pressed
  (a calculation, not a save), so that button was pressed once for PALLAVI, ESHANI and PEHU. RAJAT was
  already the active chart.
- Each person: every route the site offers (Basic, Details x3 tabs, Charts, Dasha, Transits, Saturn x3,
  Chakras x8, Balas, Ashtakavarga x20 views, Yogas, Longevity, Arudhas, Argala x46, Sahams, Analysis,
  Tithi Pravesha, Varshaphal), all 23 divisional charts D1-D144 (dropdown), all 28 rashi dasha systems and
  all 28 graha dasha systems (collapsed and expanded). Page text is stored as data; screenshots are stored
  as evidence.
- Identity was checked after pressing Generate on the Analysis screen (name, date, time, place).

## Where it is
| Table | Holds |
|---|---|
| `vc_person` | birth data exactly as the site shows it, source URL, capture time, `verified_source`, doubts |
| `vc_screen` + `vc_screen_chunk` | every view as text (chunked); small screens also as `tables_json` |
| `vc_body_position` | Details > Key Info: longitude, nakshatra, pada, rasi, navamsha per body |
| `vc_body_varga` | sign + degree of every body in D1-D144 |
| `vc_dasha_period` | graha dasha periods (28 systems, up to pratyantar), nesting level derived from dates |
| `vc_screenshot` + `vc_screenshot_chunk` | screenshots linked to person + screen name, sha256, bytes (base64, chunked) |

### What is in D1 now (verified 2026-11-22 with `--verify`)
| Person | screens (text) | screen chunks | key-info rows | varga rows | dasha periods | screenshots |
|---|---|---|---|---|---|---|
| RAJAT | 261 | 313 | 59 | 299 | 25,181 | 26 |
| PALLAVI | 233 | 283 | 59 | 299 | 23,885 | 20 |
| ESHANI | 233 | 283 | 59 | 299 | 24,555 | 20 |
| PEHU | 233 | 281 | 59 | 299 | 25,276 | 20 |

Each person has one `vc_person` row with `verified_source = 'jagannathahora.com'`, the source URL, the
capture time (UTC) and a `doubts_json` list (open questions on time, place, gender). The doubts are kept in
D1 and in the hand-over to the owner, not in git. Screenshot names are `<PERSON>_<nn>_<screen>.jpg`; they
are linked by `vc_screenshot.screen_name`. RAJAT has more screens and screenshots than the others
because his capture was done first, with an extra first pass of default views and a larger screenshot set.

Rashi dashas (Chara, Narayana, ...) are stored as text only (month-year ranges; no structured parse yet).

Reload / verify (needs `CLOUDFLARE_D1_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` in the environment; never printed):
`python core/verified_charts.py --init`, `--load RAJAT`, `--verify`.

## Limits (honest list)
- Values are what the site displayed. We did not recompute them (CLAUDE.md: do not recalculate). They are not
  cross-checked against PyJHora/Swiss Ephemeris here; that is the next step (compare lagna/planet longitudes).
- The site shows times to the minute only. The engine's owner-fixed times (docs/DECISIONS.md 2026-11-16) may
  carry seconds.
- Screenshots are zoomed-out views (page zoom 40-50 percent) so a whole screen fits; the text is in the tables.
- Transits, Tithi Pravesha and Varshaphal screens depend on the capture date (22 Nov 2026), not on birth.
