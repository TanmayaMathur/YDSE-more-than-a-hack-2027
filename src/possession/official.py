"""Pinned public organiser helpers; never imports competition labels."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'upstream'))
from games import GAME, GAMES, asset_paths, half_video_blocks, source_frames
from baseline import team_of_each_track
from load_smart_tagging import load as load_tags, KICKOFF_VIDEO_FRAMES

FPS = GAMES[GAME]['fps']
PITCH = GAMES[GAME]['pitch']
N_FRAMES = source_frames()
BLOCKS = [(a, b + 1) for _, a, b in half_video_blocks(GAME)]
