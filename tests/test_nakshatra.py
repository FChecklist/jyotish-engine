import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
import nakshatra as K
assert K.of_lon(0) == (1, 1) and K.of_lon(13.3333) == (1, 4) and K.of_lon(13.3334) == (2, 1) and K.of_lon(359.99) == (27, 4)
assert [K.ident(n)['lord'] for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 19, 27)] == ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury','Ketu','Ketu','Mercury']
assert sum(K.ident(n)['gana'] == 'Deva' for n in range(1, 28)) == 9 and sum(K.ident(n)['gana'] == 'Rakshasa' for n in range(1, 28)) == 9
assert [sum(K.ident(n)['nadi'] == x for n in range(1, 28)) for x in ('Adi', 'Madhya', 'Antya')] == [9, 9, 9]
assert K.ident(1)['yoni'] == 'Horse' and K.ident(24)['yoni'] == 'Horse' and K.ident(14)['yoni'] == 'Tiger'
s = K.day_signals(4, 1, 4, 1); assert s['janma_day'] and s['tara'] == 'Janma' and s['chandra_bala'] == 'good'
s = K.day_signals(4, 1, 13, 5); assert s['tara_no'] == 1 and s['anu_janma_day'] is True and s['janma_day'] is False and s['moon_house_from_natal_moon'] == 5 and s['chandra_bala'] == 'weak'
s = K.day_signals(4, 1, 5, 2); assert s['tara_no'] == 2 and s['tara'] == 'Sampat' and s['moon_house_from_natal_moon'] == 2
print('test_nakshatra ok')
