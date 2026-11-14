# GUIDANCE RULES — written first, then coded (2026-11-14)

Purpose: a guidance tool. Output = DO, DON'T, PRECAUTIONS, in two layers:
- SHORT TERM: one window from one Sun sign change (ingress) to the next (about 30 days), with sub-windows for Mercury / Venus / Mars sign changes and dasha changes.
- DAILY: one day, from the daily panchang plus transits, measured against the person's BIRTH panchang.
Everything is plain code (no AI). Each item carries a rule id and a source. Everything is a tradition claim. Probability stays null until measured (see DIARY below).

## Inputs per person (from the Step 1 report)
- Birth panchang: birth nakshatra (for Tara Bala), natal Moon sign (for Chandra Bala and all gochara), birth tithi/yoga/karana (carried in the report).
- House influence (MAIN PART): each house has a main sign and minor sign(s) with shares (core/influence.py). Used to say WHICH LIFE AREA a transit touches, weighted by share.
- Ashtakavarga (BPHS plain), dasha table, natal rules fired by the weighted fit.

## A. Quality rules (is the transit good or bad?) — source: rules DB system 'gochara', book BK13
- GR-G1 (BK13_0001) Count every transit from the natal MOON sign, not from lagna.
- GR-G2 (BK13_0010-0017) Favourable houses from natal Moon: Sun 3,6,10,11 | Moon 1,3,6,7,10,11 | Mars 3,6,11 | Mercury 2,4,6,8,10,11 | Jupiter 2,5,7,9,11 | Venus 1,2,3,4,5,8,9,11,12 | Saturn 3,6,11 | Rahu and Ketu 3,6,11.
- GR-G3 (BK13_0005) A planet in the 11th from Moon is always favourable.
- GR-G4 (BK13_0003) Benefic in an unfavourable house: about neutral. (BK13_0004) Malefic in an unfavourable house: adverse. (BK13_0006) Malefic in 8th or 12th: maximum evil. (BK13_0007) Saturn over natal Moon sign: very bad.
- GR-G5 (BK13_0018, 0022-0028) Vedha: a favourable house is blocked when ANOTHER planet sits in its vedha house. Pairs are read from the DB text. Sun and Saturn never block each other; Moon and Mercury never block each other.
- GR-G6 (BK13_0020, 0021) Vipareeta vedha: a planet in a bad house is cancelled when another planet sits in the matching good house.
- GR-G7 (BK13_0029, 0030) Ashtakavarga: own bindus above 4 and sarva above 30 = favourable even in an evil house; evil house with own bindus below 4 and sarva below 30 = adverse. NOT applied: BK13_0031 (the sarva number is garbled in the book scan: 3 or 30).
- GR-G8 (BK13_0032-0035) Moorthi at a sign change: transit Moon from natal Moon at the ingress moment: 1,6,11 gold | 2,5,9 silver | 3,7,10 copper | 4,8,12 iron. Gold: benefics good, malefics adverse. Silver and copper: benefics average-to-good, malefics favourable. Iron: benefics bad, malefics average.
- GR-G9 (BK13_0038) Jupiter or Venus combust: no marriage, house-entering or new desire-driven rites. Orbs 11 deg (Jupiter) and 10 deg (Venus): classical values, NOT in the DB.
- GR-G10 Natural malefics: Sun, Mars, Saturn, Rahu, Ketu. Benefics: Moon, Mercury, Jupiter, Venus (simplified: no waxing/waning or association test). Hypothesis.
- NOT BUILT: BK13_0036 Tara of transiting planets. BK13_0037 says: combine with dasha and natal. We show dasha dates but do not combine them into a score.

## B. Area rules (which part of life is touched?) — MAIN PART
- GR-A1 A transit planet in sign S touches natal house h with weight = share of S in house h (house_influence shares, main and minor). Areas with weight below 0.15 are not shown. Main-sign areas are worded firmly; minor-sign areas are worded as "also lightly".
- GR-A2 House themes (hypothesis wording, ours): 1 self/health energy, 2 money/speech/family, 3 effort/short travel/siblings, 4 home/vehicle/mother, 5 children/study/creativity, 6 debts/health routine/rivals, 7 partnership/spouse/contracts, 8 sudden change/obstacles/hidden matters, 9 luck/father/long travel, 10 career/status, 11 gains/friends, 12 expenses/sleep/foreign.
- GR-A3 Quality (A) x area (B): good quality = "favourable for" the area; adverse quality = "be careful with" the area.

