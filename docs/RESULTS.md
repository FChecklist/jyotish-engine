# Measured results (metric: percentile of event date in person's own timeline; 50 = chance)
- 2026-11-13/14 Fine-tune CV, 111 people / 890 events: out-of-fold 50.9, 95% CI 48.8-52.7; equal weights 51.3. No skill.
- 44 technique-area tests: none survives multiple-testing correction. One lead (dasha lords own area house, foreign events) q 0.11 -> 0.54 after removing approximate-date events.
- Verification 001 vs PyJHora (7 charts): see ref/VERIFY_REPORT_001.md.
Conclusion: no demonstrated predictive skill yet. Next: bigger exact-date dataset, locked 30% test set, prospective log.
- 2026-11-14 Verification 002 (divisional charts): our own Swiss Ephemeris + BPHS formulas vs PyJHora signs. D1,D3,D4,D7,D9,D10,D12,D16,D20,D24,D27,D40,D45,D60: 40/40 signs agree each (5 charts x asc + Sun..Saturn). Limits: only 5 charts, nodes not tested, D2/D5/D6/D8/D11/D30 not tested (variant-dependent), degrees within sign differ between PyJHora functions and are not checked. Test: tests/verify_divisional.py (run with the ref venv python).
- 2026-11-14 Verification 003 (Vimshottari mahadasa): own Moon nakshatra + proportional balance + 120y cycle vs PyJHora. 5 charts: dasha lord order matches 5/5; mahadasa start dates differ by 1.6-3.0 days (worst 2.97). Year length (365.25 vs 365.256364) does not explain it. A 2-3 day shift on a 7-20 year dasha equals ~0.01 deg in Moon longitude, within the known 51 arcsec position-setting difference (geometric vs apparent). So: lords and sequence verified; exact dates carry about +-3 days until position settings are aligned. Antardasha and deeper levels not yet verified. Test: tests/verify_dasha.py.
- 2026-11-14 Verification 004 (Vimshottari antardasha): 5 charts x 81 rows. Order of sub-lords correct 5/5; durations equal MD*AD/120 exactly; but PyJHora start dates wobble up to 3.3-5.3 days from an ideal even-year timeline (it uses a calendar-style year, not a constant-length year). So antardasha start dates are good to about +-5 days; any event-timing test must use a window wider than that. Convention still to choose and document. Test: tests/verify_antardasha.py.
- 2026-11-14 Verification 005 (panchang): own Swiss Ephemeris maths vs PyJHora, 50 cases (5 places x 10 dates incl. 1947, 2026): tithi, nakshatra, pada, yoga, half-tithi (karana number), weekday all 50/50 match. Sunrise and sunset differ by up to 4.7 minutes (my test uses sun-centre, no refraction; PyJHora uses a different disc and refraction setting). Not an error, but sunrise is used to start the Vedic day, so tithi-at-sunrise could differ for births within ~5 min of a boundary. Not tested: tithi/nakshatra END times, hora, choghadiya, special yogas. Test: tests/verify_panchang.py.
- 2026-11-14 Verification 006 (nodes): PyJHora's Rahu equals the Swiss Ephemeris TRUE node to 3 decimals on 5 charts; mean node differs by 0.7-1.6 deg. So PyJHora default = true node = our stated default. Mean node would need a setting (not yet exposed in core/charts.py).
- 2026-11-14 Verification 007 (KP lords): core/kp.py star/sub/sub-sub lords. Hand-checked against published KP table values (Ashwini Ke-Ke 0:00-0:46:40, Ke-Ve to 3:00, Bharani=Venus, Revati=Mercury), all 27 nakshatra splits sum to 13:20, 360 deg total, 36,000 sample points valid. Not yet checked: KP house cusps (Placidus) against a published KP chart; ayanamsa choice (Lahiri vs Krishnamurti) effect on lords. Test: tests/test_kp.py.
- 2026-11-14 Verification 008 (Ashtakavarga): 60 random charts (1900-2020, lat -50..60). All 8 row totals equal the BPHS fixed totals (48,49,39,54,56,52,39,49) and SAV=337 on 60/60. Sun BAV and Moon BAV rebuilt independently from BPHS tables match 60/60 -- but Moon matches only with variant 'bphs_plain'. PyJHora's defaults switch on four Moon/Venus variants (moon_benefic_9_from_moon, moon_malefic_9_from_mars, moon_benefic_2_from_jupiter, moon_malefic_12_from_jupiter), so the default Moon/Venus tables differ from my recalled table by a few bindus. Mars/Mercury/Jupiter/Venus/Saturn tables checked by totals only, not cell by cell. Which variant the books support is OPEN. Test: tests/verify_ashtakavarga.py.
- 2026-11-14 Verification 009 (transit): 40 random dates 1900-2100 vs Swiss Ephemeris: worst longitude difference 60 arcsec (same geometric-vs-apparent effect as verification 001); sign mismatches 0; retrograde flags (Mars..Saturn) 0 mismatches; true node within 5 arcsec on all. Not tested: sign ingress dates, Sade Sati, Moon-based transit (Gochar) results, Vedha. Test: tests/verify_transit.py.
- 2026-11-14 Rule normaliser v1 (core/rules_norm.py): of 24,171 rules, 3,625 (15.0%) are fully parsed into testable atoms (planet in house/sign, house lord in house, conjunction, kendra/trikona groups); 6,783 partial (qualifiers such as weak, aspected, alternatives: NOT evaluated); 13,763 unparsed. By system: lalkitab 36.7% parsed, kp 24%, parashari 9.8%, jaimini 0%, prasna 1%. A first audit found a misparse (slash = alternatives read as AND); fixed and tested. Hand tests pass (tests/test_rules_norm.py). Parsed does NOT mean the rule is true: it means the software can check whether a chart satisfies it. Tool: rules/normalise_all.py.
- 2026-11-14 House-sign influence model (core/influence.py): 7 views (6 house systems + D9). Rajat test: house 1 = Leo 71.6 percent (main), Aries 14.3 percent (D9 lagna), Cancer 14.1 percent (minor); only Mercury straddles houses (1st 67 percent, 2nd 33 percent). Invariants tested: shares sum to 1 per house; each planet's house shares sum to 1; for every N the N-th lord's fit over all houses sums to 1. NOT yet tested for accuracy: the equal view weights and the 8 percent cutoff are hypotheses; they must be tuned on the validation set.

