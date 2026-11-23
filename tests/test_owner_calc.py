"""Tests for core/owner_calc.py (owner rules 2026-11-23). Synthetic charts only - no real birth data."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import owner_calc as O

BASE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]


def chart(places=None, d9=None, lagna=("Ar", 15, 0, "Ar")):
    """Every planet parked in a harmless place unless overridden: sign, 15 deg (mid-sign so Bhav Chalit == D1 when lagna is at 15 deg)."""
    pl = {p: ["Vi", 15, 0, "Vi"] for p in BASE}          # Virgo is a trigger only for Venus (rule 6); we move Venus below
    pl["Venus"] = ["Pi", 15, 0, "Pi"]                      # Pisces: not a Venus trigger
    pl["Mercury"] = ["Aq", 15, 0, "Aq"]                    # Aquarius: not a Mercury trigger
    pl["Jupiter"] = ["Ge", 15, 0, "Ge"]
    for p, v in (places or {}).items(): pl[p] = list(v)
    for p, s in (d9 or {}).items(): pl[p][3] = s
    return {"lagna": list(lagna), "planets": pl}


# ---- 1. every owner rule fires in each of its zodiacs at weight 1.0, and its use colours are never in its own avoid list ----
for r in O.RULES:
    assert not (set(r["use"]) & set(r["avoid"])), r
    for sg in r["signs"]:
        c = chart({r["planet"]: [sg, 15, 0, sg]})
        res = O.colour_advice(c)
        z = [z for z in res["zodiacs"] if z["zodiac"] == O.NAME[sg]]
        assert z, (r["no"], sg)
        hit = [x for x in z[0]["rules"] if x["rule"] == r["no"]]
        assert hit and hit[0]["weight"] == 1.0, (r["no"], sg, z[0]["rules"])
        for col in z[0]["approved"]["use"]: assert col not in z[0]["approved"]["avoid"]

# ---- 2. an aspect-only hit weighs ASPECT_W: Sun in Scorpio aspects Taurus (7th), Taurus is a Sun trigger ----
res = O.colour_advice(chart({"Sun": ["Sc", 15, 0, "Sc"]}))
ta = [z for z in res["zodiacs"] if z["zodiac"] == "Taurus"]
assert ta and ta[0]["rules"][0]["rule"] == 1 and ta[0]["rules"][0]["weight"] == O.ASPECT_W == 0.5

# ---- 3. KP missing -> weights renormalised and reported; KP present -> 0.5/0.25/0.25 ----
assert res["frames_missing"] == ["KP"] and abs(res["frame_weights"]["D1"] - 2 / 3) < 1e-9
tc = O.placidus_cusps(O._julian_day("2000-01-01", "12:00", 5.5), 28.6, 77.2)
lag_lon = (tc[1] - 23.85) % 360
lagna = (O.SIGNS[int(lag_lon // 30)], int(lag_lon % 30), int(round((lag_lon % 30 % 1) * 60)), "Ar")
c = chart({"Sun": ["Sc", 15, 0, "Sc"]}, lagna=lagna); c["birth"] = {"date": "2000-01-01", "time": "12:00", "tz": 5.5, "lat": 28.6, "lon": 77.2}
res = O.colour_advice(c)
assert res["frames_missing"] == [] and res["frame_weights"] == {"D1": 0.5, "KP": 0.25, "BC": 0.25}
assert abs(res["ayanamsa_calibrated"] - 23.85) < 0.02, res["ayanamsa_calibrated"]

# ---- 4. two negatives in one zodiac: blends are proposed, and a blend that lands on an avoided colour is rejected ----
res = O.colour_advice(chart({"Mercury": ["Cn", 15, 0, "Cn"], "Mars": ["Cn", 15, 0, "Cn"]}))
cn = [z for z in res["zodiacs"] if z["zodiac"] == "Cancer"][0]
assert {x["rule"] for x in cn["rules"]} >= {3, 4}
assert "blue+yellow=green" in cn["d1_final"]["blends_rejected"]        # rule 4 avoids green
assert "red" in cn["d1_final"]["avoid"] and "red" not in cn["d1_final"]["use"]

# ---- 5. D9 conflict: Saturn in Aries (use red/yellow/grey) but Neptune sits in Aries in D9 (avoids grey) -> grey removed ----
res = O.colour_advice(chart({"Saturn": ["Ar", 15, 0, "Ar"]}, d9={"Neptune": "Ar"}))
ar = [z for z in res["zodiacs"] if z["zodiac"] == "Aries"][0]
assert "grey" in ar["d1_final"]["use"] and ar["d9_conflict"] == ["grey"] and "grey" not in ar["approved"]["use"]
assert set(ar["approved"]["use"]) == {"red", "yellow"}

# ---- 6. P1 owner degree ladder: percent OF the aspect angle (5/10/15 -> 100/75/50) ----
sun = lambda off: O.p1_owner_degree("Sun", 0.0, 180.0 + off)
assert sun(0) == 100 and sun(9) == 100 and sun(9.1) == 75 and sun(18) == 75 and sun(18.1) == 50 and sun(27) == 50 and sun(27.1) == 0
mars = lambda ang: O.p1_owner_degree("Mars", 0.0, ang)
assert mars(90) == 100 and mars(94.5) == 100 and mars(94.6) == 75 and mars(210) == 100 and mars(120) == 0
assert O.p1_owner_degree("Jupiter", 0.0, 240) == 100 and O.p1_owner_degree("Saturn", 0.0, 270) == 100 and O.p1_owner_degree("Saturn", 0.0, 60) == 100
assert O.p1_owner_degree("Sun", 0.0, 90) == 0                   # Sun has only the 7th

# ---- 7. P2 western ----
assert O.p2_western(0, 180) == (100.0, "opposition") and O.p2_western(0, 176)[0] == 50.0
assert O.p2_western(10, 130)[1] == "trine" and O.p2_western(0, 61)[1] == "sextile" and O.p2_western(0, 30)[0] == 0

# ---- 8. P3 Vedic: full on owner list and conjunction, Parashara partials only for the 7 classical planets ----
assert O.p3_vedic("Jupiter", 0, 4) == 100 and O.p3_vedic("Sun", 0, 4) == 50 and O.p3_vedic("Sun", 0, 6) == 100
assert O.p3_vedic("Sun", 0, 0) == 100 and O.p3_vedic("Pluto", 0, 4) == 0 and O.p3_vedic("Mars", 0, 3) == 100 and O.p3_vedic("Mars", 0, 2) == 25

# ---- 9. final aspect = (P1+P2+P3+P4)/4; P4 = Lal Kitab house table (Goswami pp.118-124) ----
c = chart({"Sun": ["Ar", 10, 0, "Ar"], "Moon": ["Li", 10, 0, "Li"]})                 # lagna Aries: Sun house 1, Moon house 7
t = [a for a in O.aspect_table(c) if {a["from"], a["to"]} == {"Sun", "Moon"}][0]
assert (t["p1"], t["p2"], t["p3"], t["p4"]) == (100, 100, 100, 100) and not t["p4_pending"] and t["final"] == 100.0
assert O.lal_kitab_aspect("Sun", 1, 7) == 100 and O.lal_kitab_aspect("Sun", 4, 10) == 100 and O.lal_kitab_aspect("Sun", 3, 11) == 50
assert O.lal_kitab_aspect("Sun", 3, 9) == 50 and O.lal_kitab_aspect("Sun", 5, 9) == 50 and O.lal_kitab_aspect("Sun", 2, 6) == 25
assert O.lal_kitab_aspect("Sun", 6, 12) == 25 and O.lal_kitab_aspect("Sun", 8, 2) == 25 and O.lal_kitab_aspect("Sun", 7, 1) == 0
assert O.lal_kitab_aspect("Sun", None, 7) is None
c = chart({"Sun": ["Ar", 10, 0, "Ar"], "Moon": ["Cn", 10, 0, "Cn"]})                 # Sun house 1, Moon house 4: no LK aspect 1->4
t = [a for a in O.aspect_table(c) if {a["from"], a["to"]} == {"Sun", "Moon"}]
assert not t or t[0]["p4"] == 0
assert not any({a["from"], a["to"]} == {"Rahu", "Ketu"} for a in O.aspect_table(c))        # the node axis is not reported as an aspect

# ---- 10. rule table integrity: 15 rules, owner text confirmations ----
assert len(O.RULES) == 15 and O.RULES[0]["signs"] == ["Ta", "Li"] and O.RULES[4]["avoid"] == ["yellow", "golden"]
# ---- 11. house report: 12 houses, owner body parts, negative load -> strained house ----
assert len(O.HOUSE_BODY) == 12 and O.HOUSE_BODY[8].endswith("inner anus") and O.HOUSE_BODY[12].endswith("sexual activity")
rep = O.house_report(chart({"Saturn": ["Cn", 15, 0, "Cn"]}))           # lagna Aries: Cancer is house 4; Saturn rule 8 hits it fully
h4 = rep[3]
assert [r["house"] for r in rep] == list(range(1, 13)) and h4["zodiac"] == "Cancer" and h4["owner_negative_load"] >= 1.0
assert h4["verdict"] == "strained" and "right chest" in h4["body_parts"] and h4["lal_kitab_planet_parts"] == {"Saturn": "sight and assessment"}
assert "red" in h4["colour_avoid"] and "red" not in h4["colour_use"]
good = O.house_report(chart({"Jupiter": ["Cn", 15, 0, "Cn"]}))[3]        # Jupiter exalted in Cancer, no owner rule fires there
assert good["dignity_plus"] == 1.0 and good["verdict"] == "supportive"
assert O.dignity("Sun", "Ar") == 1.0 and O.dignity("Sun", "Li") == -1.0 and O.dignity("Sun", "Le") == 0.5 and O.dignity("Rahu", "Ta") == 0.0

# ---- 12. exhaustive check: 12 zodiacs x every subset of 12 planets ----
st = O.enumerate_all()
assert st["full_cases"] == 49152 and st["violations"] == 0 and st["unresolvable"] == 0
assert st["pure_ok"] == st["cases_with_a_rule"] == 33760 and 0 < st["one_colour_good_for_every_planet"] < st["cases_with_a_rule"]
# ---- 13. decisive remedy: the colour covering the most rule weight wins; blend only if its mix is not avoided ----
res = O.colour_advice(chart({"Mars": ["Cn", 15, 0, "Cn"], "Saturn": ["Cn", 15, 0, "Cn"]}))      # rules 3 (blue yellow) + 8 (yellow grey), avoid red
cn = [z for z in res["zodiacs"] if z["zodiac"] == "Cancer"][0]["remedy"]
assert cn["primary"] == "yellow" and cn["ranked"][0][0] == "yellow" and "red" not in [c for c, _ in cn["ranked"]]
assert O.recommend([(1, 1.0)], set())["primary"] == "blue" and O.recommend([(1, 1.0)], {"blue"})["primary"] is None
r = O.recommend([(3, 1.0), (8, 0.0)], set())                         # two rules meet: blue/yellow lead, blue + yellow = green allowed
assert r["blend"] in ("blue+yellow=green", "yellow+blue=green")
assert O.recommend([(3, 1.0), (8, 0.0)], {"green"})["blend"] is None   # green avoided: blend rejected
assert O.recommend([(3, 1.0)], set())["blend"] is None                 # one rule only: no blend needed
assert O.recommend([(12, 1.0)], set())["primary"] == "red"             # tie -> owner's listed order (red yellow green)

# ---- 14. all 12 houses x 12 zodiacs x 12 planets ----
tr = O.all_triples()
assert len(tr) == 1728 and len({(r["house"], r["zodiac"], r["planet"]) for r in tr}) == 1728
sun_ta = [r for r in tr if r["house"] == 5 and r["zodiac"] == "Taurus" and r["planet"] == "Sun"][0]
assert sun_ta["owner_rules"] == "1" and sun_ta["colour_use"] == "blue" and "orange" in sun_ta["colour_avoid"] and sun_ta["dignity"] == 0.0
assert [r for r in tr if r["house"] == 1 and r["zodiac"] == "Aries" and r["planet"] == "Sun"][0]["dignity"] == 1.0
assert sum(1 for r in tr if r["owner_rules"]) == 12 * len({(x["planet"], sg) for x in O.RULES for sg in x["signs"]})
print("test_owner_calc ok")
