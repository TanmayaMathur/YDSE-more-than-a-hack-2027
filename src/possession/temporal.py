"""Exact duration-constrained Viterbi with expanded H/A/D age states."""
import numpy as np

def decode(emission, fps=25, minimum_s=(.32, .32, .64), team_switch=1.1, dead_switch=.7):
    emission = np.asarray(emission, float)
    if emission.ndim != 2 or emission.shape[1] != 3 or not np.isfinite(emission).all():
        raise ValueError('Expected finite N x 3 evidence')
    n = len(emission)
    if not n:
        return np.empty(0, np.int8)
    duration = np.maximum(1, np.rint(np.array(minimum_s) * fps).astype(int))
    starts = np.r_[0, np.cumsum(duration)[:-1]]
    mature = np.cumsum(duration) - 1
    state_of = np.repeat(np.arange(3), duration)
    score = np.full(duration.sum(), -np.inf)
    score[starts] = emission[0] / fps
    back = np.zeros((n, duration.sum()), np.int16)
    trans = np.full((3, 3), dead_switch)
    trans[:2, :2] = team_switch
    np.fill_diagonal(trans, np.inf)
    for t in range(1, n):
        new = np.full_like(score, -np.inf)
        for k in range(3):
            a, m = starts[k], mature[k]
            candidates = score[mature] - trans[:, k]
            source = int(np.argmax(candidates))
            new[a] = candidates[source]
            back[t, a] = mature[source]
            if m > a:
                new[a+1:m+1] = score[a:m]
                back[t, a+1:m+1] = np.arange(a, m)
            # Ties stay in the mature state, preserving previous possession across gaps.
            if score[m] >= new[m]:
                new[m] = score[m]
                back[t, m] = m
        score = new + emission[t, state_of] / fps
    # A half ending can truncate a run; internal segments meet the minimum durations.
    state = int(np.argmax(score))
    path = np.empty(n, np.int8)
    for t in range(n-1, -1, -1):
        path[t] = state_of[state]
        state = back[t, state]
    return path
