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
# ================= audit additions (independent auditor findings, 23 Nov 2026) =================
import math

# ---- 15. RULES against a hard-coded copy of the owner's sentences (full names, written differently from the code) ----
OWNER_TEXT = {1: ("Sun", "Taurus Libra", "blue", "orange"), 2: ("Moon", "Scorpio Aries", "red yellow", "white black"),
              3: ("Mars", "Cancer", "blue yellow", "red"), 4: ("Mercury", "Pisces Cancer", "yellow blue grey", "green brown red"),
              5: ("Jupiter", "Capricorn Aquarius", "black red", "yellow golden"), 6: ("Venus", "Virgo Gemini Cancer", "blue green", "white silver"),
              7: ("Saturn", "Aries Scorpio", "red yellow grey", "white black"), 8: ("Saturn", "Cancer", "yellow grey", "red"),
              9: ("Rahu", "Sagittarius", "yellow green black", "brown blue"), 10: ("Ketu", "Gemini", "green purple", "grey silver"),
              11: ("Uranus", "Cancer Taurus Libra", "yellow", "red orange"), 12: ("Neptune", "Aries Scorpio Gemini", "red yellow green", "black white grey silver"),
              13: ("Neptune", "Cancer", "yellow", "red"), 14: ("Pluto", "Aries Scorpio Leo", "red yellow", "white black"), 15: ("Pluto", "Cancer", "yellow", "red")}
assert len(O.RULES) == 15
for r in O.RULES:
    pl, sg, use, avoid = OWNER_TEXT[r["no"]]
    assert r["planet"] == pl and sorted(O.NAME[x] for x in r["signs"]) == sorted(sg.split()), r["no"]
    assert r["use"] == use.split() and sorted(r["avoid"]) == sorted(avoid.split()), r["no"]
assert O.ASPECTS == {"Sun": [7], "Mercury": [7], "Venus": [7], "Moon": [7], "Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10],
                     "Rahu": [7], "Ketu": [7], "Uranus": [7], "Neptune": [7], "Pluto": [7]}

# ---- 16. aspects count FORWARD from the planet's sign, never backward ----
assert any(k[1] == O.S["Cn"] for k in O.rule_hits({"Mars": O.S["Ar"]}))       # Mars in Aries, 4th forward = Cancer -> rule 3 aspect hit
assert not any(k[1] == O.S["Cn"] for k in O.rule_hits({"Mars": O.S["Li"]}))   # Mars in Libra: Cancer is 4th BACKWARD -> no hit
# ---- 17. Vedic partials for the classical seven, none for the others ----
for n, v in {3: 25, 10: 25, 5: 50, 9: 50, 4: 75, 8: 75}.items():
    assert O.p3_vedic("Moon", 0, n - 1) == v, n                 # Moon has no special aspect list: partial applies
    assert O.p3_vedic("Rahu", 0, n - 1) == 0, n
assert O.p3_vedic("Mars", 0, 3) == 100 and O.p3_vedic("Sun", 0, 6) == 100 and O.p3_vedic("Sun", 0, 0) == 100
# ---- 18. western orbs: sextile 6, others 8, linear fall-off ----
assert abs(O.p2_western(0, 64)[0] - 100 * (1 - 4 / 6)) < 1e-9 and O.p2_western(0, 67)[0] == 0
assert abs(O.p2_western(0, 96)[0] - 100 * (1 - 6 / 8)) < 1e-9 and O.p2_western(0, 99)[0] == 0
assert O.p2_western(0, 180)[1] == "opposition" and O.p2_western(0, 120)[1] == "trine"
# ---- 19. Bhav Chalit edges (+/-15 deg around the lagna degree) and wrap at 360 ----
assert O.bhav_chalit_house(100, 114.9) == 1 and O.bhav_chalit_house(100, 115.1) == 2
assert O.bhav_chalit_house(100, 85.1) == 1 and O.bhav_chalit_house(100, 84.9) == 12
assert O.bhav_chalit_house(358, 5) == 1 and O.bhav_chalit_house(5, 358) == 1 and O.bhav_chalit_house(0, 359) == 1
# ---- 20. dignity tables (hard-coded classical values) ----
assert O.EXALT == {"Sun": "Ar", "Moon": "Ta", "Mars": "Cp", "Mercury": "Vi", "Jupiter": "Cn", "Venus": "Pi", "Saturn": "Li"}
assert O.DEBIL == {"Sun": "Li", "Moon": "Sc", "Mars": "Cn", "Mercury": "Pi", "Jupiter": "Cp", "Venus": "Vi", "Saturn": "Ar"}
assert O.OWN["Moon"] == ["Cn"] and sorted(O.OWN["Mars"]) == ["Ar", "Sc"] and sorted(O.OWN["Venus"]) == ["Li", "Ta"]
# ---- 21. owner's house/body-part list: every house carries its key words ----
KEY = {1: ["head", "forehead"], 2: ["right eye", "upper neck", "lips"], 3: ["right ear", "upper right arm"], 4: ["right chest", "wrist"],
       5: ["right abdomen", "upper right thigh"], 6: ["low right thigh", "ankle"], 7: ["waist"], 8: ["low left thigh", "anus"],
       9: ["left abdomen", "upper left thigh"], 10: ["left chest", "wrist"], 11: ["left ear", "upper left arm"], 12: ["left eye", "sexual"]}
