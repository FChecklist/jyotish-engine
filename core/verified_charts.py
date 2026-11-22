"""Verified reference charts: parse captured jagannathahora.com screens and load them into D1.

Why this exists
  The owner's four charts (RAJAT, PALLAVI, ESHANI, PEHU) were captured from his own logged-in
  jagannathahora.com account (read-only: only saved charts were opened). This module turns the
  captured screen text into structured rows and writes them into the project's own Cloudflare D1
  database (`jyotish-rules`) using the schema in migrations/0001_verified_charts.sql.

Rules (CLAUDE.md)
  * Family birth data NEVER goes in git. Input files live in data_private/ (git-ignored); this
    module only reads them and writes to D1. Tests use synthetic text only.
  * Credentials come from the environment (CLOUDFLARE_D1_TOKEN, CLOUDFLARE_ACCOUNT_ID); they are
    never printed or stored.
  * We do not recalculate charts. Values are stored exactly as the site displayed them.

Usage (from the repo root; needs the private folder next to it)
  python core/verified_charts.py --init            # create the tables (idempotent)
  python core/verified_charts.py --load RAJAT      # load one person
  python core/verified_charts.py --verify          # row counts per person
"""
import argparse
import base64
import glob
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

D1_DATABASE_ID = "c944c961-83f4-4035-882b-170072748b1f"  # jyotish-rules (docs/DECISIONS.md 2026-11-14)
VERIFIED_SOURCE = "jagannathahora.com"
SITE = "https://jagannathahora.com"
CHUNK_CHARS = 40000       # body text chunk (D1 row limit is 2 MB; statement limit 100 KB)
B64_CHUNK = 60000

SIGN_CODES = {"Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"}
_VARGA_CELL = re.compile(r"^(\d+)([A-Za-z]{2})(\d+)$")
_DEGMIN = re.compile(r"^(\d+)\D+(\d+)")
_DATE = re.compile(r"^[A-Z][a-z]{2} \d{1,2}, \d{4}$")
_DUR = re.compile(r"^\d+[ymd]( \d+[ymd])*$")

# ---------------------------------------------------------------- parsing (pure functions)


def parse_tables(text):
    """Group consecutive tab-separated lines into tables (list of list of cells)."""
    tables, cur = [], []
    for line in text.split("\n"):
        if "\t" in line:
            cur.append(line.split("\t"))
        elif cur:
            tables.append(cur)
            cur = []
    if cur:
        tables.append(cur)
    return tables


def _is_filler(row):
    return all(c.strip() in ("", "—", "-") for c in row)


def parse_key_info(text):
    """Details > Key Info. Returns rows: grp, body, longitude_text, deg, minute, nakshatra, pada, rasi, navamsha."""
    out = []
    grp = 0
    for tbl in parse_tables(text):
        if not tbl or [c.strip() for c in tbl[0][:3]] != ["Body", "Longitude", "Nakshatra"]:
            continue
        grp += 1
        for row in tbl[1:]:
            if _is_filler(row) or len(row) < 6:
                continue
            if row[0].strip() == "Body":  # repeated header inside a group
                grp += 1
                continue
            m = _DEGMIN.match(row[1])
            out.append({
                "grp": grp, "body": row[0].strip(), "longitude_text": row[1].strip(),
                "deg": int(m.group(1)) if m else None, "minute": int(m.group(2)) if m else None,
                "nakshatra": row[2].strip(), "pada": int(row[3]) if row[3].strip().isdigit() else None,
                "rasi": row[4].strip(), "navamsha": row[5].strip(),
            })
    return out


def parse_varga_table(text):
    """Details > All Bodies. Cells look like 0Le24 = 0 deg Leo 24 min. Returns rows body/varga/sign/deg/minute/raw."""
    out = []
    grp = 0
    for tbl in parse_tables(text):
        if not tbl or tbl[0][0].strip() != "Body":
            continue
        grp += 1
        header = [c.strip() for c in tbl[0]]
        for row in tbl[1:]:
            if _is_filler(row) or row[0].strip() == "Body":
                continue
            for varga, cell in zip(header[1:], row[1:]):
                cell = cell.strip()
                m = _VARGA_CELL.match(cell)
                out.append({
                    "grp": grp, "body": row[0].strip(), "varga": varga, "raw": cell,
                    "sign": m.group(2) if m else None,
                    "deg": int(m.group(1)) if m else None, "minute": int(m.group(3)) if m else None,
                })
    return out


