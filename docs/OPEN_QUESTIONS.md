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
