"""Planet dignity in a D1 sign and graha drishti offsets. Tables from docs/CALCULATION_LEDGER.md. Rahu/Ketu: no dignity (schools differ)."""
SIGN_LORD = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]
EXALT = {0: 0, 1: 1, 2: 9, 3: 5, 4: 3, 5: 11, 6: 6}
DEBIL = {p: (s + 6) % 12 for p, s in EXALT.items()}
FRIENDS = {0: (1, 2, 4), 1: (0, 3), 2: (0, 1, 4), 3: (0, 5), 4: (0, 1, 2), 5: (3, 6), 6: (3, 5)}
ENEMIES = {0: (5, 6), 1: (), 2: (3,), 3: (1,), 4: (3, 5), 5: (0, 1), 6: (0, 1, 2)}
ASPECT_OFFSETS = {0: (7,), 1: (7,), 2: (4, 7, 8), 3: (7,), 4: (5, 7, 9), 5: (7,), 6: (3, 7, 10), 7: (5, 7, 9), 8: (5, 7, 9)}   # house counts from the planet
def states(p, sign0):
    """Set of dignity states of planet p (0..6) in sign0. Empty set for Rahu/Ketu."""
    if p not in EXALT: return set()
    out = set()
    if EXALT[p] == sign0: out.add('exalted')
    if DEBIL[p] == sign0: out.add('debilitated')
    lord = SIGN_LORD[sign0]
    if lord == p: out.add('own')
    else: out.add('friend' if lord in FRIENDS[p] else 'enemy' if lord in ENEMIES[p] else 'neutral')
    return out
def aspects_house(p, house_of_p):
    """Houses aspected by planet p sitting in house_of_p (1..12)."""
    return {(house_of_p + k - 2) % 12 + 1 for k in ASPECT_OFFSETS[p]}
def aspects_planet(p, house_p, house_q):
    return ((house_q - house_p) % 12 + 1) in ASPECT_OFFSETS[p]
