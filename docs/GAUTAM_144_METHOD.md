# Gautam lectures: sentence-by-sentence method with the 12 x 12 grid (pilot, 2026-11-17)

Source: Brajesh Gautam, Jyotish Vidya, Ep. 1 (YouTube auto-captions, Hindi, saved transcript JyotishVidya_01_h8udc_JNiAg.txt). Captions are garbled in places; a statement that cannot be read with confidence is not turned into a rule.

## Key fact (Rajat's idea, 2026-11-17)
Every (house, sign) pair is exactly one lagna. 12 houses x 12 signs = 144 cells = 12 lagnas x 12 houses. A planet sits in one of 144 cells.
So for each statement we record: which cells it STATES, which cells we DERIVE by method, and which stay UNKNOWN. We never copy a meaning to all cells silently.

## Per sentence (steps)
1. Read the Hindi sentence. Say what it means in plain English. Flag ambiguity (for example "number 1" = sign 1 or house 1).
2. Scope tag: universal / planet / house / sign / planet+house / planet+sign / planet+house+sign / timing / remedy / story-or-opinion.
3. Cells: list the (house, sign) cells the sentence states. Stated = what the teacher said. Derived = what follows from classical significations (house topic x sign nature x planet nature), labelled "derived, not said by teacher".
4. Charts to test: D1 whole-sign, D9, bhava chalit, KP, and other divisional charts, using core/influence.py (houses are multi-sign).
5. Conflicts with earlier rules or with classical texts are written down, not hidden.
6. Output: rule rows in the existing schema plus `cells`, `cells_basis` (stated / derived), `charts`, `ambiguity`, `confidence`.

## Pilot 1: Venus exalted in the 7th (transcript 1:11:02)
- Said: an exalted Venus "does full indulgence"; exalted Venus in the 7th house (wife's house) gives divorce; he calls it the best position giving a bad result.
- Understanding: exalted Venus = Venus in Pisces. In the 7th house means lagna Virgo. So this is ONE cell: house 7 x Pisces.
- Stated cells: (7, Pisces). Derived: Venus in Pisces in the other 11 houses = strong, indulgent Venus, effect in that house's area (not said by teacher).
- Charts: D1 and D9 (Venus in Pisces in D9 is the same cell test). Ambiguity: none about the house, but "divorce" is stated as certain; treat as tradition claim.
- Conflict: classical texts usually call exalted Venus in the 7th a strong marriage yoga. Flag this.

## Pilot 2: Mars in sign 1 or on its cusp (transcript 1:23:03)
- Said: if Mars is "number 1" or cusping with number 1, it strongly empowers the navel centre (Hanuman consciousness); work through you gets done and cannot be stopped; you must have one heart-dear friend (not a stay-at-home one, since you cannot tell him secrets). Before it: any planet in its own sign or looking at its own sign is a king.
- Understanding: "number 1" is his sign numbering = Aries (Mars's own sign). "Cusping" = within a few degrees of the Aries border (late Pisces or early Taurus). "Looking at its own sign" = Mars aspecting Aries or Scorpio.
- Stated cells: Mars in Aries, all 12 houses (12 cells). Also Mars at the Aries border.
- Derived cells: Mars aspecting Aries or Scorpio (Mars in Capricorn, Libra, Virgo for Aries; Leo, Taurus for Scorpio), all houses. These come from the "own sign looked at is a king" sentence, which is general.
- Mars in Aries by house (derived: where the work gets done, and lagna):

| House | Lagna | Mars rules houses | Where the "work gets done" |
| --- | --- | --- | --- |
| 1 | Aries | 1, 8 | Self, body, own initiative. Ruchaka yoga (own sign in a kendra) |
| 2 | Pisces | 2, 9 | Money and speech; luck. Watch harsh speech |
| 3 | Aquarius | 3, 10 | Courage, siblings, effort and career. Mars is strong in the 3rd |
| 4 | Capricorn | 4, 11 | Home, property, vehicles; gains. Ruchaka yoga |
| 5 | Sagittarius | 5, 12 | Mind, creativity, children; expenses abroad |
| 6 | Scorpio | 6, 1 | Rivals, service, debts won through effort |
| 7 | Libra | 7, 2 | Partners and public dealing. Ruchaka yoga. Heat in partnership |
| 8 | Virgo | 8, 3 | Hidden, research, sudden matters; stamina |
| 9 | Leo | 9, 4 | Fortune, father, dharma; strong luck planet |
| 10 | Cancer | 10, 5 | Career. Ruchaka yoga, lord of 5 and 10 |
| 11 | Gemini | 11, 6 | Gains, network, friends; the "dear friend" |
| 12 | Taurus | 12, 7 | Expense, foreign, isolation; spending of energy |

- Charts: D1, D9, bhava chalit, KP. The "cusp" reading needs the multi-sign influence shares (core/influence.py).
- Ambiguity to confirm in audio: "number 1" could be the house, not the sign. His own numbering elsewhere in this video says sign 1 = Mars, so sign is the better reading.

## Scale
36 videos, about 2 hours each. Per video: about 150 timestamp chunks. Run as agent waves with the same two-pass check as the atoms pipeline. Never script the meaning text.
