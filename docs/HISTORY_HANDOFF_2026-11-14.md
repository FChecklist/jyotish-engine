# Handoff 2026-11-14 (astrology engine project, owner: Rajat)
Drive folder: 1KdxtA9DlH5rR2HLnF-qV60vQd8tLKjwd (family folder). Style wanted: direct advisor, simple English, bullets, no flattery; state weaknesses and errors plainly.

## Goal
Four engines (events, timing, do/don't, remedies) on a software that is plain code (no AI inside): software computes and applies methods step by step and outputs a detailed report; AI only infers from that report. Three stages: (1) evaluate every technique per method/astrologer, (2) apply techniques to a chart stepwise, (3) AI inference using Stage 1 + 2 (events, ages, timing, outcomes, probabilities, do/don't, remedies, precautions). Owner's aspiration: 90%+ accuracy; I report measured numbers on unseen data only.

## Decisions by owner
- Lahiri ayanamsa approved (default). KP ayanamsa (Lahiri vs Krishnamurti) not decided; keep both.
- Calculation layer: use existing software, do not recalculate. Owner wants Jagannatha Hora (PVR Narasimha Rao's Windows program) as the answer key; PyJHora (open-source port by Sundar Sundaresan, AGPL-3.0-or-later, installed in ref/venv) is the automatable stand-in until matched to JHora.
- Open: mean vs true node default; apparent vs geometric positions; meaning of "Narayana chart" and "sayan chart"; which divisional variant is primary; which birth-time grades allowed for which charts.
- Reddit/Facebook/X people data: Reddit blocked by the browser extension (old.reddit.com); Facebook and X not used. Not collected.

## Files in Drive (family folder)
- books_master_v8.part1of6 ... part6of6.jsonl (24,171 rules, join in order). Older v5 part files and a results note exist too (outdated).
- ENGINE_SPEC_v1_2026-11-14.md (master concept spec; the local copy has later edits: architecture decision and verification log).
- astro_new_code_2026-11-14.tgz (new modules core/, tech/, tune/*.py, ref/*.py, people data bt2/D1,D4-D7,D9, agent brief).
- Earlier: MASTER_HANDOFF_2026-11-13.md (id 1xWs-BMqReKFj4-K59oI1H3fIOJMmpYO0), FINETUNE_RESULTS_2026-11-13.md, RESULTS_v5_2026-11-13.md.

## State of results (all on unseen-data logic; metric: percentile of event date in the person's own timeline, 50 = chance)
- Fine-tune CV on 111 people / 890 events: out-of-fold 50.9, 95% CI 48.8-52.7 (equal weights 51.3). No skill shown.
- 44 technique-area tests (incl. strict composites): none passes multiple-testing correction. One lead (both dasha lords own an area house, foreign events) went from q 0.11 to 0.54 after removing approximate-date events.
- Verification 001: our ascendant/planets match PyJHora within 51 arc-seconds (geometric vs apparent positions explain it); nodes differ (true vs mean); D9 signs agree except nodes. Old engine crashes above 66 deg latitude. Report: ref/VERIFY_REPORT_001.md (in the tgz).

## Built
core/zodiac.py, core/houses.py (six house systems incl. bhava chalit, all signs spanned per house), core/test_houses.py (passes), core/config.py, core/SPEC.md. tech/ (technique specs, validator). ref/ (PyJHora comparison scripts).

## Next steps (agreed order)
1. Get JHora (desktop) as answer key: link the owner's laptop via the Claude desktop app (needs a task started in the desktop app, not claude.ai web) OR owner exports ~20 charts (planet table, Vimshottari, D9, D10, panchang, KP table, exact inputs and settings).
2. Wrapper around PyJHora, one function per chart type, standard output; verify each against JHora/books.
3. Normalise the 24,171 rules into checkable conditions (frame, house system); group rules by claim and count source agreement.
4. Modules M0-M11 per spec; Stage 1-3 pipeline; Stage 3 may only use fired techniques and measured numbers; no death dates, medical, or investment advice.
5. Larger natal dataset (thousands, Astro-Databank), locked 30% test set; prospective prediction log.
## Known data gaps
Brihat Jataka ch 1-4, 26-28; Jaimini Sutras remainder; 17 transcript files; Lal Kitab annual (varshphal) table (only ages 81-100 legible in Gosvami; Gosvami's formula: age divided by natal house number, remainder house); Urdu Lal Kitab scans unreadable; Founders/scientists people group incomplete (astro.com rate-limit).
