# CALCULATION LEDGER — nothing is left out silently (2026-11-14)

Rajat's rule: "don't leave any calculation minor or major." Meaning in practice:
1. Every rule in the databases (books 24,171 + Gautam transcripts 5,259) is sorted by the calculation it needs (tune/coverage.py). Counts only, no personal data.
2. For each kind of calculation the engine says: built, partial, or NOT BUILT, with the module that does it. Nothing is claimed that the ledger does not show.
3. A rule the parser cannot read is never dropped and never guessed. It stays in the database as "unparsed" or "partial" and is listed here by count.
4. Each build step adds atoms to the parser (core/rules_norm.py), the weighted fit (core/influence.py, MAIN PART: multi-sign houses), a test, then the ledger is re-measured.
5. "Complete" is judged only by the ledger numbers going up. Accuracy is a separate question (docs/RESULTS.md).

## Atoms added in this step (spec written before code)
- DIGNITY atom ('dignity', planet, state), D1 sign only. States are a SET per planet-sign: exalted, debilitated, own (own sign, including moolatrikona sign), friend, neutral, enemy. A planet can be in two states (Mercury in Virgo is exalted and own).
  - Exaltation signs: Sun Aries, Moon Taurus, Mars Capricorn, Mercury Virgo, Jupiter Cancer, Venus Pisces, Saturn Libra. Debilitation = the opposite sign.
  - Own signs: Sun Leo; Moon Cancer; Mars Aries, Scorpio; Mercury Gemini, Virgo; Jupiter Sagittarius, Pisces; Venus Taurus, Libra; Saturn Capricorn, Aquarius.
  - Friend / neutral / enemy sign: natural relation (BPHS) between the planet and the lord of the sign it sits in. Friends: Sun (Moon, Mars, Jupiter); Moon (Sun, Mercury); Mars (Sun, Moon, Jupiter); Mercury (Sun, Venus); Jupiter (Sun, Moon, Mars); Venus (Mercury, Saturn); Saturn (Mercury, Venus). Enemies: Sun (Venus, Saturn); Moon (none); Mars (Mercury); Mercury (Moon); Jupiter (Mercury, Venus); Venus (Sun, Moon); Saturn (Sun, Moon, Mars). Everything else neutral.
  - Rahu and Ketu: schools disagree on their exaltation and own signs, so no dignity atom is made for them. Such rules stay partial.
  - NOT built: moolatrikona degree ranges, temporary friendship, compound (panchadha) relation, deep exaltation degree.
- ASPECT atoms: ('aspects_house', planet, houses) and ('aspects_planet', planet, planet). Whole-house graha drishti counted in each house VIEW (so multi-sign influence applies): every planet aspects the 7th from itself; Mars also 4th and 8th; Jupiter also 5th and 9th; Saturn also 3rd and 10th; Rahu and Ketu 5th, 7th, 9th (hypothesis: schools differ). "A aspected by B" = B aspects A. Lal Kitab frame uses sign numbers from Aries.
  - NOT built: aspect orbs and strength, Jaimini rashi drishti, KP aspects.
- NOT built in this step (listed in the ledger): retrograde and combust at birth (needs speed in the natal chart), named yogas, Jaimini, shadbala/avastha, Lal Kitab states, annual (Tajika), doshas, upagrahas.

## Ledger (measured 2026-11-14 after dignity and aspect atoms)
Total rules: 29430 (books + Gautam). Parser status: parsed 3965, partial 7679, unparsed 17786.
Parsed share: 13.5% (was 13.1% = 3,844 before this step; +121 rules).

