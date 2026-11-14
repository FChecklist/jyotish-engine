# CLAUDE.md — read this first, every session

Project: Vedic astrology software with 4 engines (event prediction, timing, do/don't, remedies). Owner: Rajat (solo founder, IST). Family birth data NEVER goes in git.

## Session start (do in order)
1. Read SAVE.md, then docs/STATUS.md, docs/DECISIONS.md, docs/OPEN_QUESTIONS.md.
2. Run the tests (docs/RUNBOOK.md). Trust tests over notes.
3. Do NOT ask Rajat anything already answered in docs/DECISIONS.md.

## Session end (mandatory)
Update SAVE.md, docs/STATUS.md, docs/RESULTS.md, docs/DECISIONS.md; commit; push. Back up docs to Drive family folder 1KdxtA9DlH5rR2HLnF-qV60vQd8tLKjwd.

## Hard rules
- MAIN PART: houses are multi-sign. Never judge a rule on one house-sign only. Use core/influence.py (shares per house, weighted fit). See docs/DECISIONS.md 2026-11-14.
- The software is NOT AI: plain code, maths, if/then. It outputs a detailed per-method report. AI only infers from that report.
- 3 stages: (1) evaluate every technique per method/astrologer, (2) apply techniques stepwise to a chart, (3) AI inference using 1+2 (events, age, timing, probability, do/don't, remedies, precautions).
- Stage 3 uses ONLY fired techniques and MEASURED numbers. No validated signal => say so. No death dates, medical diagnoses, investment advice. Remedies/do-don'ts are labelled tradition claims.
- NOTHING LEFT OUT (user 2026-11-14): every rule and calculation is tracked in docs/CALCULATION_LEDGER.md (run tune/coverage.py). Write the rule/spec first, then code, then test, then re-measure the ledger. Never claim 'complete' unless the ledger says so.
- Do not recalculate charts the calculator already gives (PyJHora / Swiss Ephemeris). Our job is analysis.
- Lahiri ayanamsa default. No assumptions, no shortcuts.
- Report measured accuracy on unseen data only. Never claim 90% until measured on a locked test set.
- Rajat's style: direct senior advisor, simple English, bullets, no flattery, point out errors and weak reasoning.
- Rajat works from a phone; no laptop. JHora desktop is not used.

- OUTPUT SHAPE (user, 2026-11-14): ONLY 3 DO + 3 DONT per person per day, and 3 DO + 3 DONT per Sun-sign period. No predictions, no reasons, no rule ids. Reasons stay in the engine JSON. Entry point core/guide.py; rules docs/GUIDANCE_RULES.md. Daily message goes to the chat (send_later chain, 06:00 IST). Probability only when measured.

## Where things are
- docs/ : why, spec, decisions, status, results, runbook, open questions
- core/ : zodiac, houses (6 systems), config   tech/ : technique engine + specs   tune/ : backtests
- ref/ : PyJHora comparison   engine_legacy/ : old engine (crashes above 66 deg latitude)
- Rules DB (24,171 rules): GitHub FChecklist/jyotish-code rules/ (6 parts); full copy in Drive. D1 load still pending.
- Cloudflare account connected (D1, R2, KV via connector). Workers deploy from this repo via Cloudflare Git integration.
