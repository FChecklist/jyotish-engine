import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import rules_norm as N
def chart(asc, **s): return {'asc': asc, 'signs': {N.PL[k]: v for k, v in s.items()}}
# Aries lagna: Moon in Capricorn (sign 9) = 10th house
c = chart(0, moon=9, sun=0, mars=7, saturn=9, jupiter=3, venus=1, mercury=2, rahu=5, ketu=11)
p = N.parse('Moon in 10th house'); assert p['status'] == 'parsed' and p['atoms'] == [('planet_in_house', 1, (10,))]; assert N.evaluate(p, c) is True
p = N.parse('Moon in 9th house'); assert N.evaluate(p, c) is False
p = N.parse('Lal Kitab: Ketu in house 1', 'lalkitab'); assert p['status'] == 'parsed' and p['frame'] == 'aries_fixed' and N.evaluate(p, c) is False   # Ketu in Pisces = house 12
p = N.parse('Saturn in 10th house, weak'); assert p['status'] == 'partial' and N.evaluate(p, c) is None                      # never guess qualifiers
p = N.parse('Moon in 3rd or 10th house'); assert p['atoms'][0][2] == (3, 10) and N.evaluate(p, c) is True
p = N.parse('Mars in Scorpio'); assert p['status'] == 'parsed' and N.evaluate(p, c) is True
p = N.parse('10th lord in 10th'); assert p['status'] == 'parsed' and N.evaluate(p, c) is True      # Aries lagna: 10th sign Capricorn, lord Saturn in Capricorn = 10th
p = N.parse('Jupiter and Venus'); assert p['atoms'] == [('conj', 4, 5)] and N.evaluate(p, c) is False
p = N.parse('Rahu in example'); assert p['status'] == 'unparsed'
# frame shift: Taurus lagna, same planets
c2 = chart(1, moon=9); assert N.evaluate(N.parse('Moon in 9th house'), c2) is True
p = N.parse('Mars in 2nd / Mercury in 2nd / Jupiter in 2nd'); assert p['status'] == 'partial'   # slash = alternatives, not AND
p = N.parse('Sun in 3rd house and Moon in 4th house'); assert p['status'] == 'parsed' and len(p['atoms']) == 2
print('rules_norm tests passed')