## 010 — Parsed rules applied with weighted fit (2026-11-14)
- 24,171 rules read; only fully parsed ones (about 15%) can be applied. On Rajat's chart, 369 fired at fit >= 0.5 (lalkitab 266, parashari 89, other 11, kp 2, prasna 1).
- By role: rule 189, remedy 95, event 45, foundation 32, donot 4, yoga 3. 296 have fit 1.0.
- Most are generic per-planet-in-sign or Lal Kitab statements. They are tradition claims, NOT validated. Probability stays null, calibration none.
- Lal Kitab uses the Aries-fixed frame (open question): fit is 0 or 1, one view only.
- Tests: tests/test_apply_rules.py, and a report wiring check in tests/test_report.py. Full suite passes.

## 011 — Guidance view (2026-11-14)
- On Rajat's chart as of 2026-11-14 (Venus-Moon period): 93 dos, 4 donts, about 5 precautions, 11 dropped by safety filter. Unvalidated.
- Test caught a bug: remedy text was not checked by the safety filter. Fixed.

## 012 — Daily and Sun-sign guidance (2026-11-14)
- Tests: tara counts, Rahu Kaal for all 7 weekdays, gochara hand cases (BK13_0019, 0021, 0007, 0006, 0005), vedha table equals DB text, Sun ingress moments checked against Swiss Ephemeris (within 0.02 deg of a sign border), end-to-end 3+3 with no reasons in the user view, diary scorer detects a planted link and ignores noise.
- Window for 14 Nov 2026: Sun in Libra, 17 Oct to 16 Nov. Not yet measured against any outcome.
- Known limits: Rajat's lagna has two candidates, so area wording from lagna houses is less certain for him; the Moon-based daily checks are not affected.

