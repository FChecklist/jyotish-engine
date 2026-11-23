# Aspect strength (owner rule 2026-11-23) — spec for core/aspects.py

Source: owner message OWNER-2026-11-23-B (D1 `jyotish-rules`, table `owner_method_text`). Plain maths; no AI.
Input: sidereal longitudes from the calculator (we do not recompute charts). No birth data in this repo.

**Final aspect % = (P1 + P2 + P3 + P4) / 4.** Each principle is scored 0..100.

| P | Rule | Code |
|---|---|---|
| P1 | Owner degree ladder. Aspect angle = (n-1) x 30 forward from the aspecting planet. 7th (180) for all; Mars 4/7/8 = 90/180/210; Jupiter 5/7/9 = 120/180/240; Saturn 3/7/10 = 60/180/270; Rahu, Ketu, Uranus, Neptune, Pluto 7th only. Deviation within 5% of the angle = 100, 10% = 75, 15% = 50, beyond = 0. | `p1_owner_ladder` |
| P2 | Western. Conjunction 0 (orb 8), sextile 60 (6), square 90 (8), trine 120 (8), opposition 180 (8). Linear: 100 exact, 0 at the orb edge. | `p2_western` |
| P3 | Vedic graha drishti, sign based. Same sign = 100. Owner list = 100. Parashara partials for the 7 classical planets only, where not already full: 3rd/10th = 25, 5th/9th = 50, 4th/8th = 75. | `p3_graha_drishti` |
| P4 | Lal Kitab. **PENDING**: no verified table. Returns `None`. | `p4_lal_kitab` |

While P4 is `None`: result has `final_is_lower_bound = True` (P4 counted as 0) and `final_range_if_p4_known = (lower, lower + 25)`.
A real P4 can be plugged in with `aspect(..., p4_fn=...)` or by implementing `p4_lal_kitab`. Do not invent a table.

Aspects are directional for P1, P3, P4 (A looks forward at B); P2 is symmetric. `strongest_per_pair` keeps the stronger direction.
Rahu-Ketu pair is skipped (always exactly 180).

## Readings that need the owner (flagged, not decided)
1. "+/- 5%": coded as percent OF THE ASPECT ANGLE (7th: 9 / 18 / 27 deg; Mars 4th: 4.5 / 9 / 13.5 deg). If he meant absolute degrees (5 / 10 / 15), call with `mode='absolute_degrees'`. The two give different numbers.
2. Conjunction is not in the owner's P1 text, so P1 scores it 0. P3 and P2 do score it.
3. Nodes: owner list is 1st and 7th. The older atoms in `core/rules_norm.py` use 5/7/9 for Rahu/Ketu. Not reconciled.
4. Beyond 15% the owner gave no value; 0 is assumed. Between the steps (e.g. 5.1%) the step below applies (no interpolation), since he wrote "nearly".

## Tests
`tests/test_aspects.py`: hand-worked values for every rule, boundaries, wrap-around, direction, errors, pluggable P4, and 16 deliberate breaks that must each be detected (then the code is restored and must pass).
Not tested: real charts (cross-checked once privately against the BOSS scratch reference, 200 pairs, 0 mismatches); no link to real events has been measured.
