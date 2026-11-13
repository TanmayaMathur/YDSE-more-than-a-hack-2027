"""Collective, slot-permutation-invariant control and live/dead evidence."""
import warnings
import numpy as np
from .preprocessing import rolling, velocity

def extract(tracking, ball, reliability, pitch, fps, blocks):
    players = tracking.players[:, :, :2].astype(float) * np.asarray(pitch)
    n = len(ball)
    # Recomputed speeds avoid trusting the export's speed channel.
    pv = velocity(players, fps, 12.)
    bv = velocity(ball, fps, 45.)
    for a, _ in blocks:
        pv[a] = np.nan
        bv[a] = np.nan
    ps = np.linalg.norm(pv, axis=2)
    bs = np.linalg.norm(bv, axis=1)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        med_speed = np.nanmedian(ps, axis=1)
    med_speed = rolling(med_speed, fps * 2, 'median')
    visible = np.isfinite(players).all(axis=2)
    count = visible.sum(axis=1)
    delta = players - ball[:, None, :]
    distance = np.linalg.norm(delta, axis=2)
    distance[~np.isfinite(distance)] = np.inf
    nearest = np.full((n, 2), np.inf)
    relative = np.full((n, 2), np.nan)
    density = np.zeros((n, 2))
    approach = np.zeros((n, 2))
    row = np.arange(n)
    for team in (0, 1):
        indices = np.flatnonzero(tracking.teams == team)
        if not len(indices):
            raise ValueError('Both teams must have slots')
        dist = distance[:, indices]
        local = dist.argmin(axis=1)
        slot = indices[local]
        nearest[:, team] = dist[row, local]
        relative[:, team] = np.linalg.norm(pv[row, slot] - bv, axis=1)
        density[:, team] = (dist < 5.).sum(axis=1)
        # Positive if nearest player moves towards the ball; clipped for noisy motion.
        dot = np.sum(pv[row, slot] * (-delta[row, slot]), axis=1)
        approach[:, team] = np.nan_to_num(dot / np.maximum(nearest[:, team], .5), nan=0.)
    both = np.isfinite(nearest).all(axis=1)
    margin = np.zeros(n)
    margin[both] = np.tanh((nearest[both, 1] - nearest[both, 0]) / 2.)
    minimum = np.min(nearest, axis=1)
    proximity = np.exp(-np.maximum(minimum - 1.5, 0.) / 3.)
    # A flying ball's nearest player is weak evidence; fast receptions remain possible.
    flight = np.exp(-np.maximum(np.nan_to_num(bs, nan=8.) - 8., 0.) / 10.)
    winner = np.argmin(nearest, axis=1)
    rel = relative[row, winner]
    co_motion = .7 + .3 * np.exp(-np.nan_to_num(rel, nan=10.) / 6.)
    quality = reliability * proximity * flight * co_motion * np.minimum(count/14., 1.)
    # Small collective tie-breaks; cannot override strong direct geometric evidence.
    local_signal = .05 * np.tanh((density[:, 0] - density[:, 1]) / 2.)
    approach_signal = .05 * np.tanh((approach[:, 0] - approach[:, 1]) / 4.)
    control = quality * np.clip(margin + local_signal + approach_signal, -1., 1.)
    outside = np.isfinite(ball).all(axis=1) & ((ball[:, 0] < -.8) | (ball[:, 0] > pitch[0] + .8) |
                                                       (ball[:, 1] < -.8) | (ball[:, 1] > pitch[1] + .8))
    stationary = rolling((bs < .65).astype(float), fps * 2) * (reliability > 0)
    slow = np.clip((1.3 - np.nan_to_num(med_speed, nan=2.)) / .8, 0., 1.)
    active = np.clip((np.nan_to_num(med_speed, nan=1.4) - 1.) / 1.5, 0., 1.)
    missing_fraction = rolling((reliability == 0).astype(float), fps * 3)
    return dict(control=control, quality=quality, outside=outside.astype(float),
                stationary=stationary, slow=slow, active=active, missing=missing_fraction,
                count=count, ball_speed=bs)