for h, ks in KEY.items():
    for k in ks: assert k in O.HOUSE_BODY[h], (h, k)


# ---- 22. Placidus known-answer test against an independent solver (hour-angle / semi-arc bisection) ----
def independent_cusps(jd, lat, lon):
    t = (jd - 2451545.0) / 36525.0
    e = math.radians(23.4392911 - 0.0130042 * t)
    ramc = ((280.46061837 + 360.98564736629 * (jd - 2451545.0)) + lon) % 360
    ph = math.radians(lat)

    def ha_dsa(lam):
        l = math.radians(lam)
        ra = math.degrees(math.atan2(math.sin(l) * math.cos(e), math.cos(l))) % 360
        dec = math.asin(math.sin(e) * math.sin(l))
        dsa = 90 + math.degrees(math.asin(max(-1, min(1, math.tan(ph) * math.tan(dec)))))
        return ((ramc - ra + 180) % 360) - 180, dsa

    def solve(target):             # target(dsa) -> wanted hour angle; find lam with ha == target
        def f(lam):
            ha, dsa = ha_dsa(lam)
            return (((ha - target(dsa)) + 180) % 360) - 180
        prev, a = f(0.0), 0.0
        for i in range(1, 721):
            b = i * 0.5
            cur = f(b)
            if prev * cur <= 0 and abs(prev - cur) < 90:
                lo, hi = a, b
                for _ in range(80):
                    mid = (lo + hi) / 2
                    if f(lo) * f(mid) <= 0: hi = mid
                    else: lo = mid
                return lo % 360
            prev, a = cur, b
        raise AssertionError("no root")
    return {1: solve(lambda d: -d), 10: solve(lambda d: 0.0), 11: solve(lambda d: -d / 3), 12: solve(lambda d: -2 * d / 3),
            3: solve(lambda d: -180 + (180 - d) / 3), 2: solve(lambda d: -180 + 2 * (180 - d) / 3)}


for date, tm, tz, lat, lon in [("2000-01-01", "12:00", 5.5, 28.6, 77.2), ("1990-06-15", "03:30", 5.5, 25.2, 75.8),
                               ("1985-11-02", "21:10", 10.0, -33.9, 151.2), ("2010-03-21", "00:05", 0.0, 51.5, -0.1)]:
    jd = O._julian_day(date, tm, tz)
    mine = O.placidus_cusps(jd, lat, lon)
    ind = independent_cusps(jd, lat, lon)
    for h, v in ind.items():
        assert abs(((mine[h] - v + 180) % 360) - 180) < 0.01, (date, h, mine[h], v)

