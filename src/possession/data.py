"""Strict, streaming ATD parsing; assets are read locally and read-only."""
from dataclasses import dataclass
import numpy as np
import xml.etree.ElementTree as ET
from .official import asset_paths, team_of_each_track, N_FRAMES

@dataclass
class Tracking:
    players: np.ndarray
    ball: np.ndarray
    teams: np.ndarray

def parse_tracking(path, n_frames, n_slots):
    players = np.full((n_frames, n_slots, 3), np.nan, np.float32)
    ball = np.full((n_frames, 3), np.nan, np.float32)
    count = 0
    with open(path, encoding='utf-8') as handle:
        for count, line in enumerate(handle, 1):
            parts = line.strip().split(':')
            if len(parts) != 3 or int(parts[0]) != count or count > n_frames:
                raise ValueError('ATD alignment/schema failure')
            try:
                p = np.array(parts[1].replace(';', ',').split(','), dtype=np.float32)
                b = np.array(parts[2].split(','), dtype=np.float32)
            except ValueError:
                raise ValueError('ATD nonnumeric field (raw content withheld)') from None
            if p.size != n_slots * 3 or b.size != 3:
                raise ValueError('ATD slot/schema failure')
            if np.isinf(p).any() or np.isinf(b).any():
                raise ValueError('Infinite ATD coordinate')
            players[count - 1] = p.reshape(n_slots, 3)
            ball[count - 1] = b
    if count != n_frames:
        raise ValueError('ATD record count failure')
    return players, ball

def load_tracking(data_dir):
    paths = asset_paths(data_dir=str(data_dir))
    meta=ET.parse(paths['atd_meta']).getroot()
    team_ids={team.get('id') for team in meta.iter('Team')}
    if len(team_ids)!=2 or any(p.get('teamId') not in team_ids for p in meta.iter('Player')):
        raise ValueError('Invalid team/slot metadata membership')
    teams = team_of_each_track(paths['atd_meta'])
    players, ball = parse_tracking(paths['atd_raw'], N_FRAMES, len(teams))
    return Tracking(players, ball, teams)
