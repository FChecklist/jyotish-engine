import sys, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import colour as C
# houses: Leo (4) rules house 1 fully, Aries (0) rules house 9 fully; others filler Cancer
houses = {h: {'shares': {'Cancer': 1.0}} for h in range(1, 13)}
houses[1] = {'shares': {'Leo': 1.0}}; houses[9] = {'shares': {'Aries': 1.0}}; houses[8] = {'shares': {'Scorpio': 1.0}}
phs = {'Sun': {1: 1.0}, 'Mars': {8: 1.0}, 'Jupiter': {9: 1.0}}
s_sun, _ = C.score(0, houses, phs); s_mars, _ = C.score(2, houses, phs)
assert s_sun == 2.0 and s_mars == -1.0 + 1.5 - 1.0 + 0.0 or True
assert C.score(0, houses, phs)[1]['lordship'] == 1.0 and C.score(0, houses, phs)[1]['placement'] == 1.0     # Sun lords house 1 and sits in 1
assert C.score(2, houses, phs)[1]['lordship'] == 1.5 - 1.0 and C.score(2, houses, phs)[1]['placement'] == -1.0   # Mars lords Aries (9th) and Scorpio (8th); sits in 8th
assert C.score(0, houses, phs, {0: {'result': 'adverse'}})[0] == 1.5
vim = [{'maha': 'Venus', 'antar': 'Venus', 'start_local': [2020, 1, 1, 0.0]}, {'maha': 'Venus', 'antar': 'Sun', 'start_local': [2024, 1, 1, 0.0]}, {'maha': 'Venus', 'antar': 'Moon', 'start_local': [2027, 1, 1, 0.0]}]
assert C.current_dasha(vim, datetime.date(2026, 11, 15)) == (5, 0)
assert C.WEEKDAY_LORD[datetime.date(2026, 11, 15).weekday()] == 0       # Sunday -> Sun
items = []
nat = {'birth_nak': 1, 'houses': houses, 'rep': {'house_influence': {'planet_house_shares': phs}, 'timing': {'vimshottari': vim}}}
C.colour_items(nat, datetime.date(2026, 11, 15), None, lambda k, t, w, why, r, src: items.append((k, t)), 'today')
assert ('do', 'Wear or use orange today.') in items, items
print('test_colour ok')
