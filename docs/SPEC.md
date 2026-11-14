# Astrology Engine: Master Concept Specification (v1, 2026-11-14)

Principle: the SOFTWARE is plain code. Inputs go in, if/then and maths run, a detailed REPORT comes out. Every number in the report has: method name, source tag, formula or rule used, inputs used. The AI never calculates; it only reads the report (and the measured validation record of each technique) and writes inference.
Rule: nothing is assumed. Where traditions differ, every variant is computed and labelled; none is silently chosen. Where a concept is unclear, it is listed under OPEN QUESTIONS and not coded until settled.

Status key: DONE = coded and tested; PART = coded, not fully tested or not all variants; TODO.

## ARCHITECTURE DECISION (owner, 2026-11-14)
Calculation layer = PyJHora (open-source port of Jagannatha Hora, by Sundar Sundaresan, licence AGPL-3.0-or-later). Our software does NOT recalculate what PyJHora already gives (positions, divisional charts, dashas, panchang, transits, Ashtakavarga where available). Our code = the ANALYSIS layer: reference frames, house/sign equivalence, rule and technique evaluation, report assembly, validation. Our own M1-M8 code stays only as an independent regression check against PyJHora, never as the source of record.
Conditions: pin the PyJHora version; record every PyJHora setting in each report; verify each PyJHora module we depend on before use (positions/ascendant/D9 done, 001); check the AGPL implications before any commercial use.

## M0 Inputs and time
- Birth date, time, place (lat, lon, altitude), gender; time zone WITH historical changes (DST, war time, LMT before standard time); source and Rodden grade of the birth time. TODO (tz history is currently trusted from input)
- Birth-time sensitivity: recompute at +/- 1, 5, 15 min; mark each fact stable or fragile. TODO
- Ayanamsa options: Lahiri, KP (Krishnamurti), Raman, Fagan-Bradley, True Chitra, Yukteswar, tropical (none). PART
- Node: mean and true Rahu/Ketu, both stored. PART
- Julian day, Delta-T, ephemeris source. DONE (Swiss Ephemeris)

## M1 Positions and planetary condition
- Bodies: Sun to Saturn, Rahu, Ketu; Uranus, Neptune, Pluto; Chiron and main asteroids (Ceres, Pallas, Juno, Vesta); Lilith (mean, true); Vertex, East point. PART
- Upagrahas: Gulika and Maandi (day/night, prahara based), Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu; Kala, Mrityu, Artha-prahara, Yamaghantaka. TODO
- Per body: longitude, latitude, declination, speed, retrograde, stationary, nakshatra, pada, sign, degree in sign, KP star lord and sub lord and sub-sub lord. PART
- Combustion (distance from Sun, per planet, direct vs retrograde, all variants); planetary war (graha yuddha, winner rule variants); cazimi. TODO
- Dignity: exaltation, debilitation, moolatrikona, own sign, natural friend/enemy/neutral, temporary friendship, compound (panchadha) relationship; deep exaltation/debilitation degree; Neecha Bhanga (all conditions listed in sources); Vargottama; Pushkara navamsa and Pushkara bhaga. PART
- Avasthas: Baladi (5), Jagradadi (3), Deeptadi (9), Lajjitadi (6), Shayanadi (12). TODO
- Special degrees: Gandanta, sign and nakshatra junction (sandhi), Mrityu bhaga, Sarpa/dagdha degrees, critical degrees (0, 29), anaretic degree, Sun-Moon eclipse degrees. TODO
- Strength: Shadbala (sthana, dig, kala, cheshta, naisargika, drik), Ishta/Kashta, Bhava bala, Vimsopaka bala, Digbala alone. TODO
- Ashtakavarga: BAV (7 planets + lagna), SAV, prastara, trikona and ekadhipatya sodhana, shodhya pinda, rasi and graha pinda, kakshya. PART (BAV tables and checksum done)
- Western: essential dignities (domicile, exaltation, triplicity, term/bound, face; detriment, fall), accidental dignities, dispositors, final dispositor. TODO

