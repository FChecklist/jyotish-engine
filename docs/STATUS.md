# Status (2026-11-14)
Done: rule DB v8 (24,171 rules); core/zodiac+houses (tests pass); technique engine + 2 spec sets; backtest tooling; PyJHora verification 001 (ascendant identical, planets within 51 arcsec, nodes differ by setting).
In progress: repo + Cloudflare setup.
Blocked: nothing hard. Open questions pending.
Not verified: dasha levels below antardasha, other dasha systems (Narayana, Chara, Yogini ...), D-charts beyond D9, KP cusps and ruling planets, panchang end-times and extras, transit, Ashtakavarga, historical time zones.
Known bugs: legacy engine crashes above 66 deg latitude.
Data gaps: Brihat Jataka ch 1-4, 26-28; Jaimini Sutras remainder; 17 transcripts; Lal Kitab Varshphal table; Urdu scans; founders group.

2026-11-14 update: core/charts.py wrapper built (PyJHora, D1-D60 incl. ascendant). Signs verified for 14 divisional factors (RESULTS.md). Still unverified: nodes, D2/D5/D6/D8/D11/D30 variants, dasha dates, KP cusps and ruling planets, panchang end-times and extras, transit, Ashtakavarga, historical time zones.
Engines: NOT complete. Built: house model, technique engine, rules DB, chart wrapper. Not built: rule normalisation, M2-M11 modules, report assembler, Stage 3 pipeline, validated accuracy.

2026-11-14 late: wrappers done and tested: charts, Vimshottari maha+antar, panchang (5 limbs), KP lords, Ashtakavarga (variants exposed), transit. tests/run_all.sh passes locally; CI workflow added (check GitHub Actions tab). Checks assert thresholds and fail on regressions (sabotage-tested).
Not done: other dasha systems (Narayana etc.), KP cusps, panchang end-times, ingress dates, rule normalisation (24,171 rules), method packs M2-M11, report assembler, Stage 1-3 pipeline, large dataset + locked test.
2026-11-14 later: core/report.py builds the Step 1 report (chart D1-D60, panchang, KP lords, dasha, ashtakavarga both variants, transit, birth-time sensitivity). events/dos/donts/precautions/remedies are empty 'not_built' sections; calibration 'none'. Known limitation: KP block uses report ayanamsa, not Krishnamurti, until wired.
2026-11-14 rule normalisation v1: 15.0% of rules parsed. Next: aspects ('aspecting', 'drishti'), lord-of-X-in-Y with qualifiers, own/exalted/debilitated sign states, yogas by name (Ruchaka etc.), Jaimini (Atmakaraka, karakamsa), Lal Kitab sleeping/awake states; then re-measure.
2026-11-14: core/house_signs.py built: per house, signs under whole/equal/equal-mid/sripati/porphyry/KP-placidus with votes, plus D9 layer and planet-house shifts across systems. Rajat test: H1 = Leo main, Cancer secondary (about 4.9 deg avg); only Mercury changes house (1 vs 2). Rule engine does not use it yet.

## 2026-11-14 update
- DONE: core/apply_rules.py, Lal Kitab frame in influence.fit, report events/dos/donts/remedies filled (status built_unvalidated) when rules_glob is passed.
- NEXT: extend parser beyond 15% (aspects, dignity, yogas, Jaimini terms); wire KP ayanamsa; load rules to D1; check CI.

## 2026-11-14 late
- DONE: daily and Sun-sign 3+3 guidance for four people (core/guide.py); event backtest (tune/event_backtest.py); diary scorer.
- NOT COMPLETE (honest list): rule parser covers 15%, transit-condition parser missing for ~850 DB transit rules, no dasha-to-rule linking, KP ayanamsa not wired, no Jaimini dashas, Yamaganda/Gulika/Choghadiya/hora not built, birth time of Rajat unresolved (two lagna candidates), no measured accuracy above chance.

## Update 2026-11-14 (late)
- AI conversion run finished. 3,717 AI atoms loaded (`jyotish-code/rules/atoms_ai_v2.jsonl`). Executable rules: 8,325 / 29,430. Run `tune/coverage.py`.
- Next: strength/shadbala, Lal Kitab, Jaimini, other dashas, transit-condition parser, the ~17,000 not-yet-expressible rules (need new atoms: lagna-sign, strength, transit, divisional).

- Executable rules: 9,655 of 29,430 (32.8%) after lagna_sign. NOT complete.

- Executable rules: 9,849 of 29,430 (33.5%) after group atoms. NOT complete.
