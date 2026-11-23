"""Owner colour-and-aspect calculator (rules of 2026-11-23, texts OWNER-2026-11-23-A/B/C in D1 jyotish-rules).
Plain code, no AI. Two calculators in one file:

1. colour_advice(chart)   - the 15 owner colour rules, aspect list, D1 Final = 0.5 D1 + 0.25 KP + 0.25 Bhav Chalit,
                            blends when several negatives meet in one zodiac, D9 validation with conflict-resolving mix.
2. aspect_table(chart)    - final aspect % = (P1 owner degree ladder + P2 western + P3 Vedic + P4 Lal Kitab) / 4.

Chart input (no birth data is stored in git; pass it in at run time):
  {"lagna": [sign, deg, min, d9_sign], "planets": {"Sun": [sign, deg, min, d9_sign], ...},
   "birth": {"date": "YYYY-MM-DD", "time": "HH:MM", "tz": 5.5, "lat": .., "lon": ..}}   # birth is optional: needed for KP
Signs are 2-letter codes Ar Ta Ge Cn Le Vi Li Sc Sg Cp Aq Pi (sidereal, as on jagannathahora.com).

ASSUMPTIONS (owner to confirm; each is one named constant or function):
  ASPECT_W            colour rules: an aspect-only hit weighs 0.5 of a placement hit (owner gave no figure for the colour rules).
  P1 orbs             owner wrote "+/- 5%, 10%, 15%": read as percent OF the aspect angle (5% of 180 = 9 deg). Absolute degrees would be a one-line change.
  P2 orbs             western conjunction/square/trine/opposition 8 deg, sextile 6 deg, strength falls linearly to 0 at the orb edge.
  P3 partial aspects  Parashara 3rd/10th = 25, 5th/9th = 50, 4th/8th = 75 for the 7 classical planets; full on the owner's list and on conjunction.
  P4 Lal Kitab        house-to-house table from B.M. Goswami, "Lal Kitab" (English, based on the 1952 edition), chapter Planetary Aspect, pp.118-124
                      (archive.org/details/jyotishlalkitabb.m.gosvami): 1->7 100, 4->10 100, 3->9 and 3->11 50, 5->9 50, 2->6 25, 6->12 25, 8->2 25
                      (the book also says 8->2 is 100 in one passage: conflict, 25 used). Mercury, Rahu and Ketu have special rules in the book: NOT modelled.
                      Houses are counted from the lagna sign (whole sign). Provisional until the owner confirms the source.
  KP                  sidereal Placidus; ayanamsa is calibrated so the computed ascendant equals the site's lagna (the site gives only degrees).
  Bhav Chalit         equal house, each house spans cusp +/- 15 deg, cusp 1 = lagna longitude.
"""
import itertools, math, json, sys

SIGNS = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]
S = {s: i for i, s in enumerate(SIGNS)}
NAME = dict(Ar="Aries", Ta="Taurus", Ge="Gemini", Cn="Cancer", Le="Leo", Vi="Virgo", Li="Libra", Sc="Scorpio",
            Sg="Sagittarius", Cp="Capricorn", Aq="Aquarius", Pi="Pisces")

# (no, planet, trigger signs, use colours, avoid colours) - owner text OWNER-2026-11-23-A; rule 5 "And" and Sun Taurus/Libra confirmed in -C
RULES = [dict(no=n, planet=p, signs=t.split(), use=u.split(), avoid=a.split()) for n, p, t, u, a in [
    (1, "Sun", "Ta Li", "blue", "orange"),
    (2, "Moon", "Sc Ar", "red yellow", "white black"),
    (3, "Mars", "Cn", "blue yellow", "red"),
    (4, "Mercury", "Pi Cn", "yellow blue grey", "green brown red"),
    (5, "Jupiter", "Cp Aq", "black red", "yellow golden"),
    (6, "Venus", "Vi Ge Cn", "blue green", "white silver"),
    (7, "Saturn", "Ar Sc", "red yellow grey", "white black"),
    (8, "Saturn", "Cn", "yellow grey", "red"),
    (9, "Rahu", "Sg", "yellow green black", "brown blue"),
    (10, "Ketu", "Ge", "green purple", "grey silver"),
    (11, "Uranus", "Cn Ta Li", "yellow", "red orange"),
    (12, "Neptune", "Ar Sc Ge", "red yellow green", "black white grey silver"),
    (13, "Neptune", "Cn", "yellow", "red"),
    (14, "Pluto", "Ar Sc Le", "red yellow", "white black"),
    (15, "Pluto", "Cn", "yellow", "red")]]
