# Owner colour rules, 23 Nov 2026 (engine v0.3.0)

Version: 0.3.0 (see CHANGELOG.md, version.json). Source: owner, 23 Nov 2026, id `OWNER-2026-11-23-A`. Owner text verbatim: `docs/OWNER_RULES_2026-11-23.md`.
This is a tradition claim, not a measured fact. No accuracy is claimed. These rules SUPERSEDE the 21 Nov table (`docs/PLANET_SIGN_NEGATIVES.md`, `core/planet_negatives.py`) wherever they differ.

## Files
- Rules: `data/owner_colour_rules.csv` (15 rows: rule_no, planet, trigger_signs, use_colours, avoid_colours, source, note). Same 15 rules are in Cloudflare D1 `owner_colour_rules`; compared row by row, no difference.
- Code: `core/colour_rules.py` (plain if/then, no AI). Placidus cusps come from `core/houses.py` (Swiss Ephemeris), not from a second implementation.
- Tests: `tests/test_colour_rules.py` (in `tests/run_all.sh`).
- Nothing is loaded to D1 by this change, nothing is deployed, the daily guidance is not changed.

## What the engine does, step by step
1. Input: lagna longitude, sidereal longitude of each planet, Lahiri by default (ayanamsa is a parameter). Planets not supplied are not evaluated.
2. Three views, each a map planet -> sign:
   - D1: the sign of the longitude.
   - Bhav Chalit (BC): equal houses. House h spans lagna + 30(h-1) minus 15 up to plus 15, so cusp 1 = lagna longitude and the cusp is the middle of the house.
   - KP: sidereal Placidus houses (`kp_cusps(jd, lat, lon, ayanamsa)`). Refuses latitudes inside the polar circles.
   - In KP and BC the planet's effective sign = lagna sign + (house - 1).
3. A rule fires on a zodiac in one view when its planet SITS in a trigger sign (weight 1.0) or ASPECTS a trigger sign (weight 0.5, assumption). Aspects count forward by house number, own house = 1:
   - Sun, Moon, Mercury, Venus: 1, 7. Mars: 1, 4, 7, 8. Jupiter: 1, 5, 7, 9. Saturn: 1, 3, 7, 10. Rahu, Ketu, Uranus, Neptune, Pluto: 1, 7.
4. D1 Final weight of (zodiac, rule) = 0.5 x D1 + 0.25 x KP + 0.25 x BC. Maximum 1.0 (placement in all three). The owner's "in case of doubt" split is the same 50/25/25, so there is one set of weights.
5. Colour advice per zodiac, from every rule with weight above 0 on that zodiac:
   - pure colours = union of use colours minus union of avoid colours;
   - one negative with a pure colour left: pure colours only, no blend;
   - two or more negatives, or no pure colour left: blends are proposed too. Blend table: blue+yellow=green, red+yellow=orange, red+blue=purple, black+white=grey, red+green=brown. Components come from the use colours; a blend whose RESULT is an avoid colour is rejected. With two or more negatives the blends are listed before the single colours.
   - If a zodiac needs a blend and none is valid, `blend_unavailable` is true (it is not hidden).
6. D9 check: the same rules are run on the D9 signs (9 x longitude). For each D1 Final zodiac, a suggested colour is ANTI if a D9 rule firing on the same zodiac avoids it. Anti colours are removed. If anything is anti, a mix is proposed: a blend of colours from the D1 Final use list and the D9 use list (at least one from D1 Final) whose result is an avoid colour in neither D1 Final nor D9.
   - status `approved`: nothing anti. `adjusted`: something anti, other colours or a mix remain. `unresolved`: nothing left.
7. Output (`analyse(...)`): views, houses per view, planets that moved house versus D1, per-zodiac hits (with by-view weights and weight_total), advice, D9 validation. Plain data, JSON-safe.

## Readings and assumptions (owner to confirm)
- (a) Aspect hit weight 0.5. The owner said only that the effect "reduces if its not directly in that zodiac". One constant, `ASPECT_HIT_WEIGHT`, in `core/colour_rules.py`.
- (b) Rule 5: owner wrote "Or do not use Yellow or golden". Read as "And": yellow and golden are both avoided.
- (c) Rule 1: Sun triggers are Taurus and Libra. The 21 Nov table said Taurus and Virgo. The new text wins.
- (d) KP and Bhav Chalit are not captured from the source site, so they are computed here (Placidus via Swiss Ephemeris, equal-house Bhav Chalit).
- (e) A blend may need an avoided colour as an ingredient (only the result is checked, as briefed). Such blends carry `uses_avoided_component: true`. Owner: is an avoided colour allowed as an ingredient?
- (f) Any weight above 0 counts when building the colour lists, so a rule that fires only through KP (weight 0.25) adds its use and avoid colours like a full hit. The weights are reported, not used as a cut-off. Owner: set a minimum weight?
- (g) D9 mix: components from D1 Final use + D9 use colours, at least one from D1 Final. This rule is ours.
- (h) "Zodiac" in KP and BC = whole sign from the house number, as briefed. The repo rule that every house touches 2+ signs (core/influence.py shares) is not applied here; the three-view weighting stands in for it. Needs a decision.
- Spelling: `While` = White, `aquarious` = Aquarius, `sagitarius` = Sagittarius, `scropio` = Scorpio. Rule 6 trigger order is Virgo, Gemini, Cancer.
- Rahu and Ketu aspects are 1 and 7 only, as listed; `core/dignity.py` has 5/7/9 for the nodes and is not changed.
- The old table's separate Rahu/Ketu/Uranus/Neptune/Pluto rows are gone; rule numbers changed (old 8 Rahu is now 9, and so on). Old rules had "any one colour or the combination"; the new rules use "use these, avoid those, blend to reach a colour".

## What was measured (not accuracy, only behaviour on the real table)
Random charts (20,000, random sign maps, not real people): in 162,135 zodiac hits, "no pure colour left" never happened (0), D9 `unresolved` never happened, a D9 mix was proposed in 1.7% (2,727), and among zodiacs with two or more negatives (61,225) 19% (11,884) had no valid blend. So with the real table the nothing-pure and unresolved paths are only exercised by synthetic rules in the tests.

## Not done
- Not wired into `core/guide.py` or the daily 3 DO + 3 DONT. Not loaded to D1. Nothing deployed. Ledger not re-measured.
- Not run against a real person's chart in this repo (no birth data in git). The Placidus and house maths are tested on synthetic charts.
- D9 is whole-sign only (no multi-sign shares).
