"""Bounded trajectory repair and time-dependent observation reliability."""
import numpy as np
import pandas as pd

def runs(mask):
    d = np.diff(np.r_[False, np.asarray(mask, bool), False].astype(np.int8))
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))

def rolling(values, frames, kind='mean'):
    series = pd.Series(np.asarray(values, float))
    obj = series.rolling(max(1, int(frames) | 1), center=True, min_periods=1)
    return getattr(obj, kind)().to_numpy()

def repair_ball(ball_m, blocks, fps, max_gap_s=.8, max_speed=45.):
    xy = np.asarray(ball_m, float).copy()
    reliability = np.isfinite(xy).all(axis=1).astype(float)
    # Reject isolated spikes only when the two surrounding samples agree physically.
    for start, stop in blocks:
        if stop - start < 3:
            continue
        prev, mid, nxt = xy[start:stop-2], xy[start+1:stop-1], xy[start+2:stop]
        bad = ((np.linalg.norm(mid - prev, axis=1) * fps > max_speed) &
               (np.linalg.norm(nxt - mid, axis=1) * fps > max_speed) &
               (np.linalg.norm(nxt - prev, axis=1) * fps / 2 < max_speed))
        indices = np.flatnonzero(bad) + start + 1
        xy[indices] = np.nan
        reliability[indices] = 0
        for a0, b0 in runs(~np.isfinite(xy[start:stop]).all(axis=1)):
            a, b = start + a0, start + b0
            if a <= start or b >= stop or b - a > int(max_gap_s * fps):
                continue
            duration = (b - a + 1) / fps
            distance = np.linalg.norm(xy[b] - xy[a - 1])
            if distance / duration > max_speed:
                continue
            alpha = np.arange(1, b - a + 1) / (b - a + 1)
            xy[a:b] = xy[a-1] + alpha[:, None] * (xy[b] - xy[a-1])
            # Never assign interpolated positions the same reliability as observations.
            reliability[a:b] = .65 * np.exp(-duration / max_gap_s)
    return xy, reliability

def velocity(xy, fps, max_speed):
    vel = np.full_like(xy, np.nan, dtype=float)
    vel[1:] = np.diff(xy, axis=0) * fps
    vel[np.linalg.norm(vel, axis=-1) > max_speed] = np.nan
    return vel