## M2 Zodiac, houses, reference frames (Module A)
- Natural zodiac: house N <-> sign N (Kalapurusha). DONE (zodiac.py)
- House systems: whole sign, equal (asc as start), equal (asc as middle), Sripati bhava chalit, Porphyry, Placidus; Koch, Regiomontanus, Campanus, Alcabitius to add. DONE for six; TODO others
- Per house: start, middle, end, all signs spanned with degrees, planets inside under each system. DONE
- Boundary flags (planet within 1 degree of a sign or house edge). TODO
- Reference frames: lagna, Moon, Sun, Aries-fixed (Lal Kitab), any planet, karaka (Jaimini, Bhavat Bhavam). PART
- House classes: kendra, trikona, dusthana, trik, upachaya, maraka, apoklima, panapara, chara/sthira/dwiswabhava; bhavat bhavam; natural karakas (sthira) and per-house karakas. TODO
- Lagnas: Janma, Hora, Ghati, Bhava, Varnada, Indu, Sri, Pada (Arudha), Karaka lagna; Chandra lagna, Surya lagna; Sudarshana chakra (three-lagna reading). TODO

## M3 Relationships between planets and houses
- Parashari graha drishti: 7th for all; special Mars 4/8, Jupiter 5/9, Saturn 3/10; Rahu/Ketu variants (all variants stored); fractional drishti (1/4, 1/2, 3/4, full) and drishti bala in virupas. PART
- Rashi drishti (Jaimini): movable-fixed, dual-dual pairs. DONE (in chara code)
- Lal Kitab drishti scheme (own aspect table) and Lal Kitab "takkar/sathi" relations. TODO
- KP relations: star lord, sub lord, 4-step significators (occupant's star lord, occupant, owner's star lord, owner). PART
- Conjunctions: same sign, same house (per system), same nakshatra, orb-based degree distance, exact (under 1 degree), with applying/separating; three or more planets (stellium). PART
- Western aspects: conjunction 0, semisextile 30, semisquare 45, sextile 60, quintile 72, square 90, trine 120, sesquiquadrate 135, biquintile 144, quincunx 150, opposition 180; configurable orbs; applying/separating; out-of-sign aspects; parallels and contra-parallels (declination); antiscia and contra-antiscia; midpoints and 90-degree dial. TODO
- Aspect patterns: grand trine, T-square, grand cross, yod, kite, mystic rectangle, stellium. TODO
- Mutual relations: parivartana (sign exchange, 3 kinds), mutual aspect, mutual reception, nakshatra exchange, sambandha (4 kinds), kartari (shubha/papa), vedha, argala and virodhargala. PART
- Sign lord chains, dispositor trees, planet in another planet's nakshatra (nakshatra lord chain). PART

## M4 Divisional and derived charts
- Parashari 16 vargas: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60; plus D5, D6, D8, D11, D81, D108, D144, D150 (Nadiamsa). Every division method variant kept (for example D2 Parashara hora vs Jaimini, D3 variants, D30 unequal). PART (D9, D10 only)
- Per chart: all body positions, dignity there, aspects, yogas there, lord strengths. TODO
- Sensitivity: D27 and above need minute-level birth time; mark fragile. TODO
- Other charts: Bhava chalit chart, Moon chart, Sun chart, Arudha chart, Karakamsa chart, Narayana (sign) chart per Sanjay Rath convention to be confirmed, sayana (tropical) chart, KP chart, draconic chart, harmonic charts (H5, H7, H9). TODO
- Progressed and return charts: solar return (Varshaphala, Tajaka), lunar return, secondary progression, solar arc, tertiary progression, primary directions, annual profection, Lal Kitab annual chart. PART (solar return, BCP age house)

## M5 Yogas and combinations (rules engine over M1 to M4)
- Pancha Mahapurusha; Gajakesari; Budhaditya; Chandra-Mangala; Raja yogas (kendra-trikona lord links, all variants); Dhana yogas; Viparita Raja; Neecha Bhanga Raja; Kemadruma; Sunapha, Anapha, Durudhura; Vasi, Vesi, Ubhayachari; Nabhasa (32: Akriti, Sankhya, Ashraya, Dala); Saraswati, Lakshmi, Amala, Parvata, Kahala, Chamara, Shankha, Bhadra, Hamsa, Malavya, Ruchaka, Sasa; Daridra; Sanyasa; Arishta and Balarishta; Maraka; combinations of 2 to 6 planets (Saravali). PART
- Doshas: Mangal/Kuja (from lagna, Moon, Venus, with cancellations), Kala Sarpa / Kaal Amrit, Pitru, Guru Chandal, Shrapit, Grahan, Kemadruma, Sade Sati, Dhaiyya, Ashtama Shani. PART
- Lal Kitab structures: pakka ghar, kayam grah, dharmi/ andha / nabalig teva, sleeping planets, masnui grahas, rin (all nine), saathi, mukabale. PART
- Source rule base: 19,575 rules in books_master_v6. Each rule must be translated into a precise condition on the M1 to M4 facts (the current bottleneck, about 25% translated). PART

