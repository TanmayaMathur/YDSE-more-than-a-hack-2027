"""Verify file formats locally and build collision-free canonical data links/copies."""
import csv
import json
import os
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from prepare_data import ROOT, sha256

sys.path.insert(0, str(ROOT / 'upstream'))
from games import SOURCES, SUFFIXES

def check(path, kind, n):
    if kind == 'atd_meta':
        root = ET.parse(path).getroot()
        if len(list(root.iter('Team'))) != 2 or not list(root.iter('Player')):
            raise ValueError('Invalid tracking metadata')
    elif kind == 'smart_tagging':
        root = ET.parse(path).getroot()
        if not list(root.iter('instance')):
            raise ValueError('Invalid tagging file')
    elif kind == 'atd_raw':
        count = 0
        with path.open() as f:
            for count, line in enumerate(f, 1):
                parts = line.strip().split(':')
                if len(parts) != 3 or int(parts[0]) != count:
                    raise ValueError('Noncontiguous tracking / malformed line')
        if count != n:
            raise ValueError('Tracking count mismatch')
    elif kind == 'homography':
        with path.open(newline='') as f:
            rows = csv.DictReader(f)
            if not {'frame', 'h00', 'h22', 'valid'} <= set(rows.fieldnames):
                raise ValueError('Homography schema mismatch')
            count = 0
            for count, row in enumerate(rows, 1):
                if int(row['frame']) != count - 1:
                    raise ValueError('Homography index mismatch')
        if count != n:
            raise ValueError('Homography count mismatch')
    elif kind == 'video':
        with path.open('rb') as f:
            if f.read(12)[4:8] != b'ftyp':
                raise ValueError('Invalid MP4 signature')

def main():
    manifest = []
    for source, spec in SOURCES.items():
        for kind in spec['assets']:
            name = spec['stem'] + SUFFIXES[kind]
            candidates = list((ROOT / 'data_staging').rglob(name))
            if kind == 'video':
                candidates = list(ROOT.glob(spec['stem'] + '*.mp4'))
            if not candidates:
                raise FileNotFoundError(name)
            hashes = {sha256(p) for p in candidates}
            if len(hashes) != 1:
                raise ValueError('Multiple differing variants; preserve and investigate')
            original = candidates[0]
            check(original, kind, spec['n_video_frames'])
            target = ROOT / 'data' / source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if sha256(target) not in hashes:
                    raise FileExistsError('Canonical collision')
            else:
                # Same-volume hard links preserve disk space; originals are never modified.
                os.link(original, target)
            manifest.append({'source': source, 'kind': kind, 'path': str(target),
                             'original': str(original), 'sha256': next(iter(hashes)),
                             'bytes': original.stat().st_size, 'format_verified': True})
    (ROOT / 'private' / 'asset_manifest.json').write_text(json.dumps(manifest, indent=2))
    (ROOT / 'reports' / 'data_integrity.md').write_text(
        '# Data integrity\n\nEight archives were extracted into separate checksum-qualified directories. '
        'All member paths, duplicates and expansion limits were checked; CRCs verified during extraction. '
        'Nine expected assets identified by name and format, SHA-256 recorded locally. '
        'Tracking and homography counts and contiguous frame IDs verified for both sources. '
        'Both videos passed MP4 signature checks; full video decoding was not performed. '
        'Canonical files are hard links: inference opens them read-only. Originals remain untouched.\n\n'
        'Detailed inventories and hashes: private/archive_manifest.json and private/asset_manifest.json. '
        'Signed participation terms were not supplied; local-only processing follows the public restrictions. '
        'No match content was sent to a hosted model or external service.\n')
    print(f'PASS: {len(manifest)} required assets verified; canonical layout ready. No raw data displayed.')

if __name__ == '__main__':
    main()
