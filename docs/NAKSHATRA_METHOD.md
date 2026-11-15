# Nakshatra method (spec, written before code) - 2026-11-15

Goal: turn the English nakshatra books into checkable rules and apply them step by step to Rajat, Pallavi, Eshani, Pehu.

## Sources (English, archive.org)
- RK: Raj Kumar, Role of Nakshatra in Astrology (5 chunks)
- HN: Dennis Harness, The Nakshatras (3 chunks)
- SB: S.P. Bhagat, Significance of Stellar Astrology
- BN: The Book of Nakshatras (fetch was refused by the tool allowlist on chunk 2; see status)
- Merlin: Lunar Mansions in Vedic Astrology (not yet run)
Rules are paraphrased, never copied. Each rule keeps book + position.

## Step-wise method
1. Identity table (data, no book needed): 27 nakshatras x lord, deity, gana, yoni, nadi, varna, vashya, guna, pada navamsa signs. Facts from books are compared with it; any mismatch goes to notes, not silently resolved.
2. Extraction: agents write rules.jsonl (id NK<book>_<chunk>_<seq>) and facts.jsonl per chunk into astro/nk/.
3. Conversion: same AI atom pipeline as other rules (PROMPT.md vocabulary, strict validator). Only complete + valid atoms run. Others stay in the ledger as not runnable.
4. Chart facts per person: Moon nakshatra and pada, lagna nakshatra, nakshatra of each planet, dasha lord's nakshatra, janma/anu-janma/trijanma nakshatras.
5. Fire rules: planet_in_nak and related atoms against the chart, with the multi-view fit.
6. Day level: Tara bala and Chandra bala of the day's Moon nakshatra against the person's birth nakshatra (counted from janma nakshatra, 9 taras).
7. Output: feeds the same 3 DO + 3 DON'T. No reasons shown. Reasons stay in engine JSON.
8. Ledger: re-run tune/coverage.py. Do not say complete unless the ledger says so.

## Limits
- Accuracy not measured. Book claims are tradition claims.
- Books disagree (e.g. RK itself lists two lords for Ashwini in different places). Disagreements are kept as notes.

## Built 2026-11-15
- core/nakshatra.py: table (lord, gana, yoni, nadi), of_lon, natal_signals (janma, lagna, every planet's nakshatra+pada, anu-janma, trijanma, 9 taras), day_signals (tara, chandra bala, janma/anu/tri days).
- guide.py puts it in the engine JSON per person under 'nakshatra'. The user view (3+3) is unchanged.
- tune/nak_facts_check.py: book facts vs table. Result: 250 agree, 4 differ only in animal names (goat/sheep, leopard/tiger).
- Merlin not run: its URL was not found. BN refused by fetch allowlist.
- Known limit: lagna nakshatra depends on exact birth time (a few minutes can change the pada, near sign start the nakshatra).

## Activation ages (2026-11-15)
- core/activation.py. Planet maturity ages: two web schemes kept apart (they conflict, e.g. Jupiter 16 vs 33-34). Both from secondary pages (panchangbodh calculator; Sanjay Rath's table as quoted on a blog). No primary verse found. Ptolemy's life-stage table is a different idea and is not used.
- Nakshatra ages: 31 statements for 22 of 27 nakshatras, taken from the three nakshatra books (rules/nakshatra_ages_v1.jsonl, tune/make_nak_ages.py). 5 nakshatras have none. No book was found that gives a per-nakshatra activation age as a system; these are scattered "struggle until / golden period" claims.
- Output: engine JSON 'activation' per person. Not used in the 3 DO + 3 DONT.
