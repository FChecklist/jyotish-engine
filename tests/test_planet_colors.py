import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import planet_colors as C
assert len(C.PLANET_COLORS) == 12 and [r[0] for r in C.PLANET_COLORS] == list(range(1, 13))
assert C.BY_ENGINE_ID == {0: 'Orange', 1: 'White', 2: 'Red', 3: 'Green', 4: 'Yellow', 5: 'Off white', 6: 'Black', 7: 'Blue', 8: 'Gray'}
assert C.BY_NAME['Pluto'] == 'Dark black' and C.BY_NAME['Neptune'] == 'Ocean colour' and C.BY_NAME['Uranus'] == 'Opal white'
print('test_planet_colors ok')
