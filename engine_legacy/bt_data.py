# Backtest set: public figures. Birth data typed from memory of public records (Rodden-style). grade: A=birth record/time well known, B=time quoted widely but less certain.
# (name, grade, local datetime, tz hours east, lat, lon, [events])
from datetime import datetime as D
P = []
def add(*a): P.append(a)

add('Einstein', 'A', D(1879,3,14,11,30), 0.667, 48.40, 9.99, [
 (D(1902,6,23),'career','Patent office job'),(D(1903,1,6),'marriage','Marries Mileva'),(D(1904,5,14),'children','Son Hans Albert'),
 (D(1905,6,30),'status','Special relativity paper'),(D(1909,10,15),'career','Professor Zurich'),(D(1914,4,1),'foreign','Moves to Berlin'),
 (D(1919,6,2),'marriage','Marries Elsa'),(D(1920,2,20),'setback','Mother dies'),(D(1922,11,9),'status','Nobel prize announced'),
 (D(1933,10,17),'foreign','Arrives USA'),(D(1936,12,20),'setback','Elsa dies')])
add('SteveJobs', 'A', D(1955,2,24,19,15), -8, 37.77, -122.42, [
 (D(1976,4,1),'career','Apple founded'),(D(1978,5,17),'children','Daughter Lisa'),(D(1980,12,12),'status','Apple IPO'),
 (D(1985,9,16),'setback','Forced out of Apple'),(D(1991,3,18),'marriage','Marries Laurene'),(D(1991,9,22),'children','Son Reed'),
 (D(1997,2,7),'career','Returns to Apple (NeXT bought)'),(D(2003,10,1),'setback','Cancer diagnosis'),(D(2007,1,9),'status','iPhone launch'),(D(2011,10,5),'setback','Death')])
add('Gandhi', 'B', D(1869,10,2,7,33), 4.64, 21.64, 69.60, [
 (D(1883,5,15),'marriage','Child marriage'),(D(1885,11,15),'setback','Father dies'),(D(1888,9,4),'foreign','Sails to London'),
 (D(1893,5,24),'foreign','Arrives South Africa'),(D(1915,1,9),'status','Returns to India'),(D(1930,3,12),'status','Salt March'),
 (D(1942,8,8),'status','Quit India'),(D(1944,2,22),'setback','Kasturba dies'),(D(1947,8,15),'status','Independence'),(D(1948,1,30),'setback','Assassinated')])
add('Obama', 'A', D(1961,8,4,19,24), -10, 21.31, -157.86, [
 (D(1990,2,5),'status','Harvard Law Review president'),(D(1992,10,3),'marriage','Marries Michelle'),(D(1995,11,7),'setback','Mother dies'),
 (D(1996,11,5),'career','Elected Illinois senate'),(D(1998,7,4),'children','Malia'),(D(2001,6,10),'children','Sasha'),
 (D(2004,11,2),'status','US Senate won'),(D(2008,11,4),'status','Elected President'),(D(2012,11,6),'status','Re-elected')])
add('BillGates', 'A', D(1955,10,28,21,15), -8, 47.61, -122.33, [
 (D(1975,4,4),'career','Microsoft founded'),(D(1980,11,6),'career','IBM deal'),(D(1986,3,13),'status','Microsoft IPO'),
 (D(1994,1,1),'marriage','Marries Melinda'),(D(1994,6,10),'setback','Mother dies'),(D(1996,4,26),'children','Jennifer'),
 (D(1999,5,23),'children','Rory'),(D(2000,1,13),'career','Steps down as CEO'),(D(2002,9,14),'children','Phoebe'),(D(2021,5,3),'marriage','Divorce announced')])
add('Diana', 'A', D(1961,7,1,19,45), 1, 52.83, 0.51, [
 (D(1981,2,24),'marriage','Engagement'),(D(1981,7,29),'marriage','Wedding'),(D(1982,6,21),'children','William'),
 (D(1984,9,15),'children','Harry'),(D(1992,3,29),'setback','Father dies'),(D(1992,12,9),'marriage','Separation announced'),
 (D(1995,11,20),'status','Panorama interview'),(D(1996,8,28),'marriage','Divorce final'),(D(1997,8,31),'setback','Death')])
add('Elizabeth2', 'A', D(1926,4,21,2,40), 1, 51.5, -0.12, [
 (D(1936,12,11),'status','Father becomes king'),(D(1947,11,20),'marriage','Wedding'),(D(1948,11,14),'children','Charles'),
 (D(1950,8,15),'children','Anne'),(D(1952,2,6),'status','Becomes queen'),(D(1960,2,19),'children','Andrew'),(D(1964,3,10),'children','Edward'),
 (D(2021,4,9),'setback','Philip dies')])
add('Musk', 'A', D(1971,6,28,7,30), 2, -25.75, 28.19, [
 (D(1989,6,1),'foreign','Moves to Canada'),(D(1992,9,1),'foreign','Moves to USA (Penn)'),(D(1999,2,1),'status','Zip2 sold'),
 (D(2000,1,1),'marriage','Marries Justine'),(D(2002,5,14),'career','SpaceX founded'),(D(2002,9,4),'setback','First son dies'),
 (D(2002,10,3),'status','PayPal sold'),(D(2008,9,28),'status','Falcon 1 reaches orbit'),(D(2022,10,27),'career','Buys Twitter')])
