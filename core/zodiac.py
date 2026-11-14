"""Module A1: the fixed vocabulary. Signs, natural zodiac (Kalapurusha) <-> house, reference frames. No chart maths here."""
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SIGN_LORD = ['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']  # classical 7-planet lords
def natural_sign_of_house(h):   # Kalapurusha: house 1 = Aries ... house 12 = Pisces. h in 1..12, returns sign index 0..11
    return (h - 1) % 12
def natural_house_of_sign(s):   # Aries = 1 ... Pisces = 12
    return s % 12 + 1
def house_from(frame_sign, sign):  # house number of `sign` when counting from `frame_sign` as house 1
    return (sign - frame_sign) % 12 + 1
def sign_at_house(frame_sign, h):  # inverse: which sign is house h when frame_sign is house 1
    return (frame_sign + h - 1) % 12
# Reference frames a rule may count houses from. A rule is only evaluated after its frame is resolved.
FRAMES = ('lagna', 'moon', 'sun', 'aries_fixed', 'planet:<name>', 'karaka')
def sign_of(lon): return int((lon % 360) // 30)
def deg_in_sign(lon): return (lon % 360) % 30
