"""Short-term guidance: one Sun-sign window (GR-S*). Candidates carry weights; user view keeps top 3 do and 3 dont."""
import datetime
import transit as TR, gochara as G
from daily import _add, _quality_items, areas, top, hm
from guidance_rules import *
def _at(dt, tz, lat, lon): return TR.transit(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0, tz, lat, lon)
def _sign(p, dt, tz, lat, lon): return _at(dt, tz, lat, lon)['sign'][p]
def ingresses(p, start, days, tz, lat, lon, step_h=6):
    """Sign-change moments of planet p, found by stepping then bisecting to the minute. Returns [(datetime, new_sign0)]."""
    out = []; t = start; end = start + datetime.timedelta(days=days); prev = _sign(p, t, tz, lat, lon)
    while t < end:
        t2 = t + datetime.timedelta(hours=step_h); s2 = _sign(p, t2, tz, lat, lon)
        if s2 != prev:
            lo, hi = t, t2
            while (hi - lo).total_seconds() > 60:
                mid = lo + (hi - lo) / 2
                if _sign(p, mid, tz, lat, lon) == prev: lo = mid
                else: hi = mid
            out.append((hi.replace(second=0, microsecond=0), s2)); prev = s2
        t = t2
    return out
def sun_window(date, tz, lat, lon):
    t0 = datetime.datetime(date.year, date.month, date.day, 12) - datetime.timedelta(days=35)
    ing = ingresses(0, t0, 75, tz, lat, lon, step_h=12); now = datetime.datetime(date.year, date.month, date.day, 12)
    s = max(x for x in ing if x[0] <= now); e = min(x for x in ing if x[0] > now)
    return s, e
def month_items(natal, date, tz, lat, lon):
    (s_dt, s_sign), (e_dt, e_sign) = sun_window(date, tz, lat, lon)
    snap = datetime.datetime(date.year, date.month, date.day, 12); tr = _at(snap, tz, lat, lon)
    gm = G.assess(natal['moon_sign0'], tr['sign'], natal['bav'], natal['sav']); items = []
    for p, scale in ((6, 4), (4, 4), (7, 3), (8, 3), (0, 3), (2, 2), (3, 1.5), (5, 1.5)):
        _quality_items(items, natal, p, gm[p], scale, 'month')
    # personal colour for the Sun-sign period (GR-C1, C2): extra candidate = lord of the Sun's new sign
    import colour as COL
    COL.colour_items(natal, date, gm, lambda k, t, w, why, r, src: _add(items, k, t, w, why, r, src), 'this month', extra=[(COL.SIGN_LORD[tr['sign'][0]], "lord of the Sun's sign")])
    # Sun moorthi at window start (GR-G8)
    sun_t = _at(s_dt, tz, lat, lon); mh = G.house_from(natal['moon_sign0'], sun_t['sign'][1]); mo = G.moorthi(mh, 0)
    if mo['moorthi'] == 'iron': _add(items, 'dont', 'Avoid big new commitments in this month; keep plans flexible.', 3, f"Sun moorthi iron (Moon {mh}th at ingress)", 'GR-G8', 'DB BK13_0035')
    # combustion (GR-G9)
    cb = G.combust(tr['lon'])
    if cb: _add(items, 'dont', 'Do not hold marriage, house-entry or new desire-driven rites this month.', 6, 'combust ' + ', '.join(c['planet'] for c in cb), 'GR-G9', 'DB BK13_0038')
    # dasha changes inside window (GR-S3)
    rows = natal['rep']['timing']['vimshottari']; ch = []
    for i, r in enumerate(rows):
        t = datetime.datetime(*[int(x) for x in r['start_local'][:3]])
        if s_dt - datetime.timedelta(days=5) <= t <= e_dt + datetime.timedelta(days=5): ch.append((t.date().isoformat(), r['maha'], r['antar']))
    if ch: _add(items, 'dont', 'Avoid irreversible big decisions close to the period-change date.', 5, f'dasha change(s) in window: {ch}', 'GR-S3', 'classical (junction caution)')
    # dasha-linked remedies and don'ts from the rules database (and Gautam transcripts), judged with the running periods (GR-S5)
    for sec, kind in (('remedies', 'do'), ('donts', 'dont')):
        for r in natal['rep'].get(sec, {}).get('items', []):
            txt = (r.get('remedy') or r.get('outcome') or '').split(';')[0].strip().rstrip('.')
            if r.get('dasha_linked') and len(txt.split()) >= 3: _add(items, kind, txt[0].upper() + txt[1:] + '.', 4 * r['fit'], 'dasha-linked rule ' + r['id'], 'GR-S5', r['source'])
    # sub-windows: fast planet ingresses inside the window
    sub = []
    for p in (3, 5, 2):
        for dt, sg in ingresses(p, s_dt, (e_dt - s_dt).days + 1, tz, lat, lon):
            if dt < e_dt:
                g = G.assess(natal['moon_sign0'], _at(dt, tz, lat, lon)['sign'], natal['bav'], natal['sav'])[p]; sub.append({'planet': PL[p], 'at': dt.isoformat(sep=' '), 'result': g['result'], 'house_from_moon': g['house_from_moon']})
                _quality_items(items, natal, p, g, 1.0, f'sub-window {PL[p]} from {dt.date()}')
    facts = {'window_start': s_dt.isoformat(sep=' '), 'window_end': e_dt.isoformat(sep=' '), 'sun_sign': SIGNS[s_sign], 'sun_moorthi': mo, 'sub_windows': sub, 'dasha_changes': ch,
             'gochara': {PL[p]: {k: v for k, v in g.items() if k in ('sign', 'house_from_moon', 'result', 'vedha_by')} for p, g in gm.items()}}
    return items, facts
