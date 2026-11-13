"""Inspect Git's index for restricted assets before any publication."""
import hashlib
import json
import re
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]

def main():
    result=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True)
    if result.returncode:
        raise SystemExit('Initialize and stage the intended public files first.')
    files=[name for name in result.stdout.decode('utf-8').split('\0') if name]
    if not files:
        raise SystemExit('FAIL: no tracked files; stage the intended public source before checking.')
    allowed_csv={'research/competitor_inventory.csv'}
    forbidden_roots={'data','data_staging','private','official','vendor_research','.venv'}
    problems=[]; manifest=[]
    for name in files:
        path=ROOT/name; suffix=path.suffix.lower()
        if name.split('/')[0] in forbidden_roots:
            problems.append(name+': private directory')
        if suffix in {'.mp4','.zip','.npy','.npz','.pkl','.joblib','.pt','.pth','.xml'}:
            problems.append(name+': data/model/archive file')
        if suffix=='.csv' and name not in allowed_csv:
            problems.append(name+': frame-level CSV is not public source')
        if path.stat().st_size>2_000_000:
            problems.append(name+': unexpectedly large source file')
        if suffix=='.csv' and name in allowed_csv:
            if not path.read_text(encoding='utf-8').startswith('repository,url,'):
                problems.append(name+': unexpected inventory schema')
        if suffix in {'.py','.md','.json','.txt','.toml','.csv'}:
            text=path.read_text(encoding='utf-8-sig')
            if re.search(r'(?m)^-----BEGIN (?:OPENSSH )?PRIVATE KEY-----\s*$',text):
                problems.append(name+': possible private key')
        manifest.append({'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    local=ROOT/'private';local.mkdir(exist_ok=True)
    (local/'public_source_manifest.json').write_text(json.dumps(manifest,indent=2))
    if problems:
        raise SystemExit('\n'.join(problems))
    print(f'PASS: {len(files)} tracked source/report files; no restricted assets, predictions, model blobs or large data files.')
    print('Review the actual staged list as well; automated hygiene is not a licence review.')

if __name__=='__main__':
    main()