def _parse_date(s):
    from datetime import datetime
    return datetime.strptime(s, "%b %d, %Y")


def parse_dasha_periods(text):
    """Flat dasha listing -> periods with derived nesting level.

    The page shows, per period: LORD [Now] START → END DURATION (one item per line). Nesting is not
    in the text, so level = number of earlier open periods that fully contain this one.
    """
    lines = [l.strip() for l in text.split("\n")]
    periods = []
    i = 0
    while i < len(lines):
        # a period starts at a lord line followed (optionally after 'Now') by date, '→', date, duration
        j = i + 1
        is_current = 0
        if j < len(lines) and lines[j] == "Now":
            is_current = 1
            j += 1
        if (j + 3 < len(lines) and _DATE.match(lines[j]) and lines[j + 1] == "→"
                and _DATE.match(lines[j + 2]) and _DUR.match(lines[j + 3]) and lines[i]
                and not _DATE.match(lines[i]) and lines[i] not in ("→", "Now")):
            periods.append({"lord": lines[i], "start_text": lines[j], "end_text": lines[j + 2],
                            "duration_text": lines[j + 3], "is_current": is_current})
            i = j + 4
        else:
            i += 1
    stack = []
    for seq, p in enumerate(periods, 1):
        s, e = _parse_date(p["start_text"]), _parse_date(p["end_text"])
        while stack and not (stack[-1][0] <= s and e <= stack[-1][1] and (stack[-1][0], stack[-1][1]) != (s, e)):
            # same-span as the parent is allowed for first child; handled below
            if stack[-1][0] <= s and e <= stack[-1][1]:
                break
            stack.pop()
        p["seq"] = seq
        p["level"] = len(stack) + 1
        stack.append((s, e))
    return periods


def parse_form(form_raw):
    """Form dump produced by the capture script: 'placeholder=value | ... || timebtn=6:15 AM'."""
    main, _, tb = form_raw.partition("|| timebtn=")
    vals = [seg.split("=", 1)[1].strip() if "=" in seg else seg.strip() for seg in main.split(" | ")]
    # order on the site: name, search, dob, city search, city, state, lat, lon, tz
    vals = [v for v in vals]
    return vals, tb.strip()


def person_record(form_raw, saved_chart_label, gender, doubts):
    """Build the vc_person fields from the capture script's form dump (values exactly as the site showed them).

    Form order on the site: name, date of birth, city search, city, state, latitude, longitude, time zone.
    """
    vals, tb = parse_form(form_raw)
    name, dob, _search, city, state, lat, lon, tz = vals[:8]
    d, m, y = dob.split("/")
    return {
        "display_name": name, "saved_chart_label": saved_chart_label, "gender": gender,
        "dob_iso": f"{int(y):04d}-{int(m):02d}-{int(d):02d}", "dob_site_text": dob,
        "tob_24h": to_24h(tb), "tob_site_text": tb, "place_city": city, "place_state": state,
        "latitude": float(lat), "longitude": float(lon), "timezone_site_text": tz,
        "form_raw": form_raw, "doubts": doubts,
    }


def to_24h(site_text):
    m = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)$", site_text.strip(), re.I)
    if not m:
        return None
    h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if ap == "AM":
        h = 0 if h == 12 else h
    else:
        h = h if h == 12 else h + 12
    return f"{h:02d}:{mi:02d}"


def chunk(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)] or [""]


def page_path_of(screen_key):
    head = screen_key.split(":")[0]
    return {"horoscope": "/horoscope", "details": "/details", "charts": "/charts", "dasha": "/dasha",
            "transits": "/transits", "saturn": "/saturn", "chakras": "/chakras", "strength": "/strength",
            "ashtakavarga": "/ashtakavarga", "yogas": "/yogas-doshas", "longevity": "/longevity",
            "arudhas": "/arudhas", "argala": "/argala", "sahams": "/sahams-sphutas",
            "analysis": "/analysis", "tithi": "/tithi-pravesha", "varshaphal": "/varshaphal"}.get(head)


