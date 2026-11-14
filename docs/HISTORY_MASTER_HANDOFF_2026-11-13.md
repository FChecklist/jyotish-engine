# MASTER HANDOFF - Rajat's Jyotish system (written 13 Nov 2026, for Claude to resume from)

READ THIS FIRST. The cloud workspace (/home/claude/astro) is temporary and can disappear between sessions. Drive is the permanent copy. Everything below says where it lives in Drive and how to continue.

## 0. The user and how to talk to him
- Rajat Agarwal, solo founder, Indirapuram (Delhi NCR), IST. Born 24 Aug 1975, Kota.
- Style he wants: senior-advisor tone. Direct, honest, analytical. No flattery or emotional validation. Simple English. Bullets. Challenge his assumptions. Correct my own mistakes openly.
- He says "You do it end to end". He wants parallel work and complete files in Google Drive.
- I have failed twice by forgetting what already exists (13 Nov: he asked for daily do/don't and I did not look in Drive first). RULE: before answering any astrology request, check section 3 (Drive map) and the scheduled task in section 5.

## 1. Goal
One software system that works for ANY birth data, with four engines:
1. Event prediction (what).  2. Timing of events (when).  3. Do / don't advice.  4. Remedies.
Based on many techniques and astrologers (Parashari, KP, Jaimini, Lal Kitab, Nadi, Prasna, Ashtakvarga, Gautam, K.N. Rao, Deepanshu Giri, Poonam Swami, Saptarishis and classical books). Test on famous people for accuracy; then run for Rajat, Pallavi (wife), Eshani and Pehu (daughters). Sources: Gautam database, other rule modules, Drive PDFs, archive.org English books, YouTube transcripts.

## 2. Status at a glance
| Area | State |
|---|---|
| Chart maths (Swiss Ephemeris) | DONE, works for any date/place |
| Engines 1-4 (event/timing, do-dont, remedies) | DONE as v1, command-line + report. Uses 5 techniques scoring. Does NOT yet use the book/Gautam rules in its scoring (only Lal Kitab + Gautam remedies text lookup) |
| Backtest on 19 famous people / 158 events | DONE. Result: NO skill better than chance (see section 8) |
| Family reports (Rajat, Pallavi, Eshani, Pehu), 1 Nov 2026 to 30 Oct 2027 | DONE, in Drive |
| Daily panchang file Nov 2026 to Dec 2027 for Rajat (2 lagna charts) | DONE, in Drive |
| Daily 3 do / 3 avoid / 3 might-happen message | RUNNING as scheduled task every day 17:42 IST (section 5) |
| Gautam rule database | 5,259 rules, in Drive (3 part files) |
| JYOTISH SUITE v1 (4 engines on 12,119 rules) | DONE 13 Nov 2026 - suite/ folder, jyotish_suite_v1.zip in Drive. 2,948 rules machine-readable. Rule layer backtest: mean percentile 52.3 (chance 50), top-20% hit 16% (chance 20%) = no proven skill |
| Book rule database | 2,120 rules from 15 sources, local file + backup zip in Drive (section 6). NOT wired into engines |
| YouTube transcripts | NOT DONE. Cloud cannot reach YouTube. Package for the user's laptop is in Drive (section 7) |
| Raman "Hindu Predictive Astrology" (126 MB) and "Dasha.pdf" (111 MB) | Scans, no text. Need OCR or an English text copy |

## 3. Google Drive map (permanent)
- Astrology root folder: 1yZaA-2TOH7kJm6PhyV4YDfWo_mDO8Sf0 (user's consolidated astrology folder).
- Family Vedic Analysis - Nov 2026: folder 1KdxtA9DlH5rR2HLnF-qV60vQd8tLKjwd. Contains:
  - Family Vedic Analysis - Nov 2026 (Rajat, Pallavi, Eshani, Pehu): Google Doc 14X6EmEDkfyMgpZDj0VrVzQRZyoZNyVdjFR51xz1UmKs
  - gautam_rules_final_v2_part_00/01/02.jsonl (ids 1XZfC4ycD46VjBXAP77bi-my_-7oWVcjQ, 14dUpEuguYxtNc-D3ZJy6p-NLn5auXYPE, 1sxdgY0Zyu4k0YufQf5I0rFlsYACvUfXn) = the 5,259 Gautam rules
  - astro_engine_code.zip (older), astro_engine_code_v2.zip 1NNp_vGmwJRRzvW7DFzgUYibHFYGMFoA0 (code of the dual-chart panchang tools)
  - panchang_daily: folder 1qnKb0Cee6DRzcCjSEZ8_vZnNiZmHCJel (monthly files astro_panchang_v2_YYYY-MM.txt; ids in section 5)
  - Family 10/10/10 files folder 1B3-SvZM3X6Qe8UNJhPEVvoY9UazxO-wd: Rajat_3_do_dont_predictions.txt 1r6rN9NWmC0bpEJzVqZ6J7lK-vMX9_5-a, Pallavi_ 1DAuyye5QOtbMQIIT6LjqddwR_T9PpVrh, Eshani_ 1tIgZEA1wfl5e18djNth7NImqtbjhtP46, Pehu_ 1yhc-591WKrqmTxyW1xG5QOubLD6r8Lwd (plus 1_rules_applied and 2_monthly_plan per person, same folder)
  - astro_workspace_backup_2026-11-13.zip (this handoff's backup: all engine code, backtest, book rules v2, panchang tools, logs). UNZIP FIRST when the workspace is empty.
- Daily plan logs: folder 176CIvIpXhlpqw8mVTCRNLNmQBzGy7x7Y (plan_<date>.txt, score_<date>.txt).
- Transcripts folder "YouTube Transcripts - Brajesh Gautam": 1oX9mn5fCK8AEnoCsQfxfiyZJ4VTOv2NT (flat; also holds the 00_* laptop package).
- Rules file for the daily task: astro_rules_and_method_v2.txt, id 1DfWA9U5RitMs2tx2Pfel-i7M2vkvpfx_.
- Source books in Drive (PDFs): "Lal Kitab - Brajesh Gautam ji" 1gZJspxeqhYjbX5gH_CSPVo0UGqSzHF--, "Lal Kitab Deepanshu Ji" 1k7HqV1TdFwwGn_U4ZMBE3dlLYriMxfeL, "Deepanshu Giri Sir Class Notes" 1YGk7GYiu05b5IH_riX_-TfEmuuV3h8XD, "Astrology_RAG_100_Books" 1x9QQkgBXwLKFWKTdzSrVTYazqFyWZOby, "Panchang & Classical Texts" 1dcIsvskZ5jbX-InyScBHa8iMV2q1_aPy, "Ancient Astro Secrets" 1wJRf1_QHMNe_2uBwp3CDNZaXxu65Dffp, "Books" 1AJh6VSZBMGWPbm8nKxWWlaDM3sh4r8xu. Key scans: Raman 1kOjpP5zQE9siHTXcBC4fh-mpE4CU6tYW; Dasha.pdf 1eMWy9cFxmpHc1AAynxrpCi4n35BBgsgk.

## 4. The code (local path /home/claude/astro, also in the backup zip)
Engine (folder engine/):
- jyotish.py: `Chart(name, local_datetime, tz_hours, lat, lon)`. Builds planets, lagna, Vimshottari / Yogini / Chara dashas, KP cusps + sub-lords, natal promise per life area, `dasha(t)`, `tpos(t)` transit positions, `tech_scores(t)`. Techniques scored separately: vim, kp, trans (double transit), chara, yog. Fixed a-priori weights W_TECH vim .30, kp .25, trans .30, chara .075, yog .075. Scores are z-scores against the same chart's own life (age 12-80, 10-day grid). They rank windows; they are not probabilities. LIMIT: scores only change on a ~10-day scale, so this engine cannot do day-level advice (it gave identical scores for 12-15 Nov 2026).
- engines.py: `windows()` (event + timing windows with agreement count, promise, confidence), `dos_donts(c,t)`, `remedies(c,t)` (traditional free remedies + Lal Kitab upay by planet-house + Gautam remedy text match), `report()`. CLI: `python engine/engines.py --name X --dob YYYY-MM-DD --tob HH:MM:SS --tz 5.5 --lat .. --lon .. --start YYYY-MM-DD --end YYYY-MM-DD --out file.txt`. Every report prints the backtest warning.
- bt_data.py (19 people, 158 events, birth data typed from memory, grade A/B), backtest.py, bt_results.json, PLAN.md, test_rajat.txt.
- Top-level helper modules in astro/: ac.py (core helpers), panchang.py, genpanchang.py (monthly panchang with flags), kp.py, lk.py, forward.py, rect.py, events_v2.py (Rajat dated events), people.py, make_report.py, etc.
- Daily panchang generator: genpanchang.py + panchang.py produce pan/astro_panchang_YYYY-MM.txt (Delhi, Lahiri). Flags: AVOID-NEW-START (Rikta tithi 4/9/14, tithi 6/8, Purnima, Amavasya), DAGDHA, VISHTI karana, nakshatra group + tara-bala, BAD YOGA, Chandrashtama, plus dual-moon-house and dual-rising-8th lines for the two lagna versions.

## 4b. JYOTISH SUITE v1 (the 4-engine software, built 13 Nov 2026)
- Code: astro/suite/ (rules.py unified loader of 12,119 rules; cond.py text-condition parser + matcher; suite_engines.py = Suite class with events(), timing(), do_dont(), remedies(), report(); run_suite.py CLI; backtest_rules.py; README.md; unparsed.tsv = the 9,171 rules not yet machine-readable).
- Run: `python astro/suite/run_suite.py --name X --dob YYYY-MM-DD --tob HH:MM:SS --tz 5.5 --lat .. --lon .. --start .. --end .. --on YYYY-MM-DD --out file.txt`.
- Drive: jyotish_suite_v1.zip (self-contained: code + rules, unzip into /home/claude) and 4 family reports Rajat/Pallavi/Eshani/Pehu_suite_2026-11-13.txt in the Family Vedic Analysis folder.
- Result: rule layer alone mean percentile 52.3 (z +1.0), top-20% 16% -> not better than chance. Label it a pattern organiser.
- Upgrade path: (1) raise parse coverage from 24% by handling more phrasings in cond.py (look at unparsed.tsv by frequency), (2) better area/polarity labelling, (3) frozen train/test weight fitting, (4) day-level layer using the panchang flags, (5) combine with transcripts rules when available.

## 5. Daily panchang for Rajat and the scheduled daily message
- TWO CHARTS are kept because birth time is uncertain by ~2 minutes: Chart A 05:39:04 lagna Leo 0 deg 25 min; Chart B 05:37:04 lagna Cancer 29 deg 59 min. Moon (Pisces 0 deg 37 min, Purva Bhadrapada-4) is the same in both. Tests could not separate A from B. Tag items [both], [Leo], [Cancer].
- Data: Drive folder panchang_daily 1qnKb0Cee6DRzcCjSEZ8_vZnNiZmHCJel. File ids: 2026-11 1IY9bp2Ll0_2O_FDRwYtWVS8ysBtqo7m4; 2026-12 1GIHHIb27UQDORp0x0BQTmzoYKt03VUQT; 2027-01 1x94X0z_KSokQdNAz8I9hJvrgDXzMqcXN; 2027-02 1pvtBx6j5VPzAKRx-vxkkTpJqM2DCdeCZ; 2027-03 1hBPKDOhwvvcg2ZMmiebjTAKzoii16BY3; 2027-04 1VsHX6BRhWazItUVyTjpDqAFCdtMgOEFm; 2027-05 1SzrnFIcsBhR0eLboz-dU0DGtLLKZdftJ; 2027-06 1JaHiiDsVRZdZXR_n8VOasJ5PyAkPHUfy; 2027-07 1KvSFWpBqbJ-A9gpEXUEOWhiq33-i4vRZ; 2027-08 1ybCmTDiVynx7LquO4QcoR_sqMgojKCIj; 2027-09 1chC3QlXuwyxdm6BvndZpCwyBxlSySeyx; 2027-10 1MdMi67-dWF7dqFM2RdrH5ECF2XfWTF6T; 2027-11 12k0C0fJCGLr7sAOR6C6pNqpwQWtBbw1b; 2027-12 1CD9AX0zRYaJBZ80ETBG16Tc95pgEQqim. Block per day starts "## YYYY-MM-DD". Checked against a web panchang for 12 Nov 2026 (within 2 min).
- Scheduled task: name "Daily plan for tomorrow (panchang)", id trig_01LURE7g3fGh64hBJYEHbXLt, runs every day 17:42 IST (message lands ~18:00), sends 3 DO + 3 AVOID + 3 MIGHT HAPPEN for TOMORROW, then logs plan_<date>.txt in the log folder. The user can reply hit/miss; save as score_<date>.txt. After 30 days compare hit rate of [both] vs [Leo] vs [Cancer]. Its full prompt is stored in the task (view with list_triggers).
- For "today" requests: open today's block in the month file (or pan/ locally), do NOT use the 10-day engine. Translate flags: avoid new starts in Rikta / Vishti / Rahu Kaal / Yamaganda / bad tara-bala / bad yoga; do important calls in Abhijit; finishing work in Ketu nakshatras.
- Key dates: 14 Nov 2026 Mercury/Venus direct; 15 Nov Pallavi Jupiter MD; 21 Nov Pehu Rahu-Ketu period; 6 Dec Rahu to Capricorn; 11 Dec Saturn direct; 13 Dec Jupiter retro; 14 Dec (A) / 21 Dec (B) Rajat Jupiter sub-period ends; Ketu on natal lagna point 12 Nov-17 Dec 2026; Jupiter on it 12-30 Jan 2027; Sade Sati (Saturn over Moon in Pisces) peak until early Jun 2027, Saturn back in Pisces 20 Oct 2027.
- Rajat now: Vimshottari Venus-Moon-Jupiter, Yogini Siddha-Dhanya, Chara (chart A) Pisces-Aquarius.
- Possible upgrade (user has not asked yet, I offered): write Do/Don't/Events text for every day of the 13 months into panchang_daily.

## 6. Rule databases
- Gautam: 5,259 rules (gautam_final_v2.jsonl; Drive in 3 parts). Quality check: 120 sampled, 58% exact, 41% small errors, 1% wrong. Source: ~60 transcripts of Brajesh Gautam.
- Other modules in db/raw (SRC_*, VER_*): Parashari, KP, Jaimini, K.N. Rao, Lal Kitab. Checks: Parashari 45% of 161 sampled confirmed vs BPHS/Phaladeepika; KP sub-lord table fully checked; Jaimini ~11% confirmed; K.N. Rao ~unverified (use only as extra); Lal Kitab best sourced but no timing.
- Books database v2: db/books_master_v2.jsonl = 2,120 rules, unique ids, no bad lines. Schema: id, system, engine_role, life_area, input, outcome, timing, strength_note, remedy, source, quote_short, confidence (all "book-claim"). Per book:
  - BK1 BVB course papers: 0 rules (question papers only, no answers)
  - BK2 392 rules: Marriage notes 1-2, Marriage Hindi, KP Chart (house-lord-in-house), Jaimini profession, Deepanshu yoga + karana notes, Lal Kitab notes HN1-HN9. Several are garbled OCR and hedged.
  - BK3 271: Prasna Marga part 1 (56) and 2 (97), Nadi (31), Ashtakvarga notes (29), KP Nakshatra Chintamani (58). Drive text was cut at ~110-173k chars so later chapters are missing.
  - BK4 367: Brihat Jataka (Iyer 1885 English), ~230k of 543k chars read.
  - BK5 1,090: Phaladeepika 464, Jataka Parijata 115, Saravali 312, Uttara Kalamrita 120, Jaimini Upadesa Sutras 79. Spot-check: 15 rules per book checked, 2 fixed. Partly read only (see books/BK5/log.tsv).
  - Per-book logs: books/BK*/log.tsv. Extraction instructions: books/instructions.md.
- Gaps: Raman and Dasha.pdf scans; unread chapters listed in logs; no book rule has yet been matched to a chart by code.

## 7. YouTube transcripts
- Scope: 22 playlists, 402 entries, 389 unique videos (13 repeats). Groups: BG Brajesh Gautam (3 playlists), DG Deepanshu Giri / Lunar Astro (8), PO Poonam Swami (3), SA Saptarishis Astrology (8). One off-topic video (Ic8ch0ivHhg, Lego).
- The cloud workspace CANNOT reach YouTube (403). Claude in Chrome can open YouTube but cannot move large text out reliably.
- Solution built: laptop package in Drive folder 1oX9mn5fCK8AEnoCsQfxfiyZJ4VTOv2NT: 00_README_INSTRUCTIONS.md, 00_get_transcripts.py (yt-dlp), 00_all_video_links.csv / .txt, 00_playlists.txt. Claude Desktop on the user's laptop runs it and uploads text files back (named GROUP_Pnn_pos_videoid_title.txt, plus report.csv). Not yet run. A copy of the prompt for Claude Desktop was given to the user in chat.
- Next after transcripts arrive: read each transcript, extract techniques + case studies (schema in yt/instructions.md; earlier agents DG1/DG2 produced yt/DG1/techniques.jsonl and cases.jsonl as examples), merge with other rules.

## 8. Backtest results (honest)
158 dated events, 19 public figures, 10-day windows, chance = 50.
- Average percentile rank of event date: vim 46.8, kp 48.1, trans 52.5, chara 53.4, yog 50.2, all combined 49.0.
- Top-20% window hit rate (chance 20%): vim 14%, kp 16%, trans 23%, chara 24%, yog 22%, all 18%.
- Domain specificity 48.8 (chance 50). Per area combined: career 61.0, children 58.0, marriage 46.5, status 39.2, foreign 46.8, setback 50.1.
- Weights were fixed before the test and not tuned afterwards (to avoid overfitting). Birth data and event dates came from my memory, which limits the test.
- Conclusion: no proven skill. If it stays near chance after adding book rules and a frozen train/test split, call the system a "pattern organiser", not a predictor. Every report must say this.
- Same message from Rajat's own life: 25 dated events, no rule beat random timing, and nothing separated chart A from B.

## 9. Family reports (yr/ folder, Drive family folder)
Per person: 1_rules_applied, 2_monthly_plan (12 months), 3_do_dont_predictions (10 Do, 10 Don't, 10 Predictions with date windows and confidence), plus <Name>_timeline. README method and limits: yr/00_README_method_and_limits.txt. Pallavi's lagna is also uncertain (Libra / Scorpio). Correction: older file family_two_lagna_analysis_2026-11-13.txt missed Rajat's Sade Sati peak; use the yr/ files.

## 10. Tool limits and lessons (so I do not repeat mistakes)
- Shell proxy blocks archive.org, YouTube, googleapis and transcript sites (403). Only package registries and GitHub work. Use Claude in Chrome for archive.org (fetch /stream/<id>_djvu.txt and read the <pre>).
- Chrome: javascript_tool returns ~1 KB; read big text by swapping document.body with a <pre> and calling get_page_text (30,000-char chunks). sessionStorage survives same-origin navigation. Trusted Types blocks innerHTML. Never run many agents each with their own Chrome tab (18 agents froze Chrome and lost everything): one tab, sequential.
- Drive: read_file_content truncates large PDFs and returns nothing for scans. create_file takes a base64Content file reference "sha256:<hex>:<abs path>", max ~3.1 MB per call. update_file cannot change content (trash + recreate). search_files has no "in parents" query; use parentId in the title-search form noted in the daily task prompt.
- Typed-from-memory data is unreliable: video IDs I retyped had 14 wrong ones, caught only by comparing with the live page data. Always verify by machine.
- No linked laptop in the cloud session (no device tools). Laptop work goes through Claude Desktop with files from Drive.

## 11. Plan - next steps in order
1. User runs the transcript package on the laptop (Claude Desktop prompt already given). Then: process transcripts into techniques/cases.
2. Merge Gautam + SRC modules + books v2 into ONE rule table with a common schema and source-strength weights.
3. Write the rule-matching layer: parse each rule's `input` into a condition (planet in house / sign, lord of house, dasha lord, transit) and test it against a Chart. Start with the simplest, most common patterns (planet-in-house, dasha-lord-house-lord) and count how many rules can be auto-coded.
4. Backtest again with a FROZEN train/test split (choose weights on half the people, check on the other half). Add more people and verified (grade A) birth data. Report plainly; do not tune until it passes.
5. Raman + Dasha.pdf: OCR (try tesseract in the workspace if the file can be downloaded; otherwise find an English text version on archive.org via Chrome, or ask the user for a text copy).
6. Day-level layer in the engine (Moon transit, tara, tithi, hora) and written Do/Don't/Events for each panchang day; keep logging hit/miss from the daily task.
7. Re-run family forward reports with the improved engine and replace the Drive copies.
8. Open questions to the user: "Narayan bhav" meaning; which Saptarishis teacher label for the Puja Sharma playlists; whether to extend the panchang beyond Dec 2027.

## 12. How to resume in a fresh session
1. Read this file (Drive: Family Vedic Analysis folder > MASTER_HANDOFF_2026-11-13.md).
2. If /home/claude/astro is missing, download astro_workspace_backup_2026-11-13.zip from the same folder and unzip into /home/claude. Needs `pip install pyswisseph` (2.10.03) and numpy.
3. Quick test: `cd /home/claude/astro/engine && python engines.py --name Rajat --dob 1975-08-24 --tob 05:39:04 --tz 5.5 --lat 25.1833 --lon 75.8333 --start 2026-11-13 --end 2027-11-13`.
4. Check the scheduled task with list_triggers, and the log folder for plan_/score_ files.
5. Update this file whenever something big changes (trash the old Drive file and create the new one, or add a dated change-log below).

## 13. Change log
- 13 Nov 2026 (later): Jyotish Suite v1 built and uploaded (section 4b).
- 13 Nov 2026: file created. Transcript laptop package uploaded. Books v2 (2,120 rules) merged. Backup zip created.
