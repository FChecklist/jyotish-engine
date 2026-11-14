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
