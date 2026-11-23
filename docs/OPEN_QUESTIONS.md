# Open questions for Rajat
1. Confirm defaults: true node, geometric positions, KP both ayanamsas.
2. Confirm: Narayana = Jaimini Narayana dasha? Sayan = tropical chart?
3. Primary divisional-chart variants; allowed birth-time grades per chart.
4. Trash outdated Drive v5 uploads?
5. Reddit route: allow old.reddit.com, API with own credentials, or paste posts.
6. Licence: PyJHora and Swiss Ephemeris are AGPL; decide open-source vs commercial licence before any paid product.
7. Lal Kitab Varshphal table: supply it.
8. Ashtakavarga Moon/Venus table variant: PyJHora default vs plain BPHS table (differs by a few bindus). Needs a source check in the books; until then both are exposed (core/ashtakavarga.py variant=).
9. Multi-sign houses (core/house_signs.py): Gautam says each house is touched by 2-3 signs. We list signs per house under six systems with votes and average degrees; a sign under 2 degrees is ignored (MIN_DEG, a heuristic). Open: (a) how to weight systems, (b) how the D9 layer should combine with D1 and KP (currently only the navamsha sign of each KP cusp and its house from the D9 lagna), (c) the exact Gautam statement and method to be read from the transcripts.

## 2026-11-23 Owner colour + aspect rules - waiting on Rajat
1. Lal Kitab aspect table (Principle 4): now taken from B.M. Goswami, Lal Kitab (English, 1952 edition), pp.118-124 (archive.org/details/jyotishlalkitabb.m.gosvami): 1->7 100, 4->10 100, 3->9/11 50, 5->9 50, 2->6 25, 6->12 25, 8->2 25 (book also says 100 in one passage). Mercury, Rahu, Ketu special rules not modelled. Owner to confirm or give another table.
2. Aspect ladder "+/- 5/10/15 %": read as percent of the aspect angle (5% of 180 = 9 deg). Confirm, or give absolute degrees.
3. Colour-rule aspect weight: assumed 0.5 of a placement hit. Confirm, or say how the aspect % should feed the colour rules.
4. Western orbs (8/6/8/8/8, linear) are my choice - confirm or give his orbs.
5. Lal Kitab body parts HOUSE-wise (Principle 2): the book gives body parts per PLANET only (liver Mars, heart Moon, torso Ketu, brain/tongue Mercury, sight Saturn, head Rahu, neck Jupiter) plus house 1 = body, 8 = eyes, 11 = legs. No house-wise list found; owner Principle 1 list is used for houses.
6. Plus side of a house: classical dignity (exalted +1, own +0.5, debilitated -1) is my assumption; owner has not given a table.
7. Bhav Chalit and KP houses are computed (the site has no such view); my ascendant calibration differs from the Lahiri ayanamsa by ~0.2 deg for the two reference charts, so planets within ~0.2 deg of a house edge may flip.
8. Independent audit of PR #4 (23 Nov 2026): rules, aspects, weights and Placidus cusps verified; privacy fix (name and birth time removed from docs), exhaustive check recomputes avoid lists independently, KP ayanamsa/latitude warnings (now: a warned KP frame is dropped and the warning is in every output), input range checks, P4 lower-bound flag, known-answer Placidus from an independent solver, rule table against hard-coded owner text. Still unverifiable: Lal Kitab table beyond the Goswami pages read; meaning of '+/-5%' (percent of the angle assumed). The D9 compare rule is now implemented house by house everywhere (item 9 asks the owner to confirm it).
9. D9 compare rule: the code checks D9 HOUSE BY HOUSE (D9 house h from the D9 lagna against D1 house h; D9 only vetoes colours, placement and aspect-only hits both veto). This came from the work brief, not from the verbatim owner text. Owner: confirm in your own words, and say whether other divisional charts (D2-D60) veto too (not implemented).
10. D1 has no rule in a house but D9 has: the code gives the D9 advice labelled `d9_only`. The owner text only says D9 validates D1 Final. Confirm, or say no advice should be given there.
11. D9 conflict mix: when D9 vetoes a colour the code tries primary + secondary of the colours left (MIX table: blue+yellow=green, red+yellow=orange, red+blue=purple, black+white=grey, red+green=brown, red+white=pink, blue+white=light blue, yellow+green=lime); if the pair is not in the table, or the mix is on an avoid list, it says none and why. Confirm the table and the rule, or give your own mixes.