## 013 — Event backtest of the daily and Sun-sign signals (2026-11-14)
- tune/event_backtest.py. Data: only Rajat has dated events (20 with exact day, births excluded). Pallavi, Eshani, Pehu have none beyond marriage and births, so nothing can be tested for them yet.
- Each event day scored on his chart (daily net score, Chandra Bala, Tara good/bad, gochara score), versus random days within +-400 days (120 per event), 5000 permutations.
- Result: net p=0.74, Chandra p=0.43, Tara good p=0.96 (events fall on good-Tara days LESS than chance), Tara bad p=0.09, gochara p=0.30. Five tests, so p=0.09 is not significant after correction.
- Meaning: no measured signal. The do/dont lists stay unvalidated tradition claims. Consistent with the earlier chance-level tests.
- Caveats: event dates may be rounded (some on 1st or 15th); event cities differ (Delhi used for panchang); many events are job changes, which are not clearly "auspicious start" days. Small sample (20).

## 014 — Dignity and aspect atoms (2026-11-14)
- tests/test_dignity.py: dignity tables hand-checked, aspect counts (Jupiter and Saturn aspect exactly 3 houses per view: fits over 12 houses sum to 3), nodes not silently dropped, fit equals the dignity of the sign.
- Ledger: parsed 3,844 -> 3,965. Small gain; see docs/CALCULATION_LEDGER.md for the remaining blocks.

## 015 — Dasha atoms (2026-11-14)
- tests/test_dasha_rules.py: phrases parse, no date means no evaluation (never guessed), whole-sign sum check, combined natal+dasha rule.
- Ledger: parsed 3,965 -> 4,585. One chart: 419 rules fired of 4,585 evaluated.

## 016 — AI conversion pilot (2026-11-14), 300 rules, 9 agents
- GOLD (150 rules the parser already reads; AI converted blind): 145 exact, 3 different, 2 marked incomplete. Precision when marked complete 98.0%, recall 96.7%.
  - The 3 "different" were PARSER errors, not AI errors: "Mercury in 1-6" was read as house 1 only, "Saturn in Cancer (house 4)" lost the house, "Mercury in Leo (house 5)" lost the house. The AI kept both. Parser fixed (ranges expand; a leftover number makes a rule partial). 77 rules that were wrongly "parsed" moved to partial: parsed 4,585 -> 4,508. Correctness up, count down.
- HARD (150 rules the parser cannot read; two independent AI passes): 17 identical and complete, 0 conflicting, 1 complete in one pass only (rejected), 132 incomplete in both. Hand check of the first 12 agreed: all 12 correct.
- Yield: about 11% of unread rules become executable (17 of 150; roughly 7% to 17% allowing for sample size). Of about 24,900 unread rules that means roughly 1,800 to 4,300 more rules, centre about 2,800.
- The rest (about 89%) are not chart conditions (methods, descriptions, palmistry, advice) or need things the engine has no atoms for yet (strength, nakshatra, yogas, Moon-based houses, transits). The AI correctly refuses them.
- Cost note: each 50-rule agent used about 88k tokens. A full two-pass run at 50 per agent is about 1,000 agents. A pre-filter plus larger batches cuts that a lot.
- Saved: 17 validated pilot atoms in jyotish-code/rules/atoms_ai_v1.jsonl (origin ai_v1_pilot_two_pass_agreed).

