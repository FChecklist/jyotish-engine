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
1. Lal Kitab aspect table (Principle 4): no verified table found; owner to name the source or table. Until then the aspect % is a lower bound (P4 = 0).
2. Aspect ladder "+/- 5/10/15 %": read as percent of the aspect angle (5% of 180 = 9 deg). Confirm, or give absolute degrees.
3. Colour-rule aspect weight: assumed 0.5 of a placement hit. Confirm, or say how the aspect % should feed the colour rules.
4. Western orbs (8/6/8/8/8, linear) are my choice - confirm or give his orbs.