# house numbers counted from the planet's own sign (1 = the sign it sits in)
ASPECTS = {"Sun": [7], "Mercury": [7], "Venus": [7], "Moon": [7], "Mars": [4, 7, 8], "Jupiter": [5, 7, 9],
           "Saturn": [3, 7, 10], "Rahu": [7], "Ketu": [7], "Uranus": [7], "Neptune": [7], "Pluto": [7]}
ASPECT_W = 0.5
FRAME_W = {"D1": 0.5, "KP": 0.25, "BC": 0.25}
MIX = {frozenset(["blue", "yellow"]): "green", frozenset(["red", "yellow"]): "orange",
       frozenset(["red", "blue"]): "purple", frozenset(["black", "white"]): "grey",
       frozenset(["red", "green"]): "brown", frozenset(["red", "white"]): "pink",
       frozenset(["blue", "white"]): "light blue", frozenset(["yellow", "green"]): "lime"}


# Owner Principle 1 (text OWNER-2026-11-23-D): houses and body parts
HOUSE_BODY = {
    1: "head, forehead, upper head, upper face",
    2: "right eye, right side of face, neckline, upper neck, lips, lower right face",
    3: "right ear to right shoulder, upper right arm",
    4: "lower right arm to wrist and hands, right chest and right breast",
    5: "right abdomen, right pocket, right hip, right stomach, upper right thigh",
    6: "low right thigh, knee to ankle and feet",
    7: "waist and sexual part",
    8: "low left thigh, knee to ankle and feet, inner anus",
    9: "left abdomen, left pocket, left hip, left stomach, upper left thigh",
    10: "lower left arm to wrist and hands, left chest and left breast",
    11: "left ear to left shoulder, upper left arm",
    12: "left eye, left side of face, lower left face, sexual activity"}
# Owner Principle 2 (Lal Kitab, Goswami p.? "Different Parts of Body are Controlled as Under"): body parts per PLANET. Sun and Venus are not in the excerpt read.
LK_PLANET_BODY = {"Mars": "liver", "Moon": "heart", "Ketu": "torso", "Mercury": "brain and tongue",
                  "Saturn": "sight and assessment", "Rahu": "head", "Jupiter": "neck"}
# Lal Kitab house-to-house aspect (Goswami pp.118-124): from house -> {to house: strength %}
LK_ASPECT = {1: {7: 100}, 2: {6: 25}, 3: {9: 50, 11: 50}, 4: {10: 100}, 5: {9: 50}, 6: {12: 25}, 8: {2: 25}}
# Classical dignity (assumption: used only for the + side of a house; owner has not given a + table)
EXALT = {"Sun": "Ar", "Moon": "Ta", "Mars": "Cp", "Mercury": "Vi", "Jupiter": "Cn", "Venus": "Pi", "Saturn": "Li"}
DEBIL = {"Sun": "Li", "Moon": "Sc", "Mars": "Cn", "Mercury": "Pi", "Jupiter": "Cp", "Venus": "Vi", "Saturn": "Ar"}
OWN = {"Sun": ["Le"], "Moon": ["Cn"], "Mars": ["Ar", "Sc"], "Mercury": ["Ge", "Vi"], "Jupiter": ["Sg", "Pi"],
       "Venus": ["Ta", "Li"], "Saturn": ["Cp", "Aq"]}


def dignity(planet, sign):
    if EXALT.get(planet) == sign: return 1.0
    if sign in OWN.get(planet, []): return 0.5
    if DEBIL.get(planet) == sign: return -1.0
    return 0.0


