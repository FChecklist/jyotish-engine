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
  P4 Lal Kitab        NO verified table found. lal_kitab_aspect() returns None (pending); final % is then a LOWER BOUND with P4 = 0.
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


def frames(chart):
    """Effective sign of every planet in D1, KP and Bhav Chalit (sign of the house it falls in, counted from the lagna sign)."""
    lag = longitude(chart["lagna"]); lag_s = int(lag // 30)
    pl = {p: longitude(v) for p, v in chart["planets"].items()}
    d1 = {p: int(l // 30) for p, l in pl.items()}
    bc = {p: (lag_s + bhav_chalit_house(lag, l) - 1) % 12 for p, l in pl.items()}
    out = {"D1": d1, "BC": bc}; info = {}
    b = chart.get("birth")
    if b:
        tc = placidus_cusps(_julian_day(b["date"], b["time"], b.get("tz", 5.5)), b["lat"], b["lon"])
        ayan = (tc[1] - lag) % 360
        sc = {h: (tc[h] - ayan) % 360 for h in tc}
        out["KP"] = {p: (lag_s + house_in(sc, l) - 1) % 12 for p, l in pl.items()}
        info["ayanamsa_calibrated"] = round(ayan, 3)
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


def colour_advice(chart):
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
    """PENDING: no verified Lal Kitab aspect table. Returns None; the final % is then a lower bound (P4 = 0)."""
    return None


def aspect_table(chart):
    pl = {p: longitude(v) for p, v in chart["planets"].items()}
    sg = {p: int(l // 30) for p, l in pl.items()}
    best = {}
    for a, b in itertools.permutations(pl, 2):
        if {a, b} == {"Rahu", "Ketu"}: continue
        v1 = p1_owner_degree(a, pl[a], pl[b]); v2, nm = p2_western(pl[a], pl[b]); v3 = p3_vedic(a, sg[a], sg[b])
        v4 = lal_kitab_aspect(a, None, None)
        r = {"from": a, "to": b, "separation": round((pl[b] - pl[a]) % 360, 1), "p1": v1, "p2": round(v2), "western": nm,
             "p3": v3, "p4": v4, "final": round((v1 + v2 + v3 + (v4 or 0)) / 4, 1), "p4_pending": v4 is None}
        k = frozenset([a, b])
        if k not in best or r["final"] > best[k]["final"]: best[k] = r
    return sorted((r for r in best.values() if r["final"] > 0), key=lambda r: -r["final"])


def calculate(chart):
    return {"colour": colour_advice(chart), "aspects": aspect_table(chart)}


if __name__ == "__main__":
    # usage: python owner_calc.py chart.json   (chart.json is NOT committed: it holds birth data)
    print(json.dumps(calculate(json.load(open(sys.argv[1]))), indent=1))