# ---- 23. KP mapping and house_in boundary ----
cu = O.placidus_cusps(O._julian_day("2000-01-01", "12:00", 5.5), 28.6, 77.2)
assert O.house_in(cu, cu[5]) == 5 and O.house_in(cu, (cu[5] - 0.001) % 360) == 4
lag_lon = (cu[1] - 23.85) % 360
ayan = (cu[1] - lag_lon) % 360
sc = {h: (cu[h] - ayan) % 360 for h in cu}
mid3 = (sc[3] + ((sc[4] - sc[3]) % 360) / 2) % 360
lag_sign = int(lag_lon // 30)
kc = {"lagna": [O.SIGNS[lag_sign], int(lag_lon % 30), 0, "Ar"], "birth": {"date": "2000-01-01", "time": "12:00", "tz": 5.5, "lat": 28.6, "lon": 77.2},
      "planets": {"Sun": [O.SIGNS[int(mid3 // 30)], int(mid3 % 30), int(round((mid3 % 1) * 60)) % 60, "Ar"]}}
fr, ls, info = O.frames(kc)
assert fr["KP"]["Sun"] == (ls + 2) % 12 and "warnings" not in info

# ---- 24. input checks and warnings ----
for bad in [{"planets": {}}, {"lagna": ["Ar", 30, 0, "Ar"], "planets": {}}, {"lagna": ["Xx", 1, 0, "Ar"], "planets": {}},
            {"lagna": ["Ar", 1, 60, "Ar"], "planets": {}},
            {"lagna": ["Ar", 1, 0, "Ar"], "planets": {}, "birth": {"date": "2000-01-01", "time": "12:00", "lat": 28, "lon": 77}}]:
    try:
        O.colour_advice(bad)
    except ValueError:
        continue
    raise SystemExit("accepted bad input: %r" % (bad,))
w = O.colour_advice({"lagna": ["Sc", 5, 0, "Ar"], "planets": {"Sun": ["Ar", 1, 0, "Ar"]},
                     "birth": {"date": "2000-01-01", "time": "12:00", "tz": 5.5, "lat": 28.6, "lon": 77.2}})
assert w.get("warnings") and "ayanamsa" in w["warnings"][0]
w = O.colour_advice({"lagna": ["Ar", 5, 0, "Ar"], "planets": {"Sun": ["Ar", 1, 0, "Ar"]},
                     "birth": {"date": "2000-01-01", "time": "12:00", "tz": 5.5, "lat": 70.0, "lon": 20.0}})
assert any("latitude" in x for x in w["warnings"])
# ---- 25. P4 unknown (no lagna) is flagged as a lower bound ----
no_lag = {"planets": {"Sun": ["Ar", 1, 0, "Ar"], "Moon": ["Li", 2, 0, "Ar"]}}
assert all(r["final_is_lower_bound"] for r in O.aspect_table(no_lag))
assert not any(r["final_is_lower_bound"] for r in O.aspect_table(chart({"Sun": ["Ar", 1, 0, "Ar"], "Moon": ["Li", 2, 0, "Ar"]})))
# ---- 26. the exhaustive check recomputes avoid lists from RULES itself: a deliberately broken rule must be caught ----
saved = O.RULES[0]["avoid"]
O.RULES[0]["avoid"] = ["blue"]            # rule 1 now avoids its own use colour
try:
    assert O.enumerate_all()["violations"] > 0
finally:
    O.RULES[0]["avoid"] = saved
assert O.enumerate_all()["violations"] == 0


# ---- 27. house-by-house D1 + D9 table (owner confirmed: D9 house counted from the D9 lagna, D9 only vetoes) ----
# Sun in Libra (D1 house 7 from Aries lagna) triggers rule 1: use blue, avoid orange. Moon placed in D9 Aries at D9 house 7 (D9 lagna Libra) triggers rule 2: avoid white/black.
hf = O.house_final_table(chart({"Sun": ["Li", 15, 0, "Ta"]}, lagna=("Ar", 15, 0, "Ar")))
assert [r["house"] for r in hf] == list(range(1, 13))
r7 = hf[6]
assert r7["d1_zodiac"] == "Libra" and r7["d1_avoid"] == ["orange"] and r7["final"]["primary"] == "blue" and r7["status"] == "d1"
# D9 veto: Sun's D9 sign Taurus is house 2 from D9 lagna Taurus? make D9 lagna Libra so D9 house 7 = Aries, put Moon there in D9
hv = O.house_final_table(chart({"Sun": ["Li", 15, 0, "Ta"], "Moon": ["Ge", 15, 0, "Ar"]}, lagna=("Ar", 15, 0, "Li")))
assert hv[6]["d9_zodiac"] == "Aries" and set(hv[6]["d9_avoid"]) == {"black", "white"}      # D9 house 7 is judged against D1 house 7
assert hv[6]["final"]["primary"] == "blue" and hv[6]["status"] == "d1"                       # blue is not anti in D9: approved unchanged
# a D1 colour that D9 forbids must be dropped: Neptune in Aries (D1, rule 12: use red/yellow/green) vs Mars in D9 Cancer = D9 house 1 (rule 3: avoid red)
hd = O.house_final_table(chart({"Neptune": ["Ar", 15, 0, "Ar"], "Mars": ["Vi", 15, 0, "Cn"]}, lagna=("Ar", 15, 0, "Cn")))
assert hd[0]["d1_recommended"]["primary"] == "red" and "red" in hd[0]["d9_avoid"]
assert hd[0]["final"]["primary"] == "yellow" and "red" in hd[0]["d9_vetoed"] and hd[0]["status"] == "d1_with_d9_veto"
# D9-only house: no D1 rule in house 1 but a D9 rule there
ho = O.house_final_table(chart({"Moon": ["Vi", 15, 0, "Sc"]}, lagna=("Ar", 15, 0, "Sc")))
assert ho[0]["d9_zodiac"] == "Scorpio" and ho[0]["d1_recommended"] is None and ho[0]["status"] == "d9_only" and ho[0]["final"]["primary"] in ("red", "yellow")

# ================= fixes for the two AUDIT: FAIL comments of 23 Nov 2026 (18:47Z) =================
import csv, copy, io
DELHI = {"date": "2000-01-01", "time": "12:00", "tz": 5.5, "lat": 28.6, "lon": 77.2}


def lagna_for(birth, ayan_target):
    """Lagna [sign, deg, min, 'Ar'] whose calibrated ayanamsa is ayan_target (to one arc-minute) for this birth."""
    tc = O.placidus_cusps(O._julian_day(birth["date"], birth["time"], birth["tz"]), birth["lat"], birth["lon"])
    ll = (tc[1] - ayan_target) % 360
    return [O.SIGNS[int(ll // 30)], int(ll % 30), int(round((ll % 30 % 1) * 60)) % 60, "Ar"]


# ---- 28. Julian day known values (L1): date, UT/zone sign, Gregorian correction, Jan/Feb month shift ----
assert O._julian_day("2000-01-01", "12:00", 0) == 2451545.0
assert O._julian_day("1900-03-01", "00:00", 0) == 2415079.5
assert O._julian_day("2000-02-29", "18:00", 0) == 2451604.25
assert O._julian_day("2000-01-01", "17:30", 5.5) == 2451545.0        # 17:30 at UTC+5.5 is 12:00 UT (zone sign)
assert O._julian_day("1999-12-31", "19:00", -5.0) == 2451544.5       # 19:00 at UTC-5 is 24:00 UT = 2000-01-01 00:00 UT
assert O._julian_day("2000-03-01", "12:00", 0) - O._julian_day("2000-02-29", "12:00", 0) == 1.0     # leap day exists

# ---- 29. validate_chart ranges (M1): every bad input raises ValueError in EVERY public entry point ----
GOOD = {"lagna": ["Ar", 5, 0, "Ar"], "planets": {"Sun": ["Ar", 1, 0, "Ar"]}, "birth": dict(DELHI)}


def with_birth(**kw):
    c = copy.deepcopy(GOOD); c["birth"].update(kw); return c


bad_charts = [with_birth(tz=99), with_birth(tz=-15), with_birth(tz="5.5"), with_birth(tz=True), with_birth(date="2000-13-45"), with_birth(date="2000-02-30"),
              with_birth(date="20000101"), with_birth(date="1200-01-01"), with_birth(date="2300-01-01"), with_birth(time="25:99"), with_birth(time="24:00"),
              with_birth(time="12:60"), with_birth(time="1:5"), with_birth(lat=200), with_birth(lat=-200), with_birth(lat=90), with_birth(lat=-90),
              with_birth(lat=float("nan")), with_birth(lon=500), with_birth(lon=-181), with_birth(lon=float("inf")), with_birth(lat="28.6"),
              {"lagna": ["Ar", 5, 0, "Ar"], "planets": {"Chiron": ["Ar", 1, 0, "Ar"]}},
              {"lagna": ["Ar", 5, 0, "Ar"], "planets": {"sun": ["Ar", 1, 0, "Ar"]}},
              {"lagna": ["Ar", 5, 0, "Ar"], "planets": {"Sun": ["Ar", "1", 0, "Ar"]}},
              {"lagna": ["Ar", 5, 0, "Ar"], "planets": ["Sun"]},
              {"lagna": ["Ar", 5, 0, "Ar"], "planets": {"Sun": ["Ar", 1, 0]}},
              {"lagna": ["Ar", 5, 0, "Ar"], "planets": {"Sun": [["Ar"], 1, 0, "Ar"]}},
              {"lagna": ["Ar", 5, 0, "Ar"], "planets": {"Sun": ["Ar", 1, 0, "Ar"]}, "birth": "2000-01-01"}]
for fn in (O.colour_advice, O.house_report, O.house_final_table, O.calculate, O.aspect_table):
    for bc in bad_charts:
        if fn is O.aspect_table and bc.get("planets") == {"Sun": ["Ar", 1, 0]}: continue      # aspect_table needs no D9 sign
        try:
            fn(bc)
        except ValueError:
            continue
        raise SystemExit("%s accepted bad input: %r" % (fn.__name__, bc))
for ok_birth in (dict(DELHI, tz=-14), dict(DELHI, tz=14), dict(DELHI, lat=89.9), dict(DELHI, lat=-89.9), dict(DELHI, lon=-180), dict(DELHI, lon=180),
                 dict(DELHI, date="1583-01-01"), dict(DELHI, date="2200-12-31"), dict(DELHI, time="00:00"), dict(DELHI, time="23:59")):
    c = copy.deepcopy(GOOD); c["birth"] = ok_birth
    O.validate_chart(c)                                       # edge values are accepted
try:
    O.aspect_table({"planets": {"Chiron": ["Ar", 1, 0, "Ar"]}}); raise SystemExit("aspect_table accepted an unknown planet")
except ValueError as e:
    assert "Chiron" in str(e)

# ---- 30. KP window edges 22-26 and latitude 66 (M1) ----
assert not O.kp_warnings(22.0, 28.6) and not O.kp_warnings(26.0, 28.6) and not O.kp_warnings(24.0, 28.6)
assert O.kp_warnings(21.999, 28.6) and O.kp_warnings(26.001, 28.6)
assert "ayanamsa" in O.kp_warnings(21.0, 0)[0] and "ayanamsa" in O.kp_warnings(27.0, 0)[0]
assert not O.kp_warnings(24.0, 66.0) and not O.kp_warnings(24.0, -66.0)
assert O.kp_warnings(24.0, 66.001) and O.kp_warnings(24.0, -66.001) and "latitude" in O.kp_warnings(24.0, 80)[0]
for target, kept in [(22.5, True), (25.5, True), (21.5, False), (26.5, False), (20.0, False), (28.0, False)]:
    c = chart({"Sun": ["Sc", 15, 0, "Sc"]}, lagna=lagna_for(DELHI, target)); c["birth"] = dict(DELHI)
    fr, _, info = O.frames(c)
    assert ("KP" in fr) == kept, (target, info)
    assert bool(info.get("warnings")) == (not kept) and info.get("kp_dropped", False) == (not kept), (target, info)
    res = O.colour_advice(c)
    assert (res["frames_missing"] == []) == kept and bool(res["warnings"]) == (not kept) and res["kp_dropped"] == (not kept)
    if not kept: assert res["frame_weights"] == {"D1": 2 / 3, "BC": 1 / 3} or all(abs(res["frame_weights"][k] - v) < 1e-9 for k, v in {"D1": 2 / 3, "BC": 1 / 3}.items())

# ---- 31. a warned KP frame is DROPPED and the warning is in EVERY output (M1) ----
tc70 = O.placidus_cusps(O._julian_day("2000-01-01", "12:00", 5.5), 70.0, 20.0)
lag70 = (tc70[1] - 23.85) % 360                                   # lagna calibrated for lat 70: only the latitude warning fires
HIGH = {"lagna": [O.SIGNS[int(lag70 // 30)], int(lag70 % 30), int(round((lag70 % 30 % 1) * 60)), "Ar"],
        "planets": {"Sun": ["Sg", 5, 0, "Ar"]}, "birth": dict(DELHI, lat=70.0, lon=20.0)}       # Sun 245 deg: KP (junk at lat 70) would put it in Scorpio
NOBIRTH = {k: v for k, v in HIGH.items() if k != "birth"}
assert O.frames(HIGH)[2]["warnings"] == O.colour_advice(HIGH)["warnings"] and "latitude" in O.colour_advice(HIGH)["warnings"][0]
raw_kp = O.placidus_cusps(O._julian_day("2000-01-01", "12:00", 5.5), 70.0, 20.0)


def strip(x):
    """drop warning bookkeeping and the calibrated ayanamsa so a warned chart can be compared with the same chart without birth data"""
    if isinstance(x, dict): return {k: strip(v) for k, v in x.items() if k not in ("warnings", "kp_dropped", "ayanamsa_calibrated", "frames_missing")}
    if isinstance(x, list): return [strip(v) for v in x]
    return x


assert strip(O.colour_advice(HIGH)) == strip(O.colour_advice(NOBIRTH))
assert strip(O.house_final_table(HIGH)) == strip(O.house_final_table(NOBIRTH))
assert strip(O.house_report(HIGH)) == strip(O.house_report(NOBIRTH))
assert strip(O.calculate(HIGH)["house_final"]) == strip(O.calculate(NOBIRTH)["house_final"])
out = O.calculate(HIGH)
assert out["warnings"] and out["kp_dropped"] and out["colour"]["warnings"] == out["warnings"] and out["frames_missing"] == ["KP"]
assert all(r["warnings"] == out["warnings"] and r["kp_dropped"] for r in out["house_final"])
assert all(r["warnings"] == out["warnings"] and r["kp_dropped"] for r in out["houses"])
assert out["frame_weights"]["D1"] == 2 / 3 or abs(out["frame_weights"]["D1"] - 2 / 3) < 1e-9
clean = O.calculate(dict(NOBIRTH))
assert clean["warnings"] == [] and not clean["kp_dropped"] and all(r["warnings"] == [] for r in clean["house_final"] + clean["houses"])
# an unwarned chart keeps KP (weights 0.5 / 0.25 / 0.25) and carries no warning
ok = O.calculate(dict(chart({"Sun": ["Sc", 15, 0, "Sc"]}, lagna=lagna_for(DELHI, 23.85)), birth=dict(DELHI)))
assert ok["warnings"] == [] and ok["frames_missing"] == [] and ok["frame_weights"] == {"D1": 0.5, "KP": 0.25, "BC": 0.25}

# ---- 32. D1 Final = 50% D1 + 25% KP + 25% Bhav Chalit, numbers by hand (Medium 2: M1, M2) ----
# no birth data: KP missing, weights D1 2/3 + BC 1/3. Lagna Aries 5 deg, Sun Aries 25 deg.
#   D1: Sun in Aries; its 7th aspect lands on Libra (a Sun trigger)            -> (rule 1, Libra) 0.5 in D1
#   Bhav Chalit: 25 deg is 20 deg after the lagna degree -> house 2 = Taurus   -> (rule 1, Taurus) 1.0 in BC
#   final: Libra 0.5 * 2/3 = 0.333, Taurus 1.0 * 1/3 = 0.333
hc = {"lagna": ["Ar", 5, 0, "Ar"], "planets": {"Sun": ["Ar", 25, 0, "Ar"]}}               # only the Sun, so only rule 1 can fire
fz = {z["zodiac"]: z for z in O.colour_advice(hc)["zodiacs"]}
assert set(fz) == {"Taurus", "Libra"}, set(fz)
assert abs(fz["Taurus"]["total_weight"] - 1 / 3) < 1e-3 and abs(fz["Libra"]["total_weight"] - 1 / 3) < 1e-3, (fz["Taurus"]["total_weight"], fz["Libra"]["total_weight"])
assert (fz["Taurus"]["rules"][0]["d1"], fz["Taurus"]["rules"][0]["bc"]) == (0, 1.0) and (fz["Libra"]["rules"][0]["d1"], fz["Libra"]["rules"][0]["bc"]) == (0.5, 0)
# with KP present the same Sun at Scorpio 4 deg (D1 and BC Scorpio, KP Libra) for a lagna calibrated at 23.85: Taurus 0.5*.5+.25*.5 = 0.375, Libra 0.25
kp_lag = ["Pi", 13, 11, "Ar"]
kpc = {"lagna": kp_lag, "planets": {"Sun": ["Sc", 4, 0, "Sc"]}, "birth": dict(DELHI)}
assert O.frames(kpc)[0]["KP"]["Sun"] == O.S["Li"]       # KP puts the Sun in Libra
kc = O.colour_advice(kpc)
assert kc["warnings"] == [] and kc["frame_weights"] == {"D1": 0.5, "KP": 0.25, "BC": 0.25}
kz = {z["zodiac"]: z["total_weight"] for z in kc["zodiacs"]}
assert kz == {"Taurus": 0.375, "Libra": 0.25}, kz

# ---- 33. D9 never adds colours where D1 has a rule (Medium 2: M3) ----
# D1: Sun in Libra = house 7 (rule 1: blue). D9 lagna Libra, so D9 house 7 = Aries; Saturn in D9 Aries (rule 7: red yellow grey) is a D9 rule there.
ha = O.house_final_table(chart({"Sun": ["Li", 15, 0, "Ta"], "Saturn": ["Vi", 15, 0, "Ar"]}, lagna=("Ar", 15, 0, "Li")))[6]
assert ha["d9_zodiac"] == "Aries" and {c for c, _ in ha["d9_recommended"]["ranked"]} == {"red", "yellow", "grey"}
assert [c for c, _ in ha["final"]["ranked"]] == ["blue"] and ha["final"]["primary"] == "blue" and ha["status"] == "d1" and ha["d9_vetoed"] == []
# D1 has no rule in the house, D9 has: labelled d9_only
assert O.house_final_table(chart({"Saturn": ["Vi", 15, 0, "Ar"]}, lagna=("Ar", 15, 0, "Ar")))[0]["status"] == "d9_only"

# ---- 34. clash_owner_decision (Medium 2: M6) and one answer per house (Medium 1) ----
# Sun Libra (house 7, only colour blue); Rahu in D9 Sagittarius = D9 house 7 when the D9 lagna is Gemini; rule 9 avoids blue.
CLASH = chart({"Sun": ["Li", 15, 0, "Ta"], "Rahu": ["Vi", 15, 0, "Sg"]}, lagna=("Ar", 15, 0, "Ge"))
cl = O.calculate(CLASH)
assert cl["house_final"][6]["status"] == "clash_owner_decision" and cl["house_final"][6]["final"]["primary"] is None and cl["house_final"][6]["d9_vetoed"] == ["blue"]
assert cl["houses"][6]["colour_use"] == [] and cl["houses"][6]["colour_status"] == "clash_owner_decision" and cl["houses"][6]["colour_blends"] == []
z7 = [z for z in cl["colour"]["zodiacs"] if z["zodiac"] == "Libra"][0]
assert z7["approved"]["use"] == [] and "owner decision" in z7["note"] and z7["d9_conflict"] == ["blue"]
# the ugly case of the old by-zodiac check: Neptune Aries (house 1) with Mars in D9 Cancer = D9 house 1 (rule 3 avoids red)
NEP = chart({"Neptune": ["Ar", 15, 0, "Ar"], "Mars": ["Vi", 15, 0, "Cn"]}, lagna=("Ar", 15, 0, "Cn"))


def one_answer(c):
    out = O.calculate(c)
    for h, (row, fin) in enumerate(zip(out["houses"], out["house_final"]), 1):
        assert row["house"] == fin["house"] == h
        want = [x for x, _ in fin["final"]["ranked"]] if fin["final"] else []
        assert row["colour_use"] == want, (h, row["colour_use"], want)
        assert row["remedy"] == fin["final"] and row["colour_status"] == fin["status"]
        assert row["colour_blends"] == ([fin["final"]["blend"]] if fin["final"] and fin["final"]["blend"] else [])
        assert set(row["colour_use"]).isdisjoint(row["colour_avoid"]) or fin["status"] == "no_rule"
        if fin["status"] != "no_rule": assert set(row["colour_avoid"]) == set(fin["d1_avoid"]) | set(fin["d9_avoid"])
    for z in out["colour"]["zodiacs"]:                           # the per-zodiac view uses the same method: same allowed colours as the house row
        fin = out["house_final"][z["house_d1"] - 1]
        assert z["zodiac"] == fin["d1_zodiac"] and sorted(z["approved"]["use"]) == sorted(x for x, _ in fin["final"]["ranked"]), (z["zodiac"], z["approved"], fin["final"])
        assert z["d9_avoid"] == fin["d9_avoid"] and z["d9_conflict"] == fin["d9_vetoed"]
    return out


nep = one_answer(NEP)
assert "red" not in nep["houses"][0]["colour_use"] and nep["houses"][0]["colour_use"] == ["yellow", "green"] and nep["colour"]["zodiacs"][0]["approved"]["use"] == ["green", "yellow"]
one_answer(CLASH)
for c in (chart({"Saturn": ["Cn", 15, 0, "Cn"], "Mercury": ["Cn", 15, 0, "Cn"]}, d9={"Mars": "Cn"}, lagna=("Ar", 15, 0, "Cn")),
          chart({"Sun": ["Li", 15, 0, "Ta"], "Mars": ["Sc", 15, 0, "Cn"]}), chart({"Moon": ["Sc", 15, 0, "Sc"], "Pluto": ["Le", 15, 0, "Ar"]}, lagna=("Sc", 15, 0, "Ar")),
          chart({}), HIGH, GOOD):
    one_answer(c)

# ---- 35. D9 mix to resolve the conflict (Low 3): where the MIX table allows; else a clear 'none' with the reason ----
assert nep["house_final"][0]["final"]["blend"] == "yellow+green=lime" and nep["house_final"][0]["final"]["blend_note"] is None and nep["house_final"][0]["status"] == "d1_with_d9_veto"
assert nep["houses"][0]["colour_blends"] == ["yellow+green=lime"]
# Saturn Aries (rule 7: red yellow grey) vs Jupiter in D9 Capricorn = D9 house 1 (rule 5 avoids yellow): red + grey is not in the MIX table
NOMIX = O.house_final_table(chart({"Saturn": ["Ar", 15, 0, "Ar"], "Jupiter": ["Ge", 15, 0, "Cp"]}, lagna=("Ar", 15, 0, "Cp")))[0]
assert NOMIX["d9_vetoed"] == ["yellow"] and NOMIX["final"]["primary"] == "red" and NOMIX["final"]["secondary"] == "grey"
assert NOMIX["final"]["blend"] is None and "no mix in the MIX table for red+grey" in NOMIX["final"]["blend_note"]
r = O.recommend([(4, 1.0)], {"yellow", "grey"}, conflict=True)                               # only blue left
assert r["blend"] is None and "only one colour left" in r["blend_note"]
r = O.recommend([(3, 1.0)], {"green"}, conflict=True)                                        # blue + yellow = green, but green is avoided
assert r["blend"] is None and "avoid list" in r["blend_note"]
r = O.recommend([(3, 1.0)], {"blue", "yellow"}, conflict=True)
assert r["primary"] is None and r["blend"] is None and "no mix" in r["blend_note"]
r = O.recommend([(3, 1.0)], {"red"}, conflict=True)
assert r["blend"] == "blue+yellow=green"                                                     # one rule, conflict -> a mix is offered
assert O.recommend([(3, 1.0)], {"red"})["blend"] is None and O.recommend([(3, 1.0)], {"red"})["blend_note"] is None   # one rule, no conflict -> none needed

# ---- 36. D9 aspect-only hit vetoes (Medium 2: M8) ----
# D1: Jupiter Capricorn = house 1 (rule 5: black red; avoid yellow golden). D9 lagna Aries; Moon in D9 Libra only ASPECTS D9 Aries (7th) = Moon trigger (rule 2 avoids white, black)
av = O.house_final_table(chart({"Jupiter": ["Cp", 15, 0, "Ge"], "Moon": ["Vi", 15, 0, "Li"]}, lagna=("Cp", 15, 0, "Ar")))[0]
assert av["d9_zodiac"] == "Aries" and "black" in av["d9_avoid"] and av["d9_vetoed"] == ["black"]
assert [c for c, _ in av["final"]["ranked"]] == ["red"] and av["status"] == "d1_with_d9_veto"
assert O.d9_house_hits(chart({"Moon": ["Vi", 15, 0, "Li"]}, lagna=("Cp", 15, 0, "Ar")))[0][(2, O.S["Ar"])] == O.ASPECT_W

# ---- 37. avoid list is the union of ALL rules in the house, D1 and D9 (Medium 2: M13) ----
# D1 house 4 Cancer: Mars (rule 3, avoid red) + Mercury (rule 4, avoid green brown red). D9 house 4 Cancer (D9 lagna Aries... D9 Cancer = house 1 from D9 lagna Cancer).
mm = chart({"Mars": ["Cn", 15, 0, "Cn"], "Mercury": ["Cn", 15, 0, "Cn"]}, lagna=("Ar", 15, 0, "Cn"))
h4 = O.house_final_table(mm)[3]
assert h4["d1_avoid"] == ["brown", "green", "red"], h4["d1_avoid"]
h1 = O.house_final_table(mm)[0]
assert h1["d9_zodiac"] == "Cancer" and h1["d9_avoid"] == ["brown", "green", "red"] and h1["status"] == "d9_only"      # both D9 rules count, not the first only
assert O.colour_advice(mm)["zodiacs"][0]["d1_final"]["avoid"] == ["brown", "green", "red"]
# a D1 colour on the avoid list of the SECOND rule is not recommended
assert "green" not in [c for c, _ in h4["final"]["ranked"]] and "brown" not in [c for c, _ in h4["final"]["ranked"]]

# ---- 38. ranking is by rule WEIGHT, not rule count (Medium 2: M14) ----
# rule 10 (green purple) weight 1.0 vs rules 4 and 8 (both list yellow and grey) weight 0.25 each: yellow/grey count 2 but weigh 0.5
rk = O.recommend([(10, 1.0), (4, 0.25), (8, 0.25)], set())
assert rk["primary"] == "green" and rk["secondary"] == "purple" and dict(rk["ranked"])["yellow"] == 0.5 and dict(rk["ranked"])["green"] == 1.0
assert [c for c, _ in rk["ranked"]][:2] == ["green", "purple"] and [c for c, _ in rk["ranked"]][-1] == "blue"

# ---- 39. Lal Kitab direction: Jupiter house 3, Sun house 11 = 87.5% (Medium 2: M15) ----
lk = chart({"Jupiter": ["Ge", 15, 0, "Ge"], "Sun": ["Aq", 15, 0, "Aq"]}, lagna=("Ar", 15, 0, "Ar"))
t = [a for a in O.aspect_table(lk) if {a["from"], a["to"]} == {"Jupiter", "Sun"}][0]
assert (t["from"], t["to"]) == ("Jupiter", "Sun") and (t["p1"], t["p2"], t["p3"], t["p4"]) == (100, 100, 100, 50) and t["final"] == 87.5
assert O.lal_kitab_aspect("Jupiter", 3, 11) == 50 and O.lal_kitab_aspect("Sun", 11, 3) == 0

# ---- 40. L2: the shipped CSV equals all_triples() cell by cell ----
with open(os.path.join(os.path.dirname(__file__), "..", "data", "owner_house_zodiac_planet.csv"), newline="") as fh:
    raw = fh.read()
assert "\r" not in raw and raw.endswith("\n")
rows = list(csv.reader(io.StringIO(raw)))
trip = O.all_triples()
assert rows[0] == ["house", "body_parts", "zodiac", "planet", "owner_rules", "dignity", "colour_use", "colour_avoid"] == list(trip[0])
assert len(rows) == 1 + len(trip) == 1729
for got, want in zip(rows[1:], trip):
    assert got == [str(want[k]) for k in rows[0]], (got, want)
buf = io.StringIO(newline="")
wr = csv.writer(buf, lineterminator="\n"); wr.writerow(rows[0]); [wr.writerow([r[k] for k in rows[0]]) for r in trip]
assert buf.getvalue() == raw                                      # byte for byte what the code would write

# ---- 41. L4: verdict_band, house_final in calculate(), HOUSE_BODY exact, Lal Kitab planet parts ----
# Sun in Leo (own sign, +0.5) in house 5 of an Aries lagna, no owner rule there: net +0.5
sl = chart({"Sun": ["Le", 15, 0, "Le"]})
assert O.house_report(sl)[4]["net"] == 0.5 and O.house_report(sl)[4]["verdict"] == "supportive"
assert O.house_report(sl, verdict_band=0.49)[4]["verdict"] == "supportive" and O.house_report(sl, verdict_band=0.5)[4]["verdict"] == "mixed"
assert O.house_report(sl, verdict_band=0.6)[4]["verdict"] == "mixed"
# Saturn Cancer: load 1.0 -> strained at the default band, mixed when the band is 1.0, strained again at 0.99
sc4 = chart({"Saturn": ["Cn", 15, 0, "Cn"]})
assert O.house_report(sc4)[3]["net"] == -1.0 and O.house_report(sc4)[3]["verdict"] == "strained"
assert O.house_report(sc4, verdict_band=0.99)[3]["verdict"] == "strained" and O.house_report(sc4, verdict_band=1.0)[3]["verdict"] == "mixed"
assert O.house_report(chart({}))[0]["verdict"] == "mixed"
cc = O.calculate(sc4)
assert set(cc) == {"warnings", "kp_dropped", "frame_weights", "frames_missing", "colour", "aspects", "houses", "house_final"}
assert len(cc["house_final"]) == 12 and [r["house"] for r in cc["house_final"]] == list(range(1, 13)) and cc["house_final"][3]["status"] == "d1"
OWNER_BODY = {1: "head, forehead, upper head, upper face", 2: "right eye, right side of face, neckline, upper neck, lips, lower right face",
              3: "right ear to right shoulder, upper right arm", 4: "lower right arm to wrist and hands, right chest and right breast",
              5: "right abdomen, right pocket, right hip, right stomach, upper right thigh", 6: "low right thigh, knee to ankle and feet",
              7: "waist and sexual part", 8: "low left thigh, knee to ankle and feet, inner anus",
              9: "left abdomen, left pocket, left hip, left stomach, upper left thigh", 10: "lower left arm to wrist and hands, left chest and left breast",
              11: "left ear to left shoulder, upper left arm", 12: "left eye, left side of face, lower left face, sexual activity"}
assert O.HOUSE_BODY == OWNER_BODY and "right pocket" in O.HOUSE_BODY[5] and "left pocket" not in O.HOUSE_BODY[5] and "left pocket" in O.HOUSE_BODY[9]
assert O.LK_PLANET_BODY == {"Mars": "liver", "Moon": "heart", "Ketu": "torso", "Mercury": "brain and tongue", "Saturn": "sight and assessment", "Rahu": "head", "Jupiter": "neck"}
mh = O.house_report({"lagna": ["Ar", 15, 0, "Ar"], "planets": {"Mars": ["Cn", 15, 0, "Cn"], "Moon": ["Sc", 15, 0, "Sc"], "Ketu": ["Ge", 15, 0, "Ge"]}})
assert mh[3]["lal_kitab_planet_parts"] == {"Mars": "liver"} and mh[7]["lal_kitab_planet_parts"] == {"Moon": "heart"} and mh[2]["lal_kitab_planet_parts"] == {"Ketu": "torso"}

# ---- 42. L3: the exhaustive check reports how many distinct cases it really evaluates, and its scope ----
st = O.enumerate_all()
assert st["distinct_cases_evaluated"] == 176 and "placement-only" in st["scope"]
assert sum(2 ** k - 1 for k in [len({r["planet"] for r in O.RULES if sg in r["signs"]}) for sg in O.SIGNS]) == 176
# recommend() ignoring the avoid list must now be caught by the exhaustive check too (all ranked colours are checked, not only the top two)
orig_rec = O.recommend
O.recommend = lambda rw, avoid, conflict=False: orig_rec(rw, set(), conflict)
try:
    assert O.enumerate_all()["violations"] > 0
finally:
    O.recommend = orig_rec
O.recommend = lambda rw, avoid, conflict=False: (lambda r: dict(r, ranked=r["ranked"] + [(c, 0.0) for c in sorted(avoid)]))(orig_rec(rw, avoid, conflict))
try:
    assert O.enumerate_all()["violations"] > 0                    # an avoided colour hiding BELOW the top two is also caught
finally:
    O.recommend = orig_rec
assert O.enumerate_all()["violations"] == 0


print("test_owner_calc ok")
