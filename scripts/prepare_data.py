"""Local-only archive preparation. Never prints restricted file contents."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def safe_members(zf, limit=8 * 1024**3):
    names = set()
    total = 0
    infos = zf.infolist()
    for info in infos:
        name = info.filename.replace('\\', '/')
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or ':' in name or '\x00' in name:
            raise ValueError('Unsafe archive path')
        if any(part.endswith((' ', '.')) or re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', part, re.I) for part in p.parts):
            raise ValueError('Unsafe Windows filename')
        key = str(p).casefold()
        if key in names:
            raise ValueError('Duplicate archive member')
        names.add(key)
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ValueError('Symlink forbidden')
        total += info.file_size
        if total > limit or (info.file_size > 100_000_000 and info.file_size / max(info.compress_size, 1) > 2000):
            raise ValueError('Archive expansion limit')
    return infos

def extract_safe(archive, destination):
    destination = Path(destination).resolve()
    with zipfile.ZipFile(archive) as zf:
        infos = safe_members(zf)
        targets = [(i, destination.joinpath(*PurePosixPath(i.filename.replace('\\', '/')).parts)) for i in infos]
        for info, target in targets:
            if not target.resolve().is_relative_to(destination):
                raise ValueError('Archive escape')
            if target.exists() and not info.is_dir():
                raise FileExistsError('Refusing to overwrite extracted member')
        destination.mkdir(parents=True, exist_ok=True)
        for info, target in targets:
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, target.open('xb') as dst:
                shutil.copyfileobj(src, dst)
    return infos

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=ROOT)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    private = workspace / 'private'
    private.mkdir(exist_ok=True)
    archives = sorted(p for p in workspace.rglob('*.zip') if not any(x in p.parts for x in ('.venv', 'data_staging', 'vendor_research')))
    manifest = []
    for index, archive in enumerate(archives, 1):
        digest = sha256(archive)
        dest = workspace / 'data_staging' / f'archive_{index:03d}_{digest[:10]}'
        marker = dest / '.complete.json'
        if marker.exists():
            record = json.loads(marker.read_text())
            if record['sha256'] != digest:
                raise ValueError('Archive changed')
        else:
            infos = extract_safe(archive, dest)
            record = {'archive': str(archive), 'size': archive.stat().st_size, 'sha256': digest,
                      'uncompressed_size': sum(i.file_size for i in infos),
                      'members': [{'name': i.filename, 'size': i.file_size} for i in infos], 'destination': str(dest)}
            marker.write_text(json.dumps(record, indent=2))
        manifest.append(record)
    (private / 'archive_manifest.json').write_text(json.dumps(manifest, indent=2))
    print(f'Inspected and safely extracted {len(manifest)} archives; original files untouched.')
    print('Detailed inventories kept in private/archive_manifest.json (local only).')

if __name__ == '__main__':
    main()
