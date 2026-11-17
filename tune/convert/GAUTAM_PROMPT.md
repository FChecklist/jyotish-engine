# Task: read one slice of a Brajesh Gautam astrology lecture, sentence by sentence, and write structured notes

Input: INFILE (Hindi YouTube auto-captions with [timestamps]; captions are noisy, English words are spelled in Devanagari, numbers can be wrong).
Output: OUTFILE (JSON lines, one object per line, UTF-8). Work in your own scratch dir /tmp/claude-0/g1_<batch>/ . Do NOT write any script that generates the meaning text. You write every `says` and `derived_method` yourself, from understanding. No web search. Use your own knowledge of Jyotish.

Read INFILE completely, in order, with the Read tool (in parts if needed). Go sentence by sentence. EVERY sentence ends up in exactly one row. Nothing is left out.

## Row types
1. Statement rows (astrology content: rules, definitions, planet/house/sign facts, timing, remedies, vastu-link claims):
{"id":"G<VID>-<batch>-<nnn>","type":"stmt","ts":"1:23:03","hindi":"<the source sentence or two, copied, max 40 words>","says":"<plain English: what he is claiming. Understand it, do not translate word by word>","kind":"rule|definition|remedy|timing|karaka|principle|other","scope":["planet","house","sign","planet+house","planet+sign","planet+house+sign","aspect","dasha","transit","chart-wide","remedy","other"],"planets":["Mars"],"cells_stated":[["*","Aries"]],"cells_derived_method":"<how the meaning changes across the other house/sign cells, using classical house topics x sign nature x planet nature. Say 'none' if the sentence is not house/sign dependent.>","derived_examples":[{"cell":["10","Cancer"],"reading":"<one concrete derived reading, labelled as derived, not said by him>"}],"charts":["D1","D9","bhava-chalit","KP"],"ambiguity":"<what could mean two things, for example sign number vs house number, or garbled caption; else empty>","classical_check":"<does a classical text agree, differ, or is it silent? one line>","effect_valence":"good|bad|mixed|neutral","confidence":"high|medium|low","tradition_claim":true}
2. Skip rows (intro, jokes, stories, advertising, audience talk, repetition, music, unreadable caption):
{"id":"G<VID>-<batch>-<nnn>","type":"skip","ts":"1:23:03","reason":"intro|story|joke|ad|audience|repeat|unreadable|opinion-not-astrology|other","gist":"<one line of what was said>"}

## The 12 x 12 grid (Rajat's method, important)
Each (house, sign) pair is exactly one lagna; 12 x 12 = 144 cells. A planet sits in one of them.
- `cells_stated`: the [house, sign] cells his sentence itself covers. House is "1".."12" or "*" for any. Sign is a name (Aries..Pisces) or "*" for any. Examples: Venus exalted in the 7th house -> [["7","Pisces"]]. Mars in Aries, any house -> [["*","Aries"]]. A house-only sentence -> [["10","*"]]. A planet-only sentence -> use planets and cells_stated [["*","*"]].
- Never put a cell in `cells_stated` unless his sentence covers it. Cells you work out yourself go in `cells_derived_method` and `derived_examples` only (give 2 to 4 examples that really differ across houses or signs, not templated).
- His sign numbers: when he says "number 1..12" for a sign, the numbering is Aries=1 ... Pisces=12 (confirmed in this series), but he sometimes says house numbers the same way. If unclear, say so in `ambiguity`.
- He uses 12 planets: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu, Uranus (Indra), Neptune (Varuna), Pluto (Yama). In his scheme the 12 signs each have a lord among these 12 (Aries Mars, Taurus Venus, Gemini Mercury, Cancer Moon, Leo Sun, Virgo Mercury or Rahu, Libra Venus or Neptune, Scorpio Mars or Uranus, Sagittarius Jupiter, Capricorn Saturn, Aquarius Saturn or Pluto, Pisces Jupiter or Ketu). Record what he actually says; do not assume.
- Houses are multi-sign (each house is touched by 2 or 3 signs). If he says this, record it.

## Arithmetic you must get right (past batches got these wrong)
- Signs in order: Aries1 Taurus2 Gemini3 Cancer4 Leo5 Virgo6 Libra7 Scorpio8 Sagittarius9 Capricorn10 Aquarius11 Pisces12. A planet in sign S in house H means lagna = sign number (S - H + 1), wrapping at 12. Example: Cancer(4) in 10th -> 4-10+1=-5 -> 7 = Libra. Check each derived example this way, or leave the lagna out of the sentence.
- Exaltation: Sun Aries, Moon Taurus, Mars Capricorn, Mercury Virgo, Jupiter Cancer, Venus Pisces, Saturn Libra. Debilitation is the opposite sign. Own signs: Sun Leo; Moon Cancer; Mars Aries+Scorpio; Mercury Gemini+Virgo; Jupiter Sagittarius+Pisces; Venus Taurus+Libra; Saturn Capricorn+Aquarius. Do not call a sign exalted/debilitated/own unless it is.
- derived_examples must be genuinely different houses and signs, 2 to 4 per statement, only when the statement depends on house or sign.

## Hard rules
- Understand each sentence and check it against house, sign and planet logic. Do not just copy his words as the meaning.
- If the caption is garbled and you cannot tell what he said, write a skip row with reason "unreadable". Never invent.
- `says` must be specific and different for each row. No template phrases. No row may repeat another row's `says`.
- Remedies, do's and don'ts are `tradition_claim: true`. No death dates, no medical diagnoses, no investment advice (record that he said it, flag it in `says`).
- If he contradicts himself or a classical text, say so in `classical_check`.
- Keep rows in transcript order. Use the nearest earlier [timestamp] for `ts`.

## Verify
Run: python3 /home/claude/jyotish-engine/tune/convert/check_gautam.py OUTFILE INFILE
It must print OK and a coverage line. Fix every error it lists. Do not finish until it prints OK. Then run: python3 /home/claude/jyotish-engine/tune/convert/fix_gautam.py OUTFILE OUTFILE.fixed and replace OUTFILE with the fixed file (cp).
Final reply: one line with the counts (stmt rows, skip rows, low-confidence rows). No other text.