add('IndiraGandhi', 'A', D(1917,11,19,23,11), 5.5, 25.43, 81.84, [
 (D(1942,3,26),'marriage','Marries Feroze'),(D(1944,8,20),'children','Rajiv'),(D(1946,12,14),'children','Sanjay'),
 (D(1960,9,8),'setback','Feroze dies'),(D(1964,5,27),'setback','Nehru dies'),(D(1966,1,24),'status','Becomes PM'),
 (D(1977,3,22),'setback','Loses election'),(D(1980,1,14),'status','Returns as PM'),(D(1980,6,23),'setback','Sanjay dies'),(D(1984,10,31),'setback','Assassinated')])
add('Nehru', 'A', D(1889,11,14,23,3), 5.456, 25.43, 81.84, [
 (D(1905,5,1),'foreign','Goes to Harrow, England'),(D(1912,8,1),'career','Returns as barrister'),(D(1916,2,8),'marriage','Marries Kamala'),
 (D(1917,11,19),'children','Indira born'),(D(1929,12,29),'status','Congress president'),(D(1931,2,6),'setback','Father dies'),
 (D(1936,2,28),'setback','Kamala dies'),(D(1947,8,15),'status','First PM'),(D(1964,5,27),'setback','Death')])
add('Amitabh', 'B', D(1942,10,11,16,0), 5.5, 25.43, 81.84, [
 (D(1969,11,7),'career','Film debut released'),(D(1973,5,11),'status','Zanjeer breakthrough'),(D(1973,6,3),'marriage','Marries Jaya'),
 (D(1974,3,17),'children','Shweta'),(D(1976,2,5),'children','Abhishek'),(D(1982,7,26),'setback','Coolie accident'),
 (D(1984,12,24),'status','Elected MP'),(D(2000,7,3),'career','KBC starts'),(D(2003,1,18),'setback','Father dies')])
add('Vivekananda', 'B', D(1863,1,12,6,33), 5.89, 22.57, 88.36, [
 (D(1881,11,15),'status','Meets Ramakrishna'),(D(1884,2,15),'setback','Father dies'),(D(1886,8,16),'setback','Ramakrishna dies'),
 (D(1893,5,31),'foreign','Sails for America'),(D(1893,9,11),'status','Chicago speech'),(D(1902,7,4),'setback','Death')])
add('Zuckerberg', 'A', D(1984,5,14,14,39), -4, 41.03, -73.77, [
 (D(2002,9,1),'education','Enters Harvard'),(D(2004,2,4),'career','Facebook launched'),(D(2004,6,15),'foreign','Moves to Palo Alto'),
 (D(2012,5,18),'status','IPO'),(D(2012,5,19),'marriage','Marries Priscilla'),(D(2015,11,30),'children','Max'),(D(2017,8,28),'children','August')])
add('Oprah', 'A', D(1954,1,29,4,30), -6, 33.06, -89.59, [
 (D(1984,1,2),'career','Moves to Chicago show'),(D(1985,12,18),'status','Color Purple released'),(D(1986,9,8),'status','National show begins'),
 (D(2003,3,1),'status','Becomes billionaire'),(D(2011,1,1),'career','OWN network launched'),(D(2011,5,25),'career','Ends talk show')])
add('MichaelJackson', 'A', D(1958,8,29,19,33), -5, 41.59, -87.35, [
 (D(1982,11,30),'status','Thriller released'),(D(1987,8,31),'status','Bad released'),(D(1994,5,26),'marriage','Marries Lisa Marie'),
 (D(1997,2,13),'children','Prince'),(D(1998,4,3),'children','Paris'),(D(2005,6,13),'setback','Trial verdict'),(D(2009,6,25),'setback','Death')])
add('Monroe', 'A', D(1926,6,1,9,30), -8, 34.05, -118.24, [
 (D(1942,6,19),'marriage','Marries Dougherty'),(D(1946,8,26),'career','Fox contract'),(D(1954,1,14),'marriage','Marries DiMaggio'),
 (D(1956,6,29),'marriage','Marries Miller'),(D(1962,8,4),'setback','Death')])
add('JFK', 'A', D(1917,5,29,15,0), -5, 42.33, -71.12, [
 (D(1943,8,2),'setback','PT-109 sinking'),(D(1944,8,12),'setback','Brother Joe dies'),(D(1946,11,5),'status','Elected to Congress'),
 (D(1952,11,4),'status','Elected Senator'),(D(1953,9,12),'marriage','Marries Jacqueline'),(D(1957,11,27),'children','Caroline'),
 (D(1960,11,8),'status','Elected President'),(D(1963,8,9),'setback','Son Patrick dies'),(D(1963,11,22),'setback','Assassinated')])
add('Churchill', 'A', D(1874,11,30,1,30), -0.0, 51.84, -1.36, [
 (D(1895,1,24),'setback','Father dies'),(D(1900,10,1),'status','Elected MP'),(D(1908,9,12),'marriage','Marries Clementine'),
 (D(1915,11,11),'setback','Resigns after Gallipoli'),(D(1940,5,10),'status','Becomes PM'),(D(1945,7,26),'setback','Loses election'),
 (D(1951,10,26),'status','PM again'),(D(1953,10,15),'status','Nobel literature')])
add('Tendulkar', 'B', D(1973,4,24,16,20), 5.5, 19.07, 72.88, [
 (D(1989,11,15),'career','Test debut'),(D(1995,5,24),'marriage','Marries Anjali'),(D(1997,10,12),'children','Sara'),
 (D(1999,5,19),'setback','Father dies'),(D(1999,9,24),'children','Arjun'),(D(2012,3,16),'status','100th international century'),(D(2013,11,16),'career','Retires')])
