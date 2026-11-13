"""YDSE hybrid inference. No labels, annotations or competitor predictions are inputs."""
import numpy as np
from .official import BLOCKS, FPS, PITCH, N_FRAMES, load_tags, KICKOFF_VIDEO_FRAMES
from .data import load_tracking
from .preprocessing import repair_ball
from .features import extract
from .tagging import evidence
from .temporal import decode
from .restarts import localize

def infer(tracking, events, config, blocks=BLOCKS, fps=FPS, pitch=PITCH):
    n = len(tracking.ball)
    ball, reliability = repair_ball(tracking.ball[:, :2] * np.asarray(pitch), blocks, fps,
                                    config['max_gap_s'], config['max_ball_speed'])
    f = extract(tracking, ball, reliability, pitch, fps, blocks)
    tag, live, restart = evidence(events, n, fps)
    restart_live, restart_quiet, restart_team, located = localize(
        events, f['ball_speed'], reliability, f['slow'], fps)
    team_signal = (config['geometry_weight'] * f['control'] + config['tag_weight'] * tag +
                   .5 * restart_team)
    # Missing ball alone has no dead-ball contribution. It needs independent slow-player evidence.
    dead = (config['dead_bias'] + 4.5 * f['outside'] * reliability +
            5.0 * f['stationary'] * f['slow'] +
            2.6 * f['missing'] * f['slow'] +
            1.1 * restart * f['slow'] - 1.3 * f['active'] -
            .7 * live - .8 * f['quality'] + .8 * restart_quiet - 2.0 * restart_live)
    emission = np.column_stack((team_signal, -team_signal, dead))
    labels = np.full(n, 'X', dtype='<U1')
    alphabet = np.array(['H', 'A', 'D'])
    for index, (a, b) in enumerate(blocks):
        local = emission[a:b].copy()
        # Only the official published pre-kickoff interval is a hard dead-ball constraint.
        if config.get('official_prekickoff', True) and blocks == BLOCKS and index == 1:
            kickoff = KICKOFF_VIDEO_FRAMES['2nd Half']
            local[:max(0, kickoff-a), :2] = -1e6
            local[:max(0, kickoff-a), 2] = 1e6
        labels[a:b] = alphabet[decode(local, fps, config['minimum_s'], config['team_switch'], config['dead_switch'])]
    stats = {'observed_or_repaired_fraction': float(np.mean(reliability > 0)),
             'restarts_localized_by_motion': located,
             'mean_control_quality': float(np.mean(f['quality'])),
             'labels': {k: int(np.sum(labels == k)) for k in 'HADX'}}
    return labels, stats

def run(data_dir, config):
    tracking = load_tracking(data_dir)
    return infer(tracking, load_tags(data_dir=str(data_dir)), config)
