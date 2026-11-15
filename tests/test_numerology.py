import sys, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import numerology as N
assert N.reduce(29) == (2, False) and N.reduce(11) == (2, True) and N.reduce(10) == (1, False) and N.reduce(0) == (0, False)
assert N.energy('KA 07 1234')['raw_sum'] == 2 + 1 + 0 + 7 + 1 + 2 + 3 + 4 and N.energy(2026)['number'] == 1 and N.energy(2026)['planet'] == 0
d = datetime.date(1990, 3, 25)                                       # fictitious
e = N.energies(d, datetime.date(2026, 11, 15), name='Ram', house='12A')
assert e['dob']['number'] == 7 and e['month_of_birth']['number'] == 3
assert e['sum_of_dob']['raw_sum'] == 2 + 5 + 3 + 1 + 9 + 9 + 0 == 29 and e['sum_of_dob']['number'] == 2
assert e['self_age']['input'] == '36' and e['self_age']['number'] == 9      # birthday 25 Mar passed: age 36
assert e['name']['raw_sum'] == 2 + 1 + 4 and e['house_no']['raw_sum'] == 1 + 2 + 1
assert e['vehicle_no'] is None and e['exam_date'] is None
assert N.NUM_PLANET[9] == 2 and sorted(N.NUM_PLANET.values()) == [0, 1, 2, 3, 4, 5, 6, 7, 8]
print('test_numerology ok')