## M6 Time systems (dashas and others)
- Vimshottari to 6 levels, with year-length variants (360 / 365.242 / 365.25 days), balance at birth, sandhi. DONE (to 3 levels)
- Yogini; Ashtottari (and its applicability conditions); Kalachakra; Dwisaptati sama; Shatabdika; Panchottari; Shodashottari; Dwadashottari; Satamsa; Shashtihayani. PART (Yogini; others TODO)
- Rashi dashas: Chara (Jaimini; K.N. Rao and Parashara variants), Narayana, Sthira, Kendradi, Drig, Trikona, Shoola, Brahma, Mandooka, Paryaya, Navamsha, Yogardha. PART (Chara only)
- Tajaka: Muntha, Varsheshwar, Mudda dasha, Patyayani. PART
- Age-activation rules: planet maturity ages (variants), Lal Kitab 35-year cycle, BCP age house, nakshatra-dasha age of onset, annual profection house. PART
- Longevity: Pindayu, Nisargayu, Amsayu, Jaimini longevity methods. TODO
- Lord-of-period strength: functional benefic/malefic per lagna, yogakaraka, karaka, placement, aspects, dignity, its own M5 yogas. TODO

## M7 Panchang for the day (C)
- Tithi, vara, nakshatra and pada, yoga, karana, paksha, lunar month (amanta and purnimanta), samvatsara, ritu, ayana, Moon sign; start and end times; sunrise, sunset, moonrise, moonset at the place; day length. PART
- Hora, choghadiya, Rahu kala, Gulika kala, Yamaganda, Abhijit muhurta, Brahma muhurta; special yogas (Sarvartha Siddhi, Amrit Siddhi, Ravi yoga, Dwipushkar, Tripushkar, Guru Pushya, Panchak, Bhadra/Vishti, Gand mool, Tithi shunya, Chandrashtama). PART
- Against birth chart: tara bala (9 taras), chandra bala, janma-nakshatra relations, Sarvatobhadra vedha, Kota chakra. TODO
- Muhurta factors, vrata and festival dates, eclipses on or near the day. TODO

## M8 Transit for the day (D)
- Positions of all bodies, speed, retrograde, ingress dates, nakshatra and pada, KP star and sub lord. PART
- Transit house from lagna and Moon; Gochara results with vedha; Ashtakavarga bindu in the transit sign; Sade Sati, Dhaiyya, Kantaka/Ashtama Shani; Jupiter-Saturn double transit; transit contacts to natal positions with orb (Vedic aspects and Western aspects); Saturn, Jupiter and node returns; lunations and eclipses over natal points. PART
- Transits in divisional charts and in the dasha-lord's frame (K.N. Rao style gochara over dasha lords). TODO
- Planetary stations, combustion and war during the transit. TODO

