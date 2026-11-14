#!/bin/sh
# Run every check. Needs PyJHora + pyswisseph (see docs/RUNBOOK.md). Exit non-zero on any failure.
cd "$(dirname "$0")" || exit 1
PY=${PY:-python3}
fail=0
for t in test_kp.py test_report.py test_rules_norm.py test_house_signs.py test_influence.py test_apply_rules.py test_guidance.py test_daily.py verify_divisional.py verify_dasha.py verify_antardasha.py verify_panchang.py verify_ashtakavarga.py verify_transit.py; do
  echo "== $t"; out=$($PY $t 2>&1); rc=$?; echo "$out" | grep -v "added to system" | tail -8; [ $rc -eq 0 ] || { echo "FAILED: $t"; fail=1; }
done
(cd ../core && $PY test_houses.py >/dev/null 2>&1) && echo "== test_houses.py ok" || { echo "== test_houses.py FAILED"; fail=1; }
exit $fail
