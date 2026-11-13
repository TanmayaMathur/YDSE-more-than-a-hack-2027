"""Run the full match twice, validate exact outputs, and prove byte reproducibility."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]

def execute(args):
    started=time.perf_counter()
    process=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if process.returncode:
        raise RuntimeError(process.stderr or process.stdout)
    return dict(command=[sys.executable,*args],seconds=time.perf_counter()-started,
                exit_code=process.returncode,stdout=process.stdout)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--team',default='YDSE')
    args=parser.parse_args()
    if not args.team or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.team):
        raise ValueError('Use a filename-safe team name')
    folder=ROOT/'private'; folder.mkdir(exist_ok=True)
    logs=[]
    outputs=[f'submission/{args.team}.csv',f'submission/{args.team}_reproduced.csv']
    runs=[]
    for path in outputs:
        logs.append(execute(['scripts/generate_submission.py','--out',path]))
        runs.append(json.loads((folder/(Path(path).stem+'_run.json')).read_text()))
        logs.append(execute(['upstream/validate_submission.py',path]))
        logs.append(execute(['scripts/validate_output.py',path]))
    digests=[hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in outputs]
    if digests[0]!=digests[1] or runs[0]['input_sha256']!=runs[1]['input_sha256'] or runs[0]['code_and_config_sha256']!=runs[1]['code_and_config_sha256']:
        raise RuntimeError('Non-reproducible inputs, code or output')
    report=dict(status='PASS',outputs=outputs,sha256=digests[0],runs=runs,commands=logs)
    (folder/'release_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('PASS: two independent full parses/inference runs; both exact CSVs officially validated; SHA-256 identical.')
    print(f'SHA-256: {digests[0]}')
    print('Full reproduction metadata remains local in private/release_verification.json.')

if __name__=='__main__':
    main()
