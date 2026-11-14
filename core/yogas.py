"""Position-only named yogas, nakshatra, retro and combust helpers. Definitions: docs/CALCULATION_LEDGER.md step 4."""
import dignity
KENDRA_FROM = (0, 3, 6, 9)
NAKS_N = 27
def nak_of(lon): return int(((lon % 360) * NAKS_N) // 360) + 1      # multiply first: exact at nakshatra borders
ORB = {1: 12.0, 2: 17.0, 3: 14.0, 4: 11.0, 5: 10.0, 6: 15.0}
ORB_RETRO = {3: 12.0, 5: 8.0}
def combust(p, lon, retro):
    if p not in ORB: return False
    orb = ORB_RETRO[p] if (p in retro and p in ORB_RETRO) else ORB[p]
    return abs((lon[p] - lon[0] + 180) % 360 - 180) < orb
def planet_from(p, ref, sg, houses): return (sg[p] - sg[ref]) % 12 + 1 in houses
def _from(ref, sg, k, who=(2, 3, 4, 5, 6)): return any((sg[q] - sg[ref]) % 12 == k for q in who)
PANCHA = {'ruchaka': 2, 'bhadra': 3, 'hamsa': 4, 'malavya': 5, 'sasa': 6}
NAMES = ('gajakesari', 'budhaditya', 'chandra_mangala', 'guru_chandala', 'shrapit', 'angarak', 'grahan', 'kemadruma', 'sunapha', 'anapha', 'duradhara', 'vesi', 'vosi', 'ubhayachari') + tuple(PANCHA)
def yoga(name, sg, house_of):
    """sg: {planet: sign0}; house_of: {planet: house in ONE view}. Returns bool."""
    if name == 'gajakesari': return (sg[4] - sg[1]) % 12 in KENDRA_FROM
    if name == 'budhaditya': return sg[0] == sg[3]
    if name == 'chandra_mangala': return sg[1] == sg[2]
    if name == 'guru_chandala': return sg[4] == sg[7]
    if name == 'shrapit': return sg[6] == sg[7]
    if name == 'angarak': return sg[2] == sg[7]
    if name == 'grahan': return any(sg[a] == sg[b] for a in (0, 1) for b in (7, 8))
    if name == 'kemadruma': return not any((sg[q] - sg[1]) % 12 in (0, 1, 11) for q in (2, 3, 4, 5, 6))
    if name in ('sunapha', 'anapha', 'duradhara'):
        s, a = _from(1, sg, 1), _from(1, sg, 11)
        return {'sunapha': s and not a, 'anapha': a and not s, 'duradhara': s and a}[name]
    if name in ('vesi', 'vosi', 'ubhayachari'):
        s, a = _from(0, sg, 1), _from(0, sg, 11)
        return {'vesi': s and not a, 'vosi': a and not s, 'ubhayachari': s and a}[name]
    if name in PANCHA:
        p = PANCHA[name]; st = dignity.states(p, sg[p])
        return bool(st & {'own', 'exalted'}) and house_of[p] in (1, 4, 7, 10)
    raise ValueError(name)