def longitude(entry):
    return S[entry[0]] * 30 + entry[1] + entry[2] / 60.0


# ---------------- houses: Bhav Chalit and KP ----------------
def bhav_chalit_house(lag_lon, lon):
    return int((((lon - lag_lon + 15) % 360) // 30) + 1)


def _julian_day(date, time, tz):
    y, m, d = map(int, date.split("-")); hh, mm = map(int, time.split(":"))
    ut = hh + mm / 60.0 - tz
    if m <= 2: y -= 1; m += 12
    a = y // 100; b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5 + ut / 24.0


def placidus_cusps(jd, lat, lon):
    """Tropical Placidus cusps {1..12} in degrees."""
    t = (jd - 2451545.0) / 36525.0
    e = math.radians(23.4392911 - 0.0130042 * t)
    ramc = ((280.46061837 + 360.98564736629 * (jd - 2451545.0)) + lon) % 360
    r = math.radians(ramc); ph = math.radians(lat)
    mc = math.degrees(math.atan2(math.sin(r), math.cos(r) * math.cos(e))) % 360
    asc = math.degrees(math.atan2(math.cos(r), -(math.sin(r) * math.cos(e) + math.tan(ph) * math.sin(e)))) % 360

    def ecl(ra):
        return math.degrees(math.atan2(math.sin(math.radians(ra)), math.cos(math.radians(ra)) * math.cos(e))) % 360

    def cusp(frac, above):
        lam = ramc if above else ramc + 180
        for _ in range(60):
            dec = math.asin(math.sin(e) * math.sin(math.radians(lam)))
            ad = math.degrees(math.asin(max(-1, min(1, math.tan(ph) * math.tan(dec)))))
            ra = ramc + frac * (90 + ad) if above else ramc + 180 - frac * (90 - ad)
            new = ecl(ra % 360)
            done = abs(((new - lam + 180) % 360) - 180) < 1e-9
            lam = new
            if done: break
        return lam % 360
    c = {10: mc, 1: asc, 11: cusp(1 / 3, True), 12: cusp(2 / 3, True), 2: cusp(2 / 3, False), 3: cusp(1 / 3, False)}
    for h in (4, 5, 6, 7, 8, 9):
        c[h] = (c[h + 6 if h <= 6 else h - 6] + 180) % 360
    return c


def house_in(cusps, lon):
    for h in range(1, 13):
        a = cusps[h]; b = cusps[h % 12 + 1]
        if ((lon - a) % 360) < ((b - a) % 360): return h
    return 1


def validate_chart(chart):
    """Reject malformed input with a clear message instead of a bare KeyError or a silently wrong answer."""
    for key in ("lagna", "planets"):
        if key not in chart: raise ValueError(f"chart needs '{key}'")
    for name, e in [("lagna", chart["lagna"])] + list(chart["planets"].items()):
        if len(e) < 4 or e[0] not in S or e[3] not in S: raise ValueError(f"{name}: need [sign, deg, min, d9 sign] with signs from {sorted(S)}")
        if not (0 <= e[1] < 30 and 0 <= e[2] < 60): raise ValueError(f"{name}: degrees must be 0-29 and minutes 0-59, got {e[1]}, {e[2]}")
    b = chart.get("birth")
    if b:
        for key in ("date", "time", "tz", "lat", "lon"):
            if key not in b: raise ValueError(f"birth needs '{key}' (time zone is never guessed)")


def frames(chart):
    """Effective sign of every planet in D1, KP and Bhav Chalit (sign of the house it falls in, counted from the lagna sign)."""
    lag = longitude(chart["lagna"]); lag_s = int(lag // 30)
    pl = {p: longitude(v) for p, v in chart["planets"].items()}
    d1 = {p: int(l // 30) for p, l in pl.items()}
    bc = {p: (lag_s + bhav_chalit_house(lag, l) - 1) % 12 for p, l in pl.items()}
    out = {"D1": d1, "BC": bc}; info = {}
    b = chart.get("birth")
    if b:
        tc = placidus_cusps(_julian_day(b["date"], b["time"], b["tz"]), b["lat"], b["lon"])
        ayan = (tc[1] - lag) % 360
        sc = {h: (tc[h] - ayan) % 360 for h in tc}
        out["KP"] = {p: (lag_s + house_in(sc, l) - 1) % 12 for p, l in pl.items()}
        info["ayanamsa_calibrated"] = round(ayan, 3)
        warn = []
        if not 22.0 <= ayan <= 26.0: warn.append(f"calibrated ayanamsa {ayan:.1f} deg is outside 22-26: lagna, place or time probably wrong, KP frame not trustworthy")
        if abs(b["lat"]) > 66: warn.append("latitude above 66: Placidus houses are undefined, KP frame not trustworthy")
        if warn: info["warnings"] = warn
    return out, lag_s, info


# ---------------- colour rules ----------------
def rule_hits(sign_of):
    """{(rule no, sign index): weight}: placement 1.0, aspect-only ASPECT_W."""
    out = {}
    for r in RULES:
        p = r["planet"]
        if p not in sign_of: continue
        s = sign_of[p]; trig = [S[x] for x in r["signs"]]
        if s in trig: out[(r["no"], s)] = 1.0
        for n in ASPECTS[p]:
            a = (s + n - 1) % 12
            if a in trig and a != s: out[(r["no"], a)] = max(out.get((r["no"], a), 0), ASPECT_W)
    return out


def advise(rule_nos, extra_avoid=()):
    use, avoid = set(), set(extra_avoid)
    for n in rule_nos:
        r = RULES[n - 1]; use |= set(r["use"]); avoid |= set(r["avoid"])
    pure = sorted(use - avoid)
    res = {"use": pure, "avoid": sorted(avoid)}
    if not pure or len(rule_nos) > 1:
        res["blends"] = [f"{a}+{b}={MIX[frozenset([a, b])]}" for a, b in itertools.combinations(sorted(use - avoid), 2)
                         if frozenset([a, b]) in MIX and MIX[frozenset([a, b])] not in avoid]
        res["blends_rejected"] = [f"{a}+{b}={MIX[frozenset([a, b])]}" for a, b in itertools.combinations(sorted(use), 2)
                                  if frozenset([a, b]) in MIX and MIX[frozenset([a, b])] in avoid]
    return res


def recommend(rule_weights, avoid):
    """Decisive remedy for one zodiac: rank every allowed colour by the total rule weight whose use list contains it; ties go to the colour
    the owner listed first. primary = best; secondary = next; blend = primary+secondary ONLY when two or more rules meet in the zodiac
    (owner: "if a zodiac has two or more negatives, use a combination") and the mix is not on an avoid list."""
    cov, pos = {}, {}
    for n, w in rule_weights:
        for i, c in enumerate(RULES[n - 1]["use"]):
            if c not in avoid:
                cov[c] = cov.get(c, 0) + w
                pos[c] = min(pos.get(c, 99), i)
    ranked = sorted(cov.items(), key=lambda kv: (-kv[1], pos[kv[0]], kv[0]))
    out = {"ranked": [(c, round(v, 3)) for c, v in ranked], "primary": ranked[0][0] if ranked else None,
           "secondary": ranked[1][0] if len(ranked) > 1 else None, "blend": None}
    if out["secondary"] and len({n for n, _ in rule_weights}) > 1:
        m = MIX.get(frozenset([out["primary"], out["secondary"]]))
        if m and m not in avoid: out["blend"] = f"{out['primary']}+{out['secondary']}={m}"
    return out


def colour_advice(chart):
    validate_chart(chart)
    fr, lag_s, info = frames(chart)
    w = {k: v for k, v in FRAME_W.items() if k in fr}
    tot = sum(w.values()); w = {k: v / tot for k, v in w.items()}          # KP missing -> renormalise, and say so
    fh = {f: rule_hits(fr[f]) for f in fr}
    final = {k: sum(w[f] * fh[f].get(k, 0) for f in fr) for k in set().union(*fh.values())}
    d9 = {p: S[v[3]] for p, v in chart["planets"].items()}
    d9h = rule_hits(d9)
    zod = []
    by = {}
    for (n, s), v in final.items():
        if v > 0: by.setdefault(s, []).append((n, v))
    for s, lst in sorted(by.items()):
        nos = sorted(n for n, _ in lst)
        adv = advise(nos)
        d9_avoid = set()
        for (n, ss) in d9h:
            if ss == s: d9_avoid |= set(RULES[n - 1]["avoid"])
        final_adv = advise(nos, d9_avoid)
        z = {"zodiac": NAME[SIGNS[s]], "house_d1": (s - lag_s) % 12 + 1,
             "total_weight": round(sum(v for _, v in lst), 3),
             "rules": [{"rule": n, "weight": round(v, 3), **{f.lower(): fh[f].get((n, s), 0) for f in fr}} for n, v in sorted(lst)],
             "d1_final": adv, "d9_avoid": sorted(d9_avoid), "approved": final_adv}
        z["d9_conflict"] = sorted(set(adv["use"]) & d9_avoid)
        z["remedy"] = recommend([(r["rule"], r["weight"]) for r in z["rules"]], set(final_adv["avoid"]))
        if not final_adv["use"] and not final_adv.get("blends"):
            z["note"] = "no colour or blend satisfies D1 Final and D9 together - owner decision"
        zod.append(z)
    return {"lagna": NAME[SIGNS[lag_s]], "frame_weights": w, "frames_missing": [f for f in FRAME_W if f not in fr],
            **info, "zodiacs": zod}


# ---------------- aspect % ----------------
CLASSICAL = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
PARTIAL = {3: 25, 10: 25, 5: 50, 9: 50, 4: 75, 8: 75}
WEST = [(0, 8, "conjunction"), (60, 6, "sextile"), (90, 8, "square"), (120, 8, "trine"), (180, 8, "opposition")]


def p1_owner_degree(planet, la, lb):
    d = (lb - la) % 360; best = 0
    for n in ASPECTS[planet]:
        ex = (n - 1) * 30
        pct = abs(d - ex) / ex * 100
        best = max(best, 100 if pct <= 5 else 75 if pct <= 10 else 50 if pct <= 15 else 0)
    return best


def p2_western(la, lb):
    d = abs(la - lb) % 360; d = min(d, 360 - d); best, name = 0.0, ""
    for ang, orb, nm in WEST:
        o = abs(d - ang)
        if o <= orb and 100 * (1 - o / orb) > best: best, name = 100 * (1 - o / orb), nm
    return best, name


def p3_vedic(planet, sa, sb):
    n = (sb - sa) % 12 + 1
    if n == 1 or n in ASPECTS[planet]: return 100
    return PARTIAL.get(n, 0) if planet in CLASSICAL else 0


def lal_kitab_aspect(planet, house_a, house_b):
    """P4: Lal Kitab house-to-house aspect strength % (from house_a to house_b), 0 when none. None if houses are unknown."""
    if house_a is None or house_b is None: return None
    return LK_ASPECT.get(house_a, {}).get(house_b, 0)


def aspect_table(chart):
    pl = {p: longitude(v) for p, v in chart["planets"].items()}
    sg = {p: int(l // 30) for p, l in pl.items()}
    lag_s = int(longitude(chart["lagna"]) // 30) if chart.get("lagna") else None
    hs = {p: (sg[p] - lag_s) % 12 + 1 for p in sg} if lag_s is not None else {}
    best = {}
    for a, b in itertools.permutations(pl, 2):
        if {a, b} == {"Rahu", "Ketu"}: continue
        v1 = p1_owner_degree(a, pl[a], pl[b]); v2, nm = p2_western(pl[a], pl[b]); v3 = p3_vedic(a, sg[a], sg[b])
        v4 = lal_kitab_aspect(a, hs.get(a), hs.get(b))
        r = {"from": a, "to": b, "separation": round((pl[b] - pl[a]) % 360, 1), "p1": v1, "p2": round(v2), "western": nm,
             "p3": v3, "p4": v4, "final": round((v1 + v2 + v3 + (v4 or 0)) / 4, 1), "p4_pending": v4 is None,
             "final_is_lower_bound": v4 is None}      # no lagna -> P4 unknown, counted as 0, so the figure can only be too low
        k = frozenset([a, b])
        if k not in best or r["final"] > best[k]["final"]: best[k] = r
    return sorted((r for r in best.values() if r["final"] > 0), key=lambda r: -r["final"])

# ---------------- house report: constant houses, moving zodiacs ----------------
def house_report(chart, verdict_band=0.25):
    """For each of the 12 houses: zodiac in it, planets in it, owner negative load (D1 Final weights of the 15 rules on that zodiac),
    classical dignity of the planets sitting there (the + side, assumption), net, body parts (owner P1, Lal Kitab planet parts P2), colours."""
    col = colour_advice(chart)
    by_zod = {z["zodiac"]: z for z in col["zodiacs"]}
    lag_s = int(longitude(chart["lagna"]) // 30)
    out = []
    for h in range(1, 13):
        s = (lag_s + h - 1) % 12
        sg = SIGNS[s]
        here = [p for p, v in chart["planets"].items() if S[v[0]] == s]
        z = by_zod.get(NAME[sg])
        neg = z["total_weight"] if z else 0.0
        plus = sum(max(dignity(p, sg), 0) for p in here)
        minus_dig = sum(min(dignity(p, sg), 0) for p in here)
        net = round(plus + minus_dig - neg, 3)
        verdict = "supportive" if net > verdict_band else "strained" if net < -verdict_band else "mixed"
        involved = sorted({RULES[r["rule"] - 1]["planet"] for r in z["rules"]}) if z else []
        row = {"house": h, "zodiac": NAME[sg], "planets_here": here, "owner_negative_load": neg,
               "dignity_plus": plus, "dignity_minus": minus_dig, "net": net, "verdict": verdict,
               "body_parts": HOUSE_BODY[h],
               "lal_kitab_planet_parts": {p: LK_PLANET_BODY[p] for p in involved if p in LK_PLANET_BODY},
               "colour_use": z["approved"]["use"] if z else [], "colour_avoid": z["approved"]["avoid"] if z else [],
               "colour_blends": z["approved"].get("blends", []) if z else [],
               "remedy": z["remedy"] if z else None}
        out.append(row)
    return out


def all_triples():
    """Every house (1-12) x every zodiac (12) x every planet (12) = 1,728 rows: what that planet does if it sits in that zodiac in that house,
    on its own. Columns: house, body parts, zodiac, planet, owner rules fired (placement), classical dignity, colours to use, colours to avoid."""
    rows = []
    for h in range(1, 13):
        for sg in SIGNS:
            for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]:
                nos = [r["no"] for r in RULES if r["planet"] == p and sg in r["signs"]]
                a = advise(nos) if nos else {"use": [], "avoid": []}
                rows.append({"house": h, "body_parts": HOUSE_BODY[h], "zodiac": NAME[sg], "planet": p,
                             "owner_rules": " ".join(map(str, nos)), "dignity": dignity(p, sg),
                             "colour_use": " ".join(a["use"]), "colour_avoid": " ".join(a["avoid"])})
    return rows


# ---------------- exhaustive check of every combination ----------------
def enumerate_all():
    """Every zodiac x every subset of the 12 planets sitting in it (12 x 4096 = 49,152 cases; planets with no rule on a zodiac cannot change the
    advice, so each zodiac is enumerated over its relevant planets and every such case stands for 2^(12-k) full cases).
    Checks the invariant that no advised colour is ever on an avoid list, and counts the cases with no pure colour / no blend left."""
    stats = {"zodiacs": 12, "full_cases": 12 * 4096, "cases_with_a_rule": 0, "one_colour_good_for_every_planet": 0, "pure_ok": 0, "blend_only": 0, "unresolvable": 0,
             "violations": 0, "worst": []}
    for sg in SIGNS:
        rel = sorted({r["planet"] for r in RULES if sg in r["signs"]})
        mult = 2 ** (12 - len(rel))
        for k in range(1, len(rel) + 1):
            for sub in itertools.combinations(rel, k):
                nos = [r["no"] for r in RULES if r["planet"] in sub and sg in r["signs"]]
                a = advise(nos)
                stats["cases_with_a_rule"] += mult
                # independent of advise(): recompute the avoid union straight from RULES, then check what recommend() actually advises
                avoid_all = set().union(*[set(RULES[n - 1]["avoid"]) for n in nos])
                rec = recommend([(n, 1.0) for n in nos], avoid_all)
                advised = [c for c in (rec["primary"], rec["secondary"]) if c]
                if not rec["primary"] or set(advised) & avoid_all or set(a["use"]) & avoid_all or (rec["blend"] and rec["blend"].split("=")[1] in avoid_all):
                    stats["violations"] += mult
                common = set.intersection(*[set(RULES[n - 1]["use"]) for n in nos]) - set(a["avoid"])
                if common: stats["one_colour_good_for_every_planet"] += mult
                if a["use"]: stats["pure_ok"] += mult
                elif a.get("blends"): stats["blend_only"] += mult
                else:
                    stats["unresolvable"] += mult
                    if len(stats["worst"]) < 12: stats["worst"].append({"zodiac": NAME[sg], "planets": list(sub), "rules": nos})
    return stats


def house_final_table(chart):
    """Owner's house-by-house view (owner confirmed 2026-11-23: D9 is checked HOUSE BY HOUSE, D9 house h counted from the D9 lagna).
    Per house: D1 zodiac + avoid, D9 zodiac + avoid, D1 recommended, D9 recommended, FINAL. D1 Final is the base; D9 can only veto colours,
    it never adds colours to a house where D1 has a rule. If D1 has no rule but D9 has, the final is the D9 advice, labelled D9-only."""
    col = colour_advice(chart)
    by = {z["zodiac"]: z for z in col["zodiacs"]}
    lag_s = int(longitude(chart["lagna"]) // 30)
    d9lag = S[chart["lagna"][3]]
    d9h = rule_hits({p: S[v[3]] for p, v in chart["planets"].items()})
    rows = []
    for h in range(1, 13):
        s1, s9 = (lag_s + h - 1) % 12, (d9lag + h - 1) % 12
        z = by.get(NAME[SIGNS[s1]])
        r1 = [(r["rule"], r["weight"]) for r in z["rules"]] if z else []
        a1 = set(z["d1_final"]["avoid"]) if z else set()
        r9 = [(n, w) for (n, s), w in d9h.items() if s == s9]
        a9 = set()
        for n, _ in r9: a9 |= set(RULES[n - 1]["avoid"])
        rec1 = recommend(r1, a1) if r1 else None
        rec9 = recommend(r9, a9) if r9 else None
        if r1:
            fin = recommend(r1, a1 | a9)
            vetoed = sorted({c for c, _ in rec1["ranked"]} & a9)
            status = "d1_with_d9_veto" if vetoed else "d1"
            if not fin["primary"]: status = "clash_owner_decision"
        elif r9:
            fin, vetoed, status = rec9, [], "d9_only"
        else:
            fin, vetoed, status = None, [], "no_rule"
        rows.append({"house": h, "d1_zodiac": NAME[SIGNS[s1]], "d1_avoid": sorted(a1), "d9_zodiac": NAME[SIGNS[s9]], "d9_avoid": sorted(a9),
                     "d1_recommended": rec1, "d9_recommended": rec9, "final": fin, "d9_vetoed": vetoed, "status": status})
    return rows


def calculate(chart):
    return {"colour": colour_advice(chart), "aspects": aspect_table(chart), "houses": house_report(chart), "house_final": house_final_table(chart)}


if __name__ == "__main__":
    # usage: python owner_calc.py chart.json   (chart.json is NOT committed: it holds birth data)
    print(json.dumps(calculate(json.load(open(sys.argv[1]))), indent=1))