## 017 — AI conversion, full run (2026-11-14)
- 20,868 pre-filtered rules in 140 batches, one pass each (sonnet). Marked complete: 3,729; valid under the strict validator: 3,718 (about 18%). One ambiguous rule removed (BK8_1279, any-of vs all-of). Saved 3,717 as `atoms_ai_v2.jsonl` (origin ai_v2_single_pass).
- Two-pass check on batches 1–3: 40/45 identical atoms when both complete (89%); most differences were equal-meaning forms (conj chain vs star).
- Audit: 150 random kept rules re-converted blind. 132 had a complete second answer (18 the second pass left incomplete). By meaning (conj groups and same-house placement treated as equal), 130/132 agree (98.5%). The 2 differences: any-of vs all-of (BK8_1279, removed) and an extra dignity atom.
- Gold check on the parser's own rules in the pilot: 98% precision (RESULTS 016). Not measured: whether the atoms are right against what the classical authors meant.
- Ledger now: executable rules 8,325 of 29,430 (28.3%): 4,591 by parser + 3,734 by AI atoms. The other 21,105 are partial or unread. NOT complete.

## 018 (2026-11-14) lagna_sign atom + re-conversion
- New atom lagna_sign (validator, multi-view fit, Lal Kitab frame, test tests/test_lagna_atom.py). 1,609 rules blocked by lagna were re-converted (41 batches, single pass); 1,330 valid and complete (83%) -> atoms_ai_v3.jsonl.
- Ledger: executable 9,655 of 29,430 = 32.8% (was 8,325 = 28.3%). Parser 4,591 parsed / 8,118 partial / 16,721 unparsed (unchanged). Not audited blind yet; most are simple "Lagna X, planet P in house N" lines. This is self-consistency, not accuracy vs real life.

## 019 (2026-11-14) blind audit v3 + group atoms
- Blind audit of 60 random lagna conversions (v3): 60/60 agree with an independent second conversion (same model, so this is self-consistency only).
- New atoms group_in_house, planet_with_group, planet_aspected_by, lord_with_group, lord_aspected_by (natural benefic/malefic is a fixed HYPOTHESIS in the ledger). 966 rules re-converted; only 194 (20%) became complete, because most also need strength/shadbala or other qualifiers. atoms_ai_v4.jsonl.
- Ledger: executable 9,849 of 29,430 = 33.5%. Still NOT complete. Biggest remaining: 16,721 unparsed (mostly free-text predictions), strength/shadbala, other dashas, divisional rules.

## 020 (2026-11-15) multi-sign houses in every chart
- tests/test_chart_views.py added; all tests pass; verify_divisional still 40/40 for D45, D60.

## 021 (2026-11-15) event test on 10 dated email events (Rajat)
- tune/event_backtest.py now accepts a private events file. 10 documented events (jobs, company, registrations, travel, education). Daily net score, Chandra, tara and gochara versus random days within +-400 days.
- Result: no signal. net observed -1.0 vs null -0.30 (p higher 0.89); tara good 0.40 vs 0.57; gochara -2.7 vs -3.1 (p 0.34). All at or below chance. n=10 is too small to show a modest effect and some events are weak (flight, domain). This gives no support to the daily-quality score.

## 022 (2026-11-15) strength atom (Shadbala)
- New atom strength (strong = Shadbala ratio >= 1, weak < 1) from PyJHora shad_bala (core/strength.py, tests/test_strength.py). Threshold is a reading choice. Conversion of 1,869 strength-text rules in progress; ledger not re-measured yet.

## 023 (2026-11-15) strength conversion + web rules, ledger
- 1,869 strength-text rules converted (38 batches, single pass): only 90 complete and valid (4.8%), 80 use the strength atom. Most such rules talk about house strength, benefic strength or "strong in own sign", which the atom does not cover. Not audited blind.
- New rule files counted: nakshatra_books_v1 (1,835), lalkitab_web_v1 (519, 518 parse natively), outer_planets_v1 (46, not runnable).
- Ledger: executable 10,957 of 31,830 = 34.4% (was 10,349 of 31,265 = 33.1%). Parser 5,175 parsed / 8,203 partial / 18,452 unparsed. NOT complete.

## 024 (2026-11-22) verified reference charts loaded
- Loaded 4 people. Row counts per person: 233-261 screens, 59 key-info rows, 299 divisional rows, about 24-25k graha dasha periods, 20-26 screenshots. Spot check: lagna sign and degree in D1 match the site screen for each person.
- No accuracy claim. These are the site's displayed values, not yet compared with our own engine.
