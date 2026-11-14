# Decisions (date, choice, reason)
- 2026-11-13 Lahiri ayanamsa default (Rajat approved). KP: run Lahiri and Krishnamurti, label output.
- 2026-11-13 Software is not AI; AI only infers from software reports (Rajat).
- 2026-11-13 3-stage verification (Rajat).
- 2026-11-14 Use existing calculator, do not recalculate (Rajat). PyJHora (Sundar Sundaresan, AGPL-3.0) installed as stand-in; Swiss Ephemeris for independent check.
- 2026-11-14 Rajat uses phone only. JHora desktop dropped as answer key. Verify by two calculators + published charts + hand-checkable astronomy.
- 2026-11-14 Defaults pending Rajat's veto: true node, geometric positions, Narayana = Jaimini Narayana dasha, sayan = tropical chart.
- 2026-11-14 House model: natural zodiac house N <-> sign N; six house systems; rules evaluated in the system their source uses.
- 2026-11-14 Stage 3 uses only fired techniques and measured numbers.
- 2026-11-14 Public-data policy: public self-posted birth data may tune the engine, then delete. Reddit blocked, not collected.
- 2026-11-14 Hosting: Cloudflare (paid $5 plan). D1 rules, R2 files; Python in Containers via Git deploy. Connector is deprecated and cannot deploy Workers.
- 2026-11-14 Single source of truth = this repo.
- 2026-11-14 Cloudflare D1 database `jyotish-rules` created (id c944c961-83f4-4035-882b-170072748b1f, APAC). Tables: rules, meta. Empty: rules not loaded yet. R2 not enabled on the account (needs dashboard enable by Rajat).
- 2026-11-14 Rajat approved option 1 for rules: rules stay out of public GitHub. jyotish-data repo stays empty; Rajat to set private. Rules load into D1 by another route.
- 2026-11-14 Both repos created by Rajat as public; engine repo stays public (AGPL-3.0). GitHub connector "GithubMobile" can push but cannot create repos.
- 2026-11-14 CORRECTION: Rajat decided rules may be public for now ("nothing is copyright issue"). Second repo is FChecklist/jyotish-code (not jyotish-data). Rules pushed there: 24,171 rows in 6 parts (rules/), quote_short column dropped (only 1 row had it). Full original file stays in Drive. Rajat may make it private later.
- 2026-11-14 Rajat confirmed two separate steps: (1) software gives probabilities of events, dates, timing, do, don't, precautions; (2) AI inference on that report, acting like an astrologer. Contract in docs/REPORT_CONTRACT.md. Software probabilities must be calibrated from measured past cases; otherwise null.
- 2026-11-14 MAIN PART OF THE SOFTWARE (Rajat, from Brajesh Gautam's teaching): every house is influenced by 2-3 zodiac signs. For each native the engine computes per house a share for each sign from several views (D1 whole-sign, equal, equal-from-middle, Sripati, Porphyry, KP Placidus with Krishnamurti ayanamsa, and D9). Biggest share = main influence, others = minor; both count in proportion. Rules are judged by a weighted FIT (0-1) over views and over the signs of a house (core/influence.py), not true/false on one sign. Weights (equal) and the 8 percent minor cutoff are hypotheses to be tuned on validation data.

## 2026-11-14 — Guidance view: only do / don't / precautions (umbrella rule)
- Rajat: the astrologer's output should be do, don't and precautions, like a forecaster who says "chance of rain, take an umbrella". No long predictions.
- Built core/guidance.py: remedy rules -> DO, donot rules -> DON'T, event rules with a harmful outcome -> PRECAUTION. Window = running Vimshottari antardasha.
- Condition (advisor note): a rain forecast works because its percentages are measured. Ours are not, so probability stays null and every item is a labelled tradition claim until a locked test set gives a measured rate.
- Safety filter drops death, disease and investment items. Word-list matching for harmful outcomes is a v1 hypothesis.
- Known weakness: the window is the running dasha, not yet tied to each rule's own timing or to transits. Next step.

## 2026-11-14 — Family data leak found and fixed
- Rajat's birth date, time and place were in tests and one handoff doc in this PUBLIC repo. Removed; tests now use a neutral chart (1990-01-01 06:00 IST Delhi).
- Git history still holds the old values. Removing them needs a history rewrite and force-push: waiting for Rajat's decision.
- Rule: tests and docs must never contain family birth data. Per-person output goes to Drive, not git.

## 2026-11-14 — User view is exactly 3 DO + 3 DONT (daily and Sun-sign month), per person
- Rajat: no predictions, no reasons, no precautions list. Only 3 do and 3 dont per day, and 3 and 3 for the Sun-sign period, for Rajat, Pallavi, Eshani, Pehu separately.
- Rules written first in docs/GUIDANCE_RULES.md (ids GR-*), tables in core/guidance_rules.py, code in core/gochara.py, daily.py, shortterm.py, guide.py.
- Daily = birth panchang (nakshatra for Tara Bala, Moon sign for Chandra Bala) against the day's panchang and transits. Month = Sun sign window with transit quality (rules DB BK13 gochara incl. vedha, bindus, moorthi, combustion) and areas weighted by main/minor house-sign influence (MAIN PART).
- Reasons, rule ids and all candidates stay in the engine JSON (internal) for AI inference and audit. User view never shows them.
- If fewer than 3 real items exist, fewer are shown; no padding.
- Gautam transcript rules are loaded with the books (weekday remedies and don'ts). Birth data comes from a private path, never git.
- Daily classical tables (Tara, tithi, nakshatra class, yoga, Rahu Kaal, Abhijit) are NOT in the rules DB. Source unverified: open question.
- Measurement: tune/diary_score.py (permutation test against a day diary). No percentages until it passes.
