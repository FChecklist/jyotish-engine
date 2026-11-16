import sys, os, datetime; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import report, daily
natal = daily.natal_of(report.build(1990, 1, 1, 6, 0, 0, 5.5, 28.6139, 77.209))     # neutral chart, no family data
d0 = datetime.date(2026, 11, 1); bad = 0; seen_trip = 0
for k in range(120):
    items, _ = daily.day_items(natal, d0 + datetime.timedelta(days=k), 5.5, 28.6139, 77.209)
    dos = [i['text'] for i in items if i['kind'] == 'do']; donts = [i['text'] for i in items if i['kind'] == 'dont']
    trip = any('trip' in t for t in donts); seen_trip += trip
    if trip and any(t.startswith('Good for travel') for t in dos): bad += 1
assert seen_trip > 0 and bad == 0, (seen_trip, bad)
print('test_daily_conflict ok', seen_trip, 'days with a trip warning, 0 contradictions')
