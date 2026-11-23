"""Planted-bug check for tests/test_owner_calc.py (not part of run_all.sh: it runs the whole suite once per bug).
For every bug below: copy core/owner_calc.py to a temp folder, plant ONE bug (exact text replace, the old text must occur exactly once),
run a copy of the test file against it and require a non-zero exit. Exit 0 only when the clean copy passes and every planted bug is caught.
Usage: python3 tests/mutation_owner_calc.py [name-filter]"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = open(os.path.join(ROOT, "core", "owner_calc.py")).read()

# (name, old text, new text)
BUGS = [
    # --- D1 Final = 50/25/25 and the frames (audit angle 1, Medium 2: M1, M2) ---
    ("D1 Final uses D1 only", 'final = {k: sum(w[f] * fh[f].get(k, 0) for f in fr) for k in set().union(*fh.values())}', 'final = {k: fh["D1"].get(k, 0) for k in set().union(*fh.values())}'),
    ("D1 and Bhav Chalit weights swapped", 'FRAME_W = {"D1": 0.5, "KP": 0.25, "BC": 0.25}', 'FRAME_W = {"D1": 0.25, "KP": 0.25, "BC": 0.5}'),
    ("KP weight 0.25 -> 0.3", 'FRAME_W = {"D1": 0.5, "KP": 0.25, "BC": 0.25}', 'FRAME_W = {"D1": 0.5, "KP": 0.3, "BC": 0.25}'),
    ("Bhav Chalit shift 15 -> 14", "return int((((lon - lag_lon + 15) % 360) // 30) + 1)", "return int((((lon - lag_lon + 14) % 360) // 30) + 1)"),
    # --- D9 rules (M3, M6, M8, M13) ---
    ("D9 adds its colours where D1 has a rule", 'fin = recommend(r1, a1 | a9, conflict=bool(vetoed))', 'fin = recommend(r1 + r9, a1 | a9, conflict=bool(vetoed))'),
    ("clash_owner_decision status removed", 'if not fin["primary"]: status = "clash_owner_decision"', "pass"),
    ("D9 aspect-only hit no longer vetoes", "rules = sorted((n, w) for (n, s), w in d9h.items() if s == s9)", "rules = sorted((n, w) for (n, s), w in d9h.items() if s == s9 and w >= 1.0)"),
    ("D9 avoid from the first rule only", "for n, _ in rules: avoid |= set(RULES[n - 1][\"avoid\"])", "for n, _ in rules[:1]: avoid |= set(RULES[n - 1][\"avoid\"])"),
    ("D1 avoid from the first rule only", 'r = RULES[n - 1]; use |= set(r["use"]); avoid |= set(r["avoid"])', 'r = RULES[n - 1]; use |= set(r["use"]); avoid = avoid or set(r["avoid"])'),
    ("D9 house counted from the D1 lagna", "s9 = (d9lag + house - 1) % 12", "s9 = (house - 1) % 12"),
    ("D9 lagna read from the wrong field", 'return rule_hits({p: S[v[3]] for p, v in chart["planets"].items()}), S[chart["lagna"][3]]', 'return rule_hits({p: S[v[3]] for p, v in chart["planets"].items()}), S[chart["lagna"][0]]'),
    ("D9 veto list emptied", "avoid = set()\n    for n, _ in rules:", "avoid = set()\n    for n, _ in []:"),
    # --- ranking, mix, Lal Kitab (M14, M15, Low 3) ---
    ("ranking by rule count, not weight", "cov[c] = cov.get(c, 0) + w", "cov[c] = cov.get(c, 0) + 1"),
    ("avoid list ignored when ranking", "if c not in avoid:\n                cov[c]", "if True:\n                cov[c]"),
    ("Lal Kitab direction swapped", "v4 = lal_kitab_aspect(a, hs.get(a), hs.get(b))", "v4 = lal_kitab_aspect(a, hs.get(b), hs.get(a))"),
    ("conflict mix never offered", "if conflict or len({n for n, _ in rule_weights}) > 1:", "if len({n for n, _ in rule_weights}) > 1:"),
    ("mix on an avoid list still offered", "elif m in avoid: out[\"blend_note\"]", "elif False: out[\"blend_note\"]"),
    # --- one answer per house (Medium 1) ---
    ("houses[] colours from the old zodiac view", '"colour_use": [c for c, _ in fr["ranked"]] if fr else [],', '"colour_use": z["approved"]["use"] if z else [],'),
    ("zodiac view checks D9 by zodiac again", "_, _, d9_avoid = d9_rules_in_house(d9h, d9lag, house)", 'd9_avoid = set().union(set(), *[set(RULES[n - 1]["avoid"]) for (n, ss) in d9h if ss == s])'),
    ("house_final missing from calculate()", ', "house_final": house_final_table(chart, _col=col)}', "}"),
    # --- KP warning handling (audit angle 2, M1) ---
    ("warned KP frame still blended in", 'info["kp_dropped"] = True\n        else:\n            out["KP"]', 'info["kp_dropped"] = True\n        if True:\n            out["KP"]'),
    ("warnings missing from house_final rows", '"warnings": col["warnings"], "kp_dropped": col["kp_dropped"]})\n    return rows', '"warnings": [], "kp_dropped": col["kp_dropped"]})\n    return rows'),
    ("warnings missing from house_report rows", '"remedy": fr, "warnings": col["warnings"]', '"remedy": fr, "warnings": []'),
    ("warnings missing from calculate() top level", 'return {"warnings": col["warnings"], "kp_dropped"', 'return {"warnings": [], "kp_dropped"'),
    ("warnings missing from colour_advice", '"warnings": info.get("warnings", [])', '"warnings": []'),
    ("ayanamsa window widened to 0-90", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 22.0, 26.0, 66.0", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 0.0, 90.0, 66.0"),
    ("ayanamsa lower edge 22 -> 21", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 22.0, 26.0, 66.0", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 21.0, 26.0, 66.0"),
    ("ayanamsa lower edge 22 -> 23", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 22.0, 26.0, 66.0", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 23.0, 26.0, 66.0"),
    ("ayanamsa upper edge 26 -> 27", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 22.0, 26.0, 66.0", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 22.0, 27.0, 66.0"),
    ("ayanamsa upper edge 26 -> 25", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 22.0, 26.0, 66.0", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 22.0, 25.0, 66.0"),
    ("ayanamsa edge 22 becomes a warning", "if not AYAN_MIN <= ayan <= AYAN_MAX:", "if not AYAN_MIN < ayan <= AYAN_MAX:"),
    ("ayanamsa edge 26 becomes a warning", "if not AYAN_MIN <= ayan <= AYAN_MAX:", "if not AYAN_MIN <= ayan < AYAN_MAX:"),
    ("latitude limit 66 -> 67", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 22.0, 26.0, 66.0", "AYAN_MIN, AYAN_MAX, KP_MAX_LAT = 22.0, 26.0, 67.0"),
    ("latitude edge 66 becomes a warning", "if abs(lat) > KP_MAX_LAT:", "if abs(lat) >= KP_MAX_LAT:"),
    ("southern latitude never warns", "if abs(lat) > KP_MAX_LAT:", "if lat > KP_MAX_LAT:"),
    # --- input validation (M1) ---
    ("tz not range-checked", '-14 <= b["tz"] <= 14', "True"),
    ("lat not range-checked", '-90 < b["lat"] < 90', "True"),
    ("lat 90 accepted", '-90 < b["lat"] < 90', '-90 <= b["lat"] <= 90'),
    ("lon not range-checked", '-180 <= b["lon"] <= 180', "True"),
    ("date not checked as a calendar day", "try: datetime.date(y, m, d)", "try: pass"),
    ("date year range dropped", "1583 <= y <= 2200", "True"),
    ("time range dropped", "0 <= hh <= 23 and 0 <= mm <= 59", "True"),
    ("unknown planet name accepted", "if name not in ASPECTS:", "if False:"),
    ("string numbers accepted", "return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)", "return True"),
    # --- Julian day (L1) ---
    ("Julian day +0.5", "+ d + b - 1524.5 + ut / 24.0", "+ d + b - 1524.0 + ut / 24.0"),
    ("time-zone sign flipped", "ut = hh + mm / 60.0 - tz", "ut = hh + mm / 60.0 + tz"),
    ("Gregorian correction dropped", "b = 2 - a + a // 4", "b = 0"),
    # --- CSV (L2) ---
    ("CSV: house 3 body part blanked", '"body_parts": HOUSE_BODY[h], "zodiac": NAME[sg], "planet": p,', '"body_parts": HOUSE_BODY[h] if h != 3 else "", "zodiac": NAME[sg], "planet": p,'),
    ("CSV: avoid list cut to its first colour", '"colour_avoid": " ".join(a["avoid"])', '"colour_avoid": " ".join(a["avoid"][:1])'),
    ("CSV: use list cut to its first colour", '"colour_use": " ".join(a["use"]),', '"colour_use": " ".join(a["use"][:1]),'),
    ("CSV: dignity of a sign dropped", '"dignity": dignity(p, sg),', '"dignity": dignity(p, sg) if sg != "Ar" else 0.0,'),
    # --- other outputs (L4) ---
    ("verdict_band 0.25 -> 0.5", "def house_report(chart, verdict_band=0.25):", "def house_report(chart, verdict_band=0.5):"),
    ("HOUSE_BODY house 5 right pocket -> left pocket", "5: \"right abdomen, right pocket,", "5: \"right abdomen, left pocket,"),
    ("Lal Kitab Mars liver -> kidney", '"Mars": "liver"', '"Mars": "kidney"'),
    # --- rules and aspects still protected ---
    ("rule 1 weight: placement 1.0 -> 0.9", "if s in trig: out[(r[\"no\"], s)] = 1.0", "if s in trig: out[(r[\"no\"], s)] = 0.9"),
    ("Jupiter 9th aspect dropped", '"Jupiter": [5, 7, 9]', '"Jupiter": [5, 7]'),
    # --- exhaustive check (L3) ---
    ("exhaustive check: colours below the top two not checked", '{c for c, _ in rec["ranked"]} & avoid_all or ', ""),
]


def run(code, tests_src, data_src):
    with tempfile.TemporaryDirectory() as d:
        for sub in ("core", "tests", "data"): os.makedirs(os.path.join(d, sub))
        open(os.path.join(d, "core", "owner_calc.py"), "w").write(code)
        shutil.copy(tests_src, os.path.join(d, "tests", "test_owner_calc.py"))
        shutil.copy(data_src, os.path.join(d, "data", "owner_house_zodiac_planet.csv"))
        p = subprocess.run([sys.executable, os.path.join(d, "tests", "test_owner_calc.py")], capture_output=True, text=True, timeout=300)
        return p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]


def main():
    flt = sys.argv[1] if len(sys.argv) > 1 else ""
    t = os.path.join(HERE, "test_owner_calc.py"); dcsv = os.path.join(ROOT, "data", "owner_house_zodiac_planet.csv")
    rc, last = run(SRC, t, dcsv)
    print("clean copy:", "PASS" if rc == 0 else "FAIL", last)
    if rc != 0: sys.exit(1)
    caught, survived = 0, []
    for name, old, new in BUGS:
        if flt and flt not in name: continue
        if SRC.count(old) != 1: print("SETUP ERROR (old text found %d times): %s" % (SRC.count(old), name)); survived.append(name); continue
        rc, last = run(SRC.replace(old, new), t, dcsv)
        if rc != 0: caught += 1; print("caught   ", name)
        else: survived.append(name); print("SURVIVED ", name)
    print("planted bugs caught: %d of %d; survived: %s" % (caught, caught + len(survived), survived or "none"))
    sys.exit(1 if survived else 0)


if __name__ == "__main__":
    main()