| kind of calculation | rules touching it | rules needing only it | engine status | what exists |
|---|---|---|---|---|
| transit | 998 | 195 | partial | core/gochara.py (BK13 gochara rules only); free-text transit rules not parsed |
| dasha | 3287 | 1136 | partial | vimshottari dates only; no rule-to-period linking; no other dashas |
| ashtakavarga | 743 | 75 | partial | core/ashtakavarga.py (tables); bindu rules only in gochara |
| divisional | 2255 | 293 | partial | core/charts.py computes D1-D60; rules on them not applied |
| aspect | 3134 | 946 | partial | aspect atoms in rules_norm |
| dignity | 3879 | 1272 | partial | dignity atom, sign-based |
| conjunction | 2842 | 1182 | partial | conj atom (two planets in one sign) |
| placement | 4951 | 2179 | built | rules_norm + influence.fit (weighted) |
| panchang | 594 | 199 | partial | core/panchang.py + daily.py (Tara, Chandra, tithi, nak class, yoga, Bhadra, Rahu Kaal, Abhijit); rest not built |
| yoga_named | 989 | 408 | not_built | no named-yoga detector |
| jaimini | 1180 | 310 | not_built | no Jaimini engine (karakas, arudha, argala) |
| kp | 143 | 54 | partial | core/kp.py lords; significators and cusp rules not built |
| strength | 3825 | 1663 | not_built | no shadbala or avastha |
| annual_tajika | 358 | 110 | not_built | no annual chart engine |
| lalkitab_state | 2628 | 797 | not_built | Lal Kitab states and debts not built |
| nodes_eclipse | 249 | 103 | not_built | no dosha detectors, no Sade Sati helper |
| upagraha_other | 326 | 87 | not_built | no upagraha or special-degree engine |
| other_text | 9830 | 9830 | not_built | free text; needs reading, not keyword |

A rule can touch several kinds. 'other_text' = free-text rules with none of the known calculation words: they need to be read and turned into atoms, not matched by keyword.
Honest reading: the new atoms work (tests pass) but add only 121 fully parsed rules, because most dignity/aspect rules carry extra conditions or different wording. The biggest unread blocks are the free-text rules (9,830), strength (3,825), dasha (3,287), Lal Kitab states (2,628), Jaimini (1,180).

## Step 2 spec (written before code): DASHA atoms
- ('dasha', planet, 'maha'|'antar'): the rule only holds while that planet runs that level of Vimshottari at the date asked. Phrases: "Venus dasha / mahadasha", "Saturn antardasha / bhukti / sub-period".
- ('dasha_house_lord', n): "dasha of the 7th lord", "7th lord dasha": holds while the maha OR antar lord rules a sign of house n. The sign set of house n comes from the multi-sign house influence, so a lord counts in proportion to the share of its sign in that house (MAIN PART). Hypothesis: maha or antar either counts.
- Needs a date. Without a running-dasha context a dasha rule is NOT evaluated (fit = None). It is never treated as true or false by guess.
- A dasha rule combined with natal atoms ("Saturn in 8th during Saturn dasha") needs all atoms true.
- Dasha-linked rules with a remedy or a don't feed the short-term DO / DON'T pool (weight 4 x fit). Outcome-only rules stay in the engine report.
- NOT built: other dasha systems (Yogini, Chara, Narayana), pratyantar, dasha lord strength, dasha sandhi rules beyond the date caution.

## Ledger after step 2 (dasha atoms), measured 2026-11-14
- Parsed 4,585 of 29,430 (15.6%); partial 7,898; unparsed 16,947. (Step 1 ended at 3,965; step 2 added 620.)
- One chart (full books + Gautam run, as of 14 Nov 2026): 4,585 rules evaluated, 419 fired, 4,166 evaluated and not fired, 0 waiting for a date. The other 24,845 are loaded but NOT executed (partial or unparsed). The report now carries this count (rules_ledger) for every person, so no rule is silently skipped.
- Per source for that chart: parashari 11,990 loaded / 1,746 evaluated; lalkitab 6,224 / 2,290; gautam 5,259 / 245; other 3,061 / 235; prasna 1,207 / 20.
- THE GAP: rules are all stored; only 15.6% can be executed. Executing the rest means converting each rule's text into atoms. Keyword matching is hitting its limit; the remaining rules need a reading step (see docs/DECISIONS.md 2026-11-14 night 2).