# ---------------------------------------------------------------- D1 access


def _creds():
    tok = os.environ.get("CLOUDFLARE_D1_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN")
    acct = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if not tok or not acct:
        raise SystemExit("CLOUDFLARE_D1_TOKEN / CLOUDFLARE_ACCOUNT_ID not set in the environment")
    return tok, acct


def d1(statements):
    """Run a list of (sql, params) in one request. Returns the result list. Never prints credentials."""
    tok, acct = _creds()
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/d1/database/{D1_DATABASE_ID}/query"
    body = json.dumps({"batch": [{"sql": s, "params": p} for s, p in statements]}).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            res = json.loads(r.read())
    except urllib.error.HTTPError as e:  # show the API error text, never the request (it holds data/credentials)
        raise RuntimeError("D1 HTTP %s: %s" % (e.code, e.read()[:300].decode("utf-8", "replace")))
    if not res.get("success"):
        raise RuntimeError("D1 error: " + json.dumps(res.get("errors")))
    return res["result"]


def init_schema(migration_path=None):
    path = migration_path or os.path.join(os.path.dirname(__file__), "..", "migrations", "0001_verified_charts.sql")
    sql = open(path, encoding="utf-8").read()
    sql = "\n".join(l for l in sql.split("\n") if not l.strip().startswith("--"))
    stmts = [(s.strip(), []) for s in sql.split(";") if s.strip()]
    d1(stmts)
    return len(stmts)


# ---------------------------------------------------------------- loading


def build_statements(person_key, person, screens, shots, captured_at):
    """Pure: returns list of (sql, params) for one person. `screens` = {screen_key: text}."""
    st = []
    for t in ["vc_screen_chunk", "vc_screen", "vc_body_position", "vc_body_varga", "vc_dasha_period",
              "vc_screenshot_chunk", "vc_screenshot"]:
        st.append((f"DELETE FROM {t} WHERE person_key=?", [person_key]))
    st.append(("DELETE FROM vc_person WHERE person_key=?", [person_key]))
    st.append(("INSERT INTO vc_person (person_key,display_name,saved_chart_label,gender,dob_iso,dob_site_text,tob_24h,"
               "tob_site_text,place_city,place_state,latitude,longitude,timezone_site_text,source_url,verified_source,"
               "captured_at,form_raw,doubts_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
               [person_key, person["display_name"], person.get("saved_chart_label"), person.get("gender"),
                person.get("dob_iso"), person.get("dob_site_text"), person.get("tob_24h"), person.get("tob_site_text"),
                person.get("place_city"), person.get("place_state"), person.get("latitude"), person.get("longitude"),
                person.get("timezone_site_text"), SITE + "/horoscope", VERIFIED_SOURCE, captured_at,
                person.get("form_raw"), json.dumps(person.get("doubts", []), ensure_ascii=False)]))
    for key, text in screens.items():
        parts = chunk(text, CHUNK_CHARS)
        tables = parse_tables(text) if len(text) < 60000 else []
        st.append(("INSERT INTO vc_screen (person_key,screen_key,page_path,source_url,captured_at,char_count,n_chunks,tables_json)"
                   " VALUES (?,?,?,?,?,?,?,?)",
                   [person_key, key, page_path_of(key), SITE + (page_path_of(key) or ""), captured_at, len(text),
                    len(parts), json.dumps(tables, ensure_ascii=False) if tables else None]))
        for i, c in enumerate(parts):
            st.append(("INSERT INTO vc_screen_chunk (person_key,screen_key,seq,chunk) VALUES (?,?,?,?)",
                       [person_key, key, i, c]))
    ki = screens.get("details:Key Info")
    if ki:
        for r in parse_key_info(ki):
            st.append(("INSERT INTO vc_body_position (person_key,grp,body,longitude_text,deg,minute,nakshatra,pada,rasi,navamsha)"
                       " VALUES (?,?,?,?,?,?,?,?,?,?)",
                       [person_key, r["grp"], r["body"], r["longitude_text"], r["deg"], r["minute"], r["nakshatra"],
                        r["pada"], r["rasi"], r["navamsha"]]))
    ab = screens.get("details:All Bodies")
    if ab:
        for r in parse_varga_table(ab):
            st.append(("INSERT INTO vc_body_varga (person_key,grp,body,varga,sign,deg,minute,raw) VALUES (?,?,?,?,?,?,?,?)",
                       [person_key, r["grp"], r["body"], r["varga"], r["sign"], r["deg"], r["minute"], r["raw"]]))
    # graha dashas (Vimsottari and the other 27 systems, collapsed and expanded); rashi dashas stay as text only
    for key in [k for k in screens if k.startswith("dasha:graha")]:
        for p in parse_dasha_periods(screens[key]):
            st.append(("INSERT INTO vc_dasha_period (person_key,screen_key,seq,level,lord,start_text,end_text,duration_text,is_current)"
                       " VALUES (?,?,?,?,?,?,?,?,?)",
                       [person_key, key, p["seq"], p["level"], p["lord"], p["start_text"], p["end_text"],
                        p["duration_text"], p["is_current"]]))
    for s in shots:
        raw = s["bytes_data"]
        b64 = base64.b64encode(raw).decode()
        parts = chunk(b64, B64_CHUNK)
        st.append(("INSERT INTO vc_screenshot (person_key,file_name,screen_name,sha256,bytes,n_chunks,source_url,captured_at)"
                   " VALUES (?,?,?,?,?,?,?,?)",
                   [person_key, s["file"], s["screen"], hashlib.sha256(raw).hexdigest(), len(raw), len(parts),
                    SITE + "/horoscope", captured_at]))
        for i, c in enumerate(parts):
            st.append(("INSERT INTO vc_screenshot_chunk (person_key,file_name,seq,b64) VALUES (?,?,?,?)",
                       [person_key, s["file"], i, c]))
    return st


