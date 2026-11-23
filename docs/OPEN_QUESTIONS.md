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
10. Aspect ladder wording: owner wrote "+/-5%, 10%, 15%". Coded as percent of the aspect angle (7th: 9/18/27 deg). Did he mean absolute degrees (5/10/15)? Both are in core/aspects.py (mode=).
11. Lal Kitab aspect table for principle 4 of the aspect %: supply a source. Until then P4 = None and every aspect % is a lower bound.
12. Should P1 give a score to conjunction (same degree)? The owner's P1 text lists only the 7th and special aspects, so it gives 0 today. Rahu/Ketu: owner list says 1st and 7th, older atoms say 5/7/9.
