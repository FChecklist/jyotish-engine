# SAVE.md — session save point (rewrite at end of every session)

Last saved: 2026-11-14 (IST)
One-line state: Design + first modules built; all accuracy tests at chance level; repo just created; Cloudflare connected; D1 jyotish-rules created (id c944c961-83f4-4035-882b-170072748b1f) with empty rules table; nothing deployed.

## Do next (in order)
1. DONE: repo pushed (public) FChecklist/jyotish-engine. Rules are in public repo FChecklist/jyotish-code (rules/ parts 01-06, no quote_short), by Rajat's decision. D1 table exists and is still empty.
2. Load 24,171 rules into D1 (table exists, empty). Bulk load cannot go through the chat connector (too large); use a private data repo + import Worker via Git deploy.
3. DONE: core/report.py (Step 1 report shape, deterministic, tested; rule sections are empty "not_built"). Wrappers (all verified, tests/run_all.sh passes): core/charts.py, dasha.py (Vimshottari), panchang.py, kp.py (lords), ashtakavarga.py, transit.py. NOT DONE: KP cusps/ruling planets, panchang end-times, Narayana/Chara/other dashas (need an independent rule source before checking), mean-node option, sign-ingress dates, Sade Sati.
4. Normalise rules into checkable conditions (frame + house system).
5. Build modules M0-M11 per docs/SPEC.md.

## Waiting on Rajat
See docs/OPEN_QUESTIONS.md.

## Where the big files are (not in git)
Drive family folder 1KdxtA9DlH5rR2HLnF-qV60vQd8tLKjwd: books_master_v8 parts, ENGINE_SPEC, code tgz, handoffs.


## Latest (2026-11-14)
- apply_rules + weighted fit wired into report (build(..., rules_glob=...)). 369 rules fired on Rajat's chart, all unvalidated. Next: parser coverage (15%), KP ayanamsa wiring, D1 load.

- 2026-11-14: guidance view built (do/dont/precautions only). Next: tie windows to rule timing + transits.

- 2026-11-14: guide.py gives 3 do + 3 dont daily and per Sun-sign month for each person. Next: scheduled daily delivery, diary sheet, transit-condition parser for the remaining DB rules.

- 2026-11-14 night: event backtest = chance. Daily send_later chain set for 06:00 IST. Need dated events for Pallavi, Eshani, Pehu.

- 2026-11-14 night: ledger + dignity/aspect atoms done. Parsed 13.5%. Biggest blocks left: free-text 9,830, strength, dasha, Lal Kitab states, Jaimini.

- 2026-11-14 night 2: dasha atoms done; parsed 15.6%. Rules are all loaded; 84% not executable yet. Waiting for Rajat on AI-assisted conversion of the rest.

- 2026-11-14 night 3: AI conversion pilot done (98% precision, 11% yield). Parser silent-drop bug fixed (parsed 4,508). Full run awaiting Rajat go/no-go.

## Save 2026-11-14 late
Done: full AI conversion (140 batches), audit, merge (`tune/convert/merge_ai.py`), `coverage.py` now counts executable rules (8,325). Daily conflict fix. Pending: purge birth data from git history (user decision), diary ratings, events for Pallavi/Eshani/Pehu, Drive backup of docs, D1 load, daily 06:00 chain (check it is alive).

2026-11-14 late: lagna_sign atom done, 1,330 rules added (atoms_ai_v3). Ledger 9,655/29,430. Next: blind audit of v3 sample, then aspect/malefic/benefic/lord/afflict atoms. Chain 06:00 IST alive.

2026-11-14 night: group atoms + v4 done (9,849/29,430 = 33.5%). Next: shadbala/strength calc, other dashas, divisional atoms, D1 load. Drive backup redone. Chain 06:00 IST alive.
