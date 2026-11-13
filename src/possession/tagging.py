"""Saturating phase evidence with defensive polarity and uncertain restart windows."""
import numpy as np

def side(name):
    value = (name or '').strip().casefold()
    if value == 'barcelona':
        return 0
    if value in ('atletic club', 'athletic club'):
        return 1
    return None

def evidence(events, n, fps):
    offense = np.zeros((n, 2), float)
    defense = np.zeros((n, 2), float)
    restart = np.zeros(n, float)
    for event in events:
        a, b = max(0, event['start_frame']), min(n, event['end_frame'])
        if b <= a:
            continue
        code = (event['code'] or '').strip().casefold()
        tags = {k.casefold(): v for k, v in event['tags'].items() if k}
        team = side(tags.get('team'))
        if code == 'set pieces':
            # Context only. No fixed dead interval and no assumed exact restart frame.
            lo, hi = max(0, a - int(8 * fps)), b
            restart[lo:a] = np.maximum(restart[lo:a], np.linspace(0, .8, a-lo))
            restart[a:hi] = np.maximum(restart[a:hi], 1.)
            continue
        if team is None or code == 'goals':
            continue
        ramp = np.minimum(1., np.minimum(np.arange(b-a) + 1, np.arange(b-a, 0, -1)) / max(1, fps/2))
        if code.startswith('defending') or code == 'defensive transition':
            defense[a:b, 1-team] += ramp
        elif code in ('build up', 'progression', 'creating chances', 'attacking transition',
                      'long ball', 'ball in final third', 'ball in the box', 'players in the box'):
            offense[a:b, team] += ramp
    # Correlated phases and paired offensive/defensive tags must not multiply confidence.
    pooled = np.maximum(np.minimum(offense, 1.), np.minimum(defense, 1.))
    team_signal = pooled[:, 0] - pooled[:, 1]
    live = np.maximum(pooled[:, 0], pooled[:, 1])
    return team_signal, live, restart
