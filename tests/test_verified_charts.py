"""Parsers of core/verified_charts.py on SYNTHETIC text only (no real birth data, no network)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import verified_charts as V

# --- tab-separated tables
t = "Heading\nBody\tLongitude\nSun\t1°02'\nMoon\t2°03'\nText\nBody\tX\nA\tB"
tabs = V.parse_tables(t)
assert len(tabs) == 2 and tabs[0][1] == ["Sun", "1°02'"] and tabs[1][0] == ["Body", "X"]

# --- Key Info (two groups, filler rows ignored)
ki = ("Key Info\nBody\tLongitude\tNakshatra\tPada\tRasi\tNavamsha\n"
      "Lagna\t10°05'\tAswini\t4\tAr\tCn\nSun - PiK\t0°00'\tBharani\t1\tAr\tAr\n—\t—\t—\t—\t—\t—\n"
      "Body\tLongitude\tNakshatra\tPada\tRasi\tNavamsha\nDhuma\t20°02'\tPurva Ashadha\t3\tSg\tLi\n")
rows = V.parse_key_info(ki)
assert len(rows) == 3
assert rows[0] == {"grp": 1, "body": "Lagna", "longitude_text": "10°05'", "deg": 10, "minute": 5,
                   "nakshatra": "Aswini", "pada": 4, "rasi": "Ar", "navamsha": "Cn"}
assert rows[2]["grp"] == 2 and rows[2]["body"] == "Dhuma" and rows[2]["deg"] == 20

# --- divisional table cells: 0Le24 -> 0 deg Leo 24 min
vt = "All Bodies\nBody\tD-1\tD-9\nLagna\t0Le24\t3Ar44\nSun\t29Pi59\t—\n"
va = V.parse_varga_table(vt)
assert len(va) == 4
assert va[0] == {"grp": 1, "body": "Lagna", "varga": "D-1", "raw": "0Le24", "sign": "Le", "deg": 0, "minute": 24}
assert va[2]["sign"] == "Pi" and va[2]["deg"] == 29 and va[2]["minute"] == 59
assert va[3]["sign"] is None and va[3]["raw"] == "—"          # missing cell kept as shown, not invented

# --- dasha periods: nesting level from date containment
d = ("Jupiter\nJan 01, 2000\n→\nJan 01, 2016\n16y\n"
     "Venus\nNow\nJan 01, 2016\n→\nJan 01, 2036\n20y\n"
     "Venus\nJan 01, 2016\n→\nJan 01, 2020\n4y\n"
     "Sun\nJan 01, 2020\n→\nJan 01, 2021\n1y\n"
     "Sun\nJan 01, 2020\n→\nMay 01, 2020\n4m\n"
     "Moon\nMay 01, 2020\n→\nJan 01, 2021\n8m\n"
     "Moon\nJan 01, 2021\n→\nJan 01, 2030\n9y\n"
     "Sun\nJan 01, 2036\n→\nJan 01, 2042\n6y\n")
ps = V.parse_dasha_periods(d)
assert [p["lord"] for p in ps] == ["Jupiter", "Venus", "Venus", "Sun", "Sun", "Moon", "Moon", "Sun"]
assert [p["level"] for p in ps] == [1, 1, 2, 2, 3, 3, 2, 1]
assert ps[1]["is_current"] == 1 and ps[0]["is_current"] == 0 and ps[1]["duration_text"] == "20y"

# --- form dump and time conversion
vals, tb = V.parse_form("name=X | date=01/02/2000 | city=Y || timebtn=10:20 PM")
assert vals == ["X", "01/02/2000", "Y"] and tb == "10:20 PM"
assert V.to_24h("10:20 PM") == "22:20" and V.to_24h("12:05 AM") == "00:05" and V.to_24h("12:30 PM") == "12:30"
assert V.to_24h("6:15 AM") == "06:15" and V.to_24h("garbage") is None

# --- statement builder: replaces rows, chunks long text, links screenshots
person = {"display_name": "TEST PERSON", "dob_iso": "2000-01-01", "tob_24h": "06:00"}
screens = {"details:Key Info": ki, "details:All Bodies": vt, "dasha:graha": d, "strength:base": "x" * 90000}
shots = [{"file": "T_01.jpg", "screen": "details", "bytes_data": b"\xff\xd8abc"}]
st = V.build_statements("TEST", person, screens, shots, "2026-01-01T00:00:00Z")
sqls = [s for s, _ in st]
assert sqls[0].startswith("DELETE FROM vc_screen_chunk") and sum(s.startswith("DELETE") for s in sqls) == 8
big = [p for s, p in st if s.startswith("INSERT INTO vc_screen_chunk") and p[1] == "strength:base"]
assert len(big) == 3 and sum(len(p[3]) for p in big) == 90000
assert sum(s.startswith("INSERT INTO vc_body_position") for s in sqls) == 3
assert sum(s.startswith("INSERT INTO vc_body_varga") for s in sqls) == 4
assert sum(s.startswith("INSERT INTO vc_dasha_period") for s in sqls) == 8
assert sum(s.startswith("INSERT INTO vc_screenshot_chunk") for s in sqls) == 1
person_row = [p for s, p in st if s.startswith("INSERT INTO vc_person")][0]
assert person_row[0] == "TEST" and "jagannathahora.com" in person_row  # verified_source flag
print("test_verified_charts ok")
