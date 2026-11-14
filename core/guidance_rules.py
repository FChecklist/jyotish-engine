"""Data tables for the guidance layers. Written from docs/GUIDANCE_RULES.md (rule ids GR-*). Code reads these; do not hide numbers elsewhere."""
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PL = {0:'Sun',1:'Moon',2:'Mars',3:'Mercury',4:'Jupiter',5:'Venus',6:'Saturn',7:'Rahu',8:'Ketu'}
NAKS = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','P.Phalguni','U.Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','P.Ashadha','U.Ashadha','Shravana','Dhanishta','Shatabhisha','P.Bhadrapada','U.Bhadrapada','Revati']
# GR-G2 (rules DB BK13_0010-0017)
FAV = {0: (3,6,10,11), 1: (1,3,6,7,10,11), 2: (3,6,11), 3: (2,4,6,8,10,11), 4: (2,5,7,9,11), 5: (1,2,3,4,5,8,9,11,12), 6: (3,6,11), 7: (3,6,11), 8: (3,6,11)}
# GR-G5 (BK13_0022-0027): favourable house -> house whose planet blocks it
_M = {3: 12, 6: 9, 11: 5}
VEDHA = {0: {3: 9, 6: 12, 10: 4, 11: 5}, 1: {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8}, 2: dict(_M), 3: {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},
         4: {2: 12, 5: 4, 7: 3, 9: 10, 11: 8}, 5: {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3}, 6: dict(_M), 7: dict(_M), 8: dict(_M)}
EXEMPT = (frozenset({0, 6}), frozenset({1, 3}))          # BK13_0028
MALEFIC = {0, 2, 6, 7, 8}; BENEFIC = {1, 3, 4, 5}        # GR-G10 (simplified)
MOORTHI = {1: 'gold', 6: 'gold', 11: 'gold', 2: 'silver', 5: 'silver', 9: 'silver', 3: 'copper', 7: 'copper', 10: 'copper', 4: 'iron', 8: 'iron', 12: 'iron'}
MOORTHI_RESULT = {'gold': ('good', 'adverse'), 'silver': ('average_to_good', 'favourable'), 'copper': ('average_to_good', 'favourable'), 'iron': ('bad', 'average')}   # (benefics, malefics) BK13_0032-0035
COMBUST_ORB = {4: 11.0, 5: 10.0}                          # GR-G9 orbs: classical, not in DB
# GR-D1
TARA = {1: ('Janma', 'mixed'), 2: ('Sampat', 'good'), 3: ('Vipat', 'bad'), 4: ('Kshema', 'good'), 5: ('Pratyak', 'bad'), 6: ('Sadhana', 'good'), 7: ('Naidhana', 'bad'), 8: ('Mitra', 'good'), 9: ('Parama Mitra', 'good')}
CHANDRA_GOOD = FAV[1]                                      # GR-D2
RIKTA = (4, 9, 14)                                         # GR-D3
BAD_YOGA = {1: 'Vishkambha', 6: 'Atiganda', 9: 'Shula', 10: 'Ganda', 13: 'Vyaghata', 15: 'Vajra', 17: 'Vyatipata', 19: 'Parigha', 27: 'Vaidhriti'}   # GR-D5
VISHTI = tuple(range(8, 58, 7))                            # GR-D6 half-tithi numbers
NAK_CLASS = {}                                             # GR-D4
for _c, _l in {'Dhruva': (4, 12, 21, 26), 'Chara': (7, 15, 22, 23, 24), 'Mridu': (5, 14, 17, 27), 'Kshipra': (1, 8, 13), 'Ugra': (2, 10, 11, 20, 25), 'Tikshna': (6, 9, 18, 19), 'Mishra': (3, 16)}.items():
    for _n in _l: NAK_CLASS[_n] = _c
NAK_ADVICE = {'Dhruva': ('do', 'Good for lasting starts: property, foundations, planting, long-term commitments.'), 'Chara': ('do', 'Good for travel, vehicles, movement and change of place.'),
              'Mridu': ('do', 'Good for art, friendships, pleasant and gentle tasks.'), 'Kshipra': ('do', 'Good for quick tasks, trade, learning and short jobs.'),
              'Ugra': ('dont', 'Avoid starting anything new; use the day only for forceful or technical work.'), 'Tikshna': ('dont', 'Avoid starting anything new; use the day only for forceful or technical work.'), 'Mishra': (None, '')}
RAHU_PART = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}   # python weekday (Mon=0) -> 1/8 part of daylight  GR-D7
WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# GR-A2 house themes: (theme, favourable wording, caution wording). Our wording: hypothesis.
AREA = {1: ('self and energy', 'Push your personal goals and look after your energy.', 'Do not overwork or overreact.'),
        2: ('money, speech and family', 'Work on earning, savings and family money talks.', 'Do not overspend, speak harshly or make money promises.'),
        3: ('effort, short travel, siblings', 'Take up effort-heavy work, short trips and outreach.', 'Avoid rash moves and quarrels with siblings.'),
        4: ('home, vehicle, mother', 'Attend to home, vehicle and mother-related matters.', 'Do not be careless with driving, vehicle or home matters.'),
        5: ('children, study, creativity', 'Focus on study, children and creative work.', 'Avoid speculation and do not pressure children.'),
        6: ('debts, health routine, rivals', 'Clear pending debts, fix your routine and handle rivals.', 'Do not take new debt or start disputes.'),
        7: ('partnership, spouse, contracts', 'Work on partnerships, spouse matters and contracts.', 'Do not argue with spouse or partners, or sign contracts in haste.'),
        8: ('sudden change, obstacles, hidden matters', 'Do research, paperwork and pending or hidden matters.', 'Avoid risky ventures and always re-check documents.'),
        9: ('luck, father, long travel', 'Seek guidance, attend to father-related matters, plan long travel.', 'Do not depend on luck and do not rush long travel.'),
        10: ('career and status', 'Make career moves and be visible at work.', 'Do not clash with seniors or quit jobs on impulse.'),
        11: ('gains and friends', 'Work on income, networking and friends.', 'Do not over-promise to friends or spend expected gains early.'),
        12: ('expenses, sleep, foreign', 'Rest, give charity and handle foreign matters.', 'Do not spend on impulse and do not cut your sleep.')}
AREA_MIN_WEIGHT = 0.15                                     # GR-A1
CAP = {'do': 3, 'dont': 3}                                 # user view: exactly 3 and 3 (Rajat 2026-11-14)