## M9 Method packs (each its own methodology, kept separate and labelled)
- Parashari (BPHS): all of M1 to M8 as written there.
- Jaimini: chara karakas (7 and 8 karaka schemes), Karakamsha, Swamsha, Arudha padas A1 to A12 (and exceptions), Upapada, Darapada, argala, rashi drishti, Jaimini raja yogas, chara dasha, longevity, sutra rules. PART
- KP (Krishnamurti): Placidus with KP ayanamsa, 249 sub-divisions, star-sub-sub, cuspal sub lord, significators, ruling planets, event conditions (promise, then timing via dasha-bhukti-antara plus transit), horary number 1 to 249, Badhak. PART
- Lal Kitab (Roop Chand Joshi): fixed houses, planet in house, teva types, rin, remedies, nishaniyan, varshphal, ages, blind and sleeping planets, aspects of its own. PART
- Bhrigu and Nadi: Bhrigu Samhita, Bhrigu Nandi Nadi (planet linkages by trine and 7th, karakas, Jupiter and Saturn transit triggers), Bhrigu bindu, Bhrigu Chakra Paddhati, Chandra Kala Nadi, Saptarishi Nadi, Dhruva Nadi, Nadiamsa D150. Rules to be taken ONLY from sources read, none assumed. TODO
- K.N. Rao: his method for timing (dasha lord plus transit of Jupiter and Saturn over key points), chara dasha practice, children, marriage, career rules, from the books read. PART
- Tajaka (annual): solar return, Muntha, Varsheshwar, Panchavargiya bala, 16 Tajaka yogas (Ikkabal, Induvara, Ithasala, Eesarapha, Nakta, Yamaya, Manaoo, Kamboola, Gairi-Kamboola, Khallasara, Radda, Duphali-kuttha, Tambira, Kuttha, Durupha), Sahams (Arabic lots: Punya, Vivaha, Putra, Karma, and others). PART
- Prasna (horary): Prasna Marga, Swara, Arudha, KP number; question chart rules. PART
- Western: tropical zodiac, Placidus/Koch/Regiomontanus houses, outer planets and asteroids, aspects and orbs, patterns, essential and accidental dignities, antiscia, midpoints, Uranian dial, progressions, solar arc, returns, transits, eclipses, fixed stars, Arabic lots, synastry and composite, planetary hours. TODO
- Relationship and matching: Ashtakoota/Guna Milan (8 kootas, 36 points), Dashakoota, Nadi dosha, Bhakoot dosha, Mangal matching, synastry. TODO
- Other: medical astrology, Muhurta (election), mundane, financial and business timing. TODO

## M10 Report assembler
- One deterministic report per chart: sections by method; each fact with method, source tag, formula, inputs, house system, ayanamsa, stability flag; list of fired techniques with evidence; list of variants that disagree. TODO
- The report carries the measured validation record of each technique alongside its firing (from Stage 1). TODO

## M11 Verification
- Unit tests per function with hand-checkable cases. PART (houses)
- Cross-check against published charts from the books and classes (positions, divisional signs, dasha dates, panchang for known dates, ashtakavarga totals). TODO
- Regression suite: any change must reproduce earlier reports for a fixed set of charts. TODO

## Concepts the first brief did not name, now added
Upagrahas (Gulika/Maandi etc.); combustion, graha yuddha, avasthas; Shadbala and Ishta/Kashta; special degrees (Gandanta, Mrityu bhaga, Pushkara); Sudarshana chakra; Sahams/Arabic lots; Kalachakra and the other dashas; longevity methods (Pindayu etc.); Ashtakoota matching; Sarvatobhadra, Kota chakra, tara and chandra bala; Muhurta; Prasna and KP horary; antiscia, midpoints, parallels, aspect patterns; fixed stars; progressions, solar arc, profections, draconic and harmonic charts; synastry; birth-time sensitivity and ayanamsa/node variants.

## OPEN QUESTIONS (need the owner's decision, nothing coded until answered)
1. "Narayana chart" and "sayan chart": confirm meaning (Narayana dasha sign sequence per Sanjay Rath? sayana = tropical chart?).
2. Ayanamsa: LAHIRI APPROVED by owner (2026-11-14) as the default. Not yet answered: whether KP should also use Lahiri or the Krishnamurti ayanamsa (until answered, KP is computed under both and labelled); Western stays tropical.
3. Node default per pack (both stored always). Verification 001 found PyJHora defaults to TRUE node and geometric positions; our old engine used MEAN node and apparent positions. Owner to choose defaults.
4. Which variant of each divisional chart to treat as primary where sources disagree.
5. Which birth-time grades (AA, A, B, SELF) may be used for which charts.

## Build order
M0 (tz history, sensitivity) -> M1 (condition and strength) -> M2 (done, extend) -> M3 -> M4 -> M7 and M8 (panchang, transit) -> M6 -> M5 (yogas, then translate rules) -> M9 packs one by one -> M10 -> M11 throughout.

## Verification log
- 001 (2026-11-14): ascendant and planets match PyJHora to within 51 arc-seconds (cause identified: geometric vs apparent positions); nodes differ by setting (true vs mean); D9 signs agree except nodes. See ref/VERIFY_REPORT_001.md. Old engine crashes above 66 degrees latitude.
