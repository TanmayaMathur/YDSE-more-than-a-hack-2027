"""Local-only deterministic generation and official format validation."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import ctypes
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from possession.pipeline import run
from possession.official import N_FRAMES
import possession_metrics as pm

def file_hash(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(4*1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()

def peak_memory_mb():
    if os.name!='nt':
        return None
    from ctypes import wintypes
    class Memory(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[
            (name,ctypes.c_size_t) for name in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage',
            'QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
    info=Memory(); info.cb=ctypes.sizeof(info)
    process=ctypes.windll.kernel32.GetCurrentProcess
    process.restype=wintypes.HANDLE
    query=ctypes.windll.psapi.GetProcessMemoryInfo
    query.argtypes=[wintypes.HANDLE,ctypes.POINTER(Memory),wintypes.DWORD]
    if query(process(),ctypes.byref(info),info.cb):
        return info.PeakWorkingSetSize/1024**2
    return None

def write_csv(path, labels):
    if len(labels) != N_FRAMES or not set(labels) <= set('HADX'):
        raise ValueError('Invalid output labels')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as f:
        f.write('frame,label\n')
        f.writelines(f'{i},{label}\n' for i, label in enumerate(labels))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path(os.environ.get('MTAH_DATA_DIR', ROOT / 'data')))
    parser.add_argument('--config', type=Path, default=ROOT / 'configs' / 'final.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'submission' / 'YDSE.csv')
    parser.add_argument('--model',choices=['v1','v2'],default='v1')
    args = parser.parse_args()
    args.config=args.config.resolve()
    if args.model=='v2' and args.out.resolve()==(ROOT/'submission/YDSE.csv').resolve():
        raise ValueError('V2 must use a candidate path; preserved YDSE.csv may not be overwritten')
    t = time.perf_counter()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    if args.model=='v2':
        from possession.v2 import run as run_v2
        labels,stats=run_v2(args.data_dir,config)
    else:
        labels, stats = run(args.data_dir, config)
    write_csv(args.out, labels)
    table = pm.read_label_csv(args.out)
    if list(table.columns) != ['frame', 'label']:
        raise ValueError('Expected exactly two columns')
    reason = pm.validate_submission(table, N_FRAMES)
    if reason:
        raise ValueError(reason)
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
    dirty = subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, capture_output=True, text=True)
    from possession.official import asset_paths
    assets=asset_paths(data_dir=str(args.data_dir))
    input_hashes={key:file_hash(assets[key]) for key in ['atd_meta','atd_raw','smart_tagging']}
    code_files=sorted(list((ROOT/'src').rglob('*.py'))+list((ROOT/'upstream').glob('*.py'))+
                      [Path(__file__),args.config])
    code_digest=hashlib.sha256()
    for path in code_files:
        code_digest.update((str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name).replace('\\','/').encode())
        code_digest.update(path.read_bytes())
    record = dict(runtime_s=time.perf_counter()-t, python=platform.python_version(),model=args.model,
                  peak_working_set_mb=peak_memory_mb(), input_sha256=input_hashes,
                  code_and_config_sha256=code_digest.hexdigest(),
                  dependencies={p: importlib.metadata.version(p) for p in ['numpy', 'pandas']},
                  code_commit=commit.stdout.strip() if commit.returncode == 0 else 'uncommitted',
                  working_tree_dirty=bool(dirty.stdout.strip()), config=config, stats=stats,
                  output_sha256=hashlib.sha256(args.out.read_bytes()).hexdigest(), rows=len(table),
                  validation='PASS (official validator function plus exact columns)')
    private = ROOT / 'private'
    private.mkdir(exist_ok=True)
    (private / (args.out.stem + '_run.json')).write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record, indent=2))

if __name__ == '__main__':
    main()
