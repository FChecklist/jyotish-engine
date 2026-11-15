# PERSONAL PIPELINE — person-specific daily Do / Don't (2026-11-15)

Entry point: `core/guide_personal.py` (uses `core/personal.py`). Test: `tests/test_personal.py`. The older `core/guide.py` is kept for comparison.

## Why it was rebuilt (owner's correction, 2026-11-15)
The first daily message was a superficial reading. Findings from reading `core/daily.py` and `core/guide.py`:
1. Day-wide panchang lines (Rahu Kaal weight 9, Abhijit 7, "avoid starting anything new" stacked from rikta tithi / nakshatra class / yoga / Bhadra) were the heaviest candidates, so the same 1-2 lines appeared for EVERY person.
2. The running dasha (maha / antar) was never read in the daily layer (only inside the monthly window). The annual chart (Varshaphal: Muntha, year lord) did not exist anywhere in the engine.
3. The "person" part was only gochara counted from the natal Moon, plus Tara/Chandra. Natal yogas, planet dignity, house lordship and lordship-weighted house shares were not connected to the day.

## What it analyses now (per person, per day)
| Group | Computed | Rule source |
|---|---|---|
| Natal | D1 signs, whole-sign houses, dignity (exalted/own/friend/enemy/debilitated), house lordship and occupancy weighted by the multi-sign house shares (influence.py), named yogas present | CALCULATION_LEDGER tables, influence.py |
| Dasha | running Vimshottari maha, antar, **pratyantar** (computed by proportion from the antar dates) and each lord's natal condition + today's transit result from the natal Moon; natal yogas those lords belong to are switched on | BK13 gochara rules, Vimshottari |
| Annual (Varshaphal) | exact solar return (sidereal Lahiri Sun back on natal longitude, verified to < 0.01 deg), annual lagna, Muntha = natal lagna + completed years (BK9_0306), Muntha house (BK9_0318-0329), Muntha lord house (BK9_0314-0316), year lord among the five candidates of BK9_0305 chosen by a SIMPLIFIED dignity-and-house score | BK9 (tajaka) rules in the rules DB; tri-rashi table classical |
| Birth vs today | Tara Bala (birth star vs today's star), Chandra Bala (today's Moon from natal Moon) | GR-D1, GR-D2 |
| Today's panchang | tithi, nakshatra class, yoga, Bhadra: marked "everybody" (not personal) and sorted AFTER personal reasons | GR-D3..D6 |
| Day lords | weekday lord and the lord of today's star: their natal condition decides what they bring to this person | hypothesis |
| Transit vs natal | gochara of all 9 planets from the natal Moon with vedha and ashtakavarga (gochara.py), spread over the natal houses the transit sign touches; transit planet within 3 deg (Moon 6 deg) of a natal planet | BK13; contact rule has no DB rule (classical) |

## How lines are chosen
Every finding is a **signal**: `{area (house 1-12 or "start and decide"), signed weight, group, factor tag, plain reason, rule ids}`. Signals are summed per area. The 3 largest positive areas are DO, the 3 largest negative are DON'T. `|net| >= 1.0` is a clear signal; between 0.25 and 1.0 the line is shown marked **(mild)** only to fill up to three; below 0.25 nothing is shown, so a person can have fewer than 3 lines. Nothing is padded. Each line shows its two best reasons, preferring personal factors and different factor groups. The full list of signals (with weights and rule ids) is in the JSON output.
"Everybody" items (Rahu Kaal, Abhijit window) are printed once at the bottom, not as personal lines.

## Honest limits (printed in every result under `limits`)
- All weights are hypotheses. Accuracy is not measured (event backtest on 20 dated events: chance level). No probability or percentage is claimed.
- 9,849 of 29,430 book rules (33.5%) are executable. Natal fired book rules are attached to each line as **support only** (life-long, not day-specific, not scored).
- NOT built, therefore not used: shadbala, Panchavargeeya bala (year lord uses a simplified score), Mudda/Varsha dasha, Tajika aspects and ithasala, other dashas, divisional-chart rules, Lal Kitab states, Jaimini, KP ruling planets, doshas, transit aspects to natal planets.
- Same weekday / same tithi as at birth is recorded in `facts.birth_vs_today` but not scored (no executable rule).
- Pratyantar is computed by proportion and not cross-checked against PyJHora. Dasha dates +-5 days.
- The family home (Delhi NCR) is used for today's panchang and the annual chart.

## Run
`python core/guide_personal.py FAMILY.json YYYY-MM-DD OUTDIR 'books_master_v8.part*.jsonl,gautam_final_v2.jsonl' 'atoms_ai_v*.jsonl'` (set `PYTHONUTF8=1` on Windows). Writes `guidance_personal_DATE.txt` and `personal_DATE.json` to OUTDIR (keep OUTDIR outside git: the JSON contains chart-derived facts).