## C. Daily panchang rules — classical muhurta tables (NOT in the rules DB; source unverified, to be matched to books)
- GR-D1 Tara Bala: count = ((day nakshatra - birth nakshatra) mod 27) + 1; tara = count mod 9 (0 -> 9). 1 Janma (mixed, avoid new starts), 2 Sampat good, 3 Vipat bad, 4 Kshema good, 5 Pratyak bad, 6 Sadhana good, 7 Naidhana bad, 8 Mitra good, 9 Parama Mitra good. DB BK13_0036 also lists 1 as bad; we treat 1 as "mixed".
- GR-D2 Chandra Bala: day's Moon sign from natal Moon sign in 1,3,6,7,10,11 good, else weak (same list as GR-G2 for the Moon).
- GR-D3 Tithi (n = 1..15 within the half-month): Rikta 4, 9, 14 and Amavasya (30): avoid new starts. Ekadashi (11, 26): fasting day in tradition.
- GR-D4 Nakshatra class: Dhruva (Rohini, U.Phalguni, U.Ashadha, U.Bhadrapada): lasting starts. Chara (Punarvasu, Swati, Shravana, Dhanishta, Shatabhisha): travel. Mridu (Mrigashira, Chitra, Anuradha, Revati): arts, friendship. Kshipra (Ashwini, Pushya, Hasta): quick tasks, trade, learning. Ugra (Bharani, Magha, P.Phalguni, P.Ashadha, P.Bhadrapada) and Tikshna (Ardra, Ashlesha, Jyeshtha, Mula): avoid new starts, ok for forceful work. Mishra (Krittika, Vishakha): mixed.
- GR-D5 Yoga: inauspicious: Vishkambha, Atiganda, Shula, Ganda, Vyaghata, Vajra, Vyatipata, Parigha, Vaidhriti.
- GR-D6 Karana: Vishti (Bhadra) = half-tithi number n in 8, 15, 22, 29, 36, 43, 50, 57: avoid new starts while it runs.
- GR-D7 Rahu Kaal = 1/8 of daylight; part number by weekday Mon 2, Tue 7, Wed 5, Thu 6, Fri 4, Sat 3, Sun 8. Do not start new work or sign.
- GR-D8 Abhijit = 8th of 15 daylight parts: best window for important starts (some schools skip Wednesday).
- GR-D9 Day grade: count good and bad factors (Chandra, Tara, tithi, nakshatra class, yoga, Bhadra, Moon gochara result). favourable if net >= 2, careful if net <= -2, else mixed. It is a COUNT, not a probability.
- GR-D10 Weekday remedies: a fired natal remedy or don't rule whose text names today's weekday is shown today (max 3).
- NOT BUILT: Yamaganda, Gulika, Choghadiya, hora, panchaka, Sarvatobhadra, ruling planets (KP).

## D. Short-term rules
- GR-S1 Window = from one Sun ingress to the next, sidereal Lahiri. Show gochara quality of all 9 planets at the window start, Sun's moorthi (GR-G8), areas touched (GR-A1).
- GR-S2 Sub-windows: sign changes of Mercury, Venus, Mars inside the window, each with its quality and areas. Station (retrograde / direct) dates of Mercury, Venus, Mars, Jupiter, Saturn are listed as information only (no rule in the DB).
- GR-S3 Antardasha / mahadasha changes inside the window are listed with dates (+- 5 days).
- GR-S4 Combustion (GR-G9) adds don'ts.

## E. Output limits
- USER VIEW (Rajat 2026-11-14): exactly 3 DO and 3 DONT per person per day, and 3 DO and 3 DONT for the Sun-sign month. No predictions, no reasons, no rule ids, no precautions list. Reasons and rule ids stay inside the engine report. If fewer than 3 real items exist, show fewer; never pad.
- Safety filter (core/guidance.py BLOCK words) applies: no death, disease or investment items.
- No probability and no percent anywhere until the DIARY test passes.

## F. DIARY (the only way to get measured numbers)
- One row per person per day: date, person, rating 1-5 (how the day went), optional note. A Drive sheet filled from the phone.
- tune/diary_score.py compares the engine's day grade with the rating against a shuffled-days baseline. After about 90 days per person, report the measured result. Until then, no percentages.
