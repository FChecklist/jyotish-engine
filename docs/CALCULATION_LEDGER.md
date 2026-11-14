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

## Step 3 spec (written before code): AI-assisted conversion of rule text into atoms (Rajat approved Option A, 2026-11-14)
Principle: AI is used ONLY as a translator during the build. The running software is plain code. Nothing the AI writes is trusted until code validates it and an audit measures its error rate.
- Format (JSON, one object per rule): {"id", "atoms": [...], "complete": true|false, "missing": "text"}.
- Atoms (the only ones the engine can run): planet_in_house{p,h[]}, planet_in_sign{p,sign}, lord_in_house{n,h[]}, conj{p,q}, planet_in_group{p,g}, dignity{p,s}, aspects_house{p,h[]}, aspects_planet{p,q}, dasha{p,level}, dasha_house_lord{n}, plus wrappers any{of:[atoms]} (OR) and not{of:atom}. Planets: Sun Moon Mars Mercury Jupiter Venus Saturn Rahu Ketu. Dignity only for the first seven.
- "complete": true ONLY if the atoms capture the WHOLE condition of the rule. A rule that is a definition, a description or advice without a chart condition is atoms [] and complete false. If any qualifier cannot be expressed (strength, degrees, named yoga, nakshatra, tithi, retrograde, etc.), complete is false and "missing" names it. Never invent. Never drop a qualifier silently.
- Code validation (core/atoms_store.py): strict schema, planets/houses/signs in range, no unknown atom. An invalid entry is rejected and counted. Only valid and complete entries are executed. They carry origin "ai_v1" so every report can separate parser-read from AI-read rules.
- Audit before trust: (1) GOLD test: 150 rules the regex parser already reads are converted blind by the AI; exact match with the parser = measured accuracy on easy rules. (2) HARD test: 150 unread rules converted independently twice; agreement rate; plus hand audit of a sample. (3) Rule for the full run: only proceed if gold accuracy and hard agreement are high enough to be useful; otherwise stop and report. Final per-rule error rate is published in docs/RESULTS.md.
- NOT trusted for: any rule marked complete false; any rule whose two passes disagree (full run uses two passes and keeps only agreeing entries).

## Step 4 spec (written before code): more atoms, so more rules can run
Context: the pilot showed most unread rules need things the engine could not check. New atoms (all plain code, tested):
- ('planet_from', p, ref, houses): p is in the Nth sign counted from planet ref (Moon, Sun, any planet; counted in signs, so the house views do not change it). "Jupiter in 5th from Moon". Not used for "from lagna" (that is planet_in_house).
- ('planet_in_nak', p, naks): p's sidereal longitude is in nakshatra n (1 Ashwini .. 27 Revati), 13 deg 20 min each. Needs longitudes (ctx lon).
- ('retro', p): p retrograde at birth, p in Mars..Saturn. Needs the birth retro flags (ctx retro). Sun, Moon never; nodes not used.
- ('combust', p): p within the orb of the Sun, p in Moon..Saturn. Orbs (classical, hypothesis): Moon 12, Mars 17, Mercury 14 (12 if retro), Jupiter 11, Venus 10 (8 if retro), Saturn 15.
- ('yoga', name): position-only named yogas, defined exactly:
  - gajakesari: Jupiter in a kendra (1, 4, 7, 10th sign) from the Moon.
  - budhaditya: Sun and Mercury in one sign. chandra_mangala: Moon and Mars in one sign.
  - guru_chandala: Jupiter with Rahu. shrapit: Saturn with Rahu. angarak: Mars with Rahu. grahan: Sun or Moon with Rahu or Ketu.
  - kemadruma: none of Mars, Mercury, Jupiter, Venus, Saturn in the Moon's sign, the 2nd or the 12th from it (basic form; cancellations not applied).
  - sunapha / anapha / duradhara: one of Mars..Saturn in the 2nd / the 12th / both from the Moon.
  - vesi / vosi / ubhayachari: one of Mars..Saturn in the 2nd / the 12th / both from the Sun.
  - ruchaka (Mars), bhadra (Mercury), hamsa (Jupiter), malavya (Venus), sasa (Saturn): the planet is in its own or exalted sign AND in a kendra from lagna, judged in each house view (multi-sign).
  - NOT built: raja yoga, dhana, viparita, neecha-bhanga and any yoga that needs house lords, strength or cancellation rules.
- Rules that still need strength (shadbala), transits, Lal Kitab states, tithi/weekday stay partial.
- Context object passed to fit: ctx = {lon, retro, maha, antar}. An atom whose data is missing is NOT evaluated (fit None), never guessed.