def run_batches(statements, max_bytes=900000, max_n=80):
    batch, size = [], 0
    for s, p in statements:
        sz = len(s) + sum(len(str(x)) for x in p)
        if batch and (size + sz > max_bytes or len(batch) >= max_n):
            d1(batch)
            batch, size = [], 0
        batch.append((s, p))
        size += sz
    if batch:
        d1(batch)


def load_person(person_key, private_dir):
    raw_dir = os.path.join(private_dir, "raw")
    meta = json.load(open(os.path.join(raw_dir, f"{person_key}_person.json"), encoding="utf-8"))
    screens = {}
    for f in sorted(glob.glob(os.path.join(raw_dir, f"{person_key}_*_text.json"))):
        screens.update(json.load(open(f, encoding="utf-8")))
    screens = {k: v for k, v in screens.items() if not k.endswith(":form") and k != "analysis:path"}
    shots = []
    sdir = os.path.join(private_dir, "screens")
    man = os.path.join(sdir, f"manifest_{person_key}.json")
    if os.path.exists(man):
        for m in json.load(open(man)):
            m["bytes_data"] = open(os.path.join(sdir, m["file"]), "rb").read()
            shots.append(m)
    st = build_statements(person_key, meta, screens, shots, meta["captured_at"])
    run_batches(st)
    return {"statements": len(st), "screens": len(screens), "shots": len(shots)}


def verify():
    out = {}
    for t in ["vc_person", "vc_screen", "vc_screen_chunk", "vc_body_position", "vc_body_varga", "vc_dasha_period",
              "vc_screenshot", "vc_screenshot_chunk"]:
        r = d1([(f"SELECT person_key, COUNT(*) AS n FROM {t} GROUP BY person_key", [])])[0]["results"]
        out[t] = {x["person_key"]: x["n"] for x in r}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--load")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--private-dir", default=os.path.join(os.path.dirname(__file__), "..", "data_private", "jagannathahora"))
    a = ap.parse_args()
    if a.init:
        print("statements applied:", init_schema())
    if a.load:
        print(load_person(a.load.upper(), a.private_dir))
    if a.verify:
        print(json.dumps(verify(), indent=1))
