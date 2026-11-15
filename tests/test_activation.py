import sys, os, datetime; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import activation as A
assert A.age_years(datetime.date(1980, 6, 15), datetime.date(2026, 6, 14)) == 45 and A.age_years(datetime.date(1980, 6, 15), datetime.date(2026, 6, 15)) == 46
s = A.planet_status(36); assert s['table_A_bphs_reference_page']['planets']['Saturn']['status'] == 'active_now' and s['table_A_bphs_reference_page']['planets']['Jupiter']['status'] == 'matured_earlier' and s['table_A_bphs_reference_page']['planets']['Ketu']['status'] == 'not_yet'
s2 = A.planet_status(34); assert s2['table_B_rath']['planets']['Jupiter']['status'] == 'active_now' and s2['table_A_bphs_reference_page']['planets']['Jupiter']['status'] == 'matured_earlier'   # schemes disagree on Jupiter: kept apart on purpose
by = {'Swati': [{'id': 'x', 'ages': [30, 60], 'kinds': ['golden'], 'text': 't', 'source': 's'}]}
assert A.nak_status('Swati', 45, by)[0]['age_now_in_or_near'] is True and A.nak_status('Swati', 20, by)[0]['age_now_in_or_near'] is False
print('test_activation ok')
