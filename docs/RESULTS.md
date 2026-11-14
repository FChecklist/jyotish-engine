# Measured results (metric: percentile of event date in person's own timeline; 50 = chance)
- 2026-11-13/14 Fine-tune CV, 111 people / 890 events: out-of-fold 50.9, 95% CI 48.8-52.7; equal weights 51.3. No skill.
- 44 technique-area tests: none survives multiple-testing correction. One lead (dasha lords own area house, foreign events) q 0.11 -> 0.54 after removing approximate-date events.
- Verification 001 vs PyJHora (7 charts): see ref/VERIFY_REPORT_001.md.
Conclusion: no demonstrated predictive skill yet. Next: bigger exact-date dataset, locked 30% test set, prospective log.
- 2026-11-14 Verification 002 (divisional charts): our own Swiss Ephemeris + BPHS formulas vs PyJHora signs. D1,D3,D4,D7,D9,D10,D12,D16,D20,D24,D27,D40,D45,D60: 40/40 signs agree each (5 charts x asc + Sun..Saturn). Limits: only 5 charts, nodes not tested, D2/D5/D6/D8/D11/D30 not tested (variant-dependent), degrees within sign differ between PyJHora functions and are not checked. Test: tests/verify_divisional.py (run with the ref venv python).
