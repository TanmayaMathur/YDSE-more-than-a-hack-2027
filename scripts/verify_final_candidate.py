"""Two complete V3 runs, official validation, and all V1/V2 preservation checks."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from verify_release import execute,ROOT
from freeze_final_candidate import verify_freeze
sys.path.insert(0,str(ROOT/'src'))
from possession.official import BLOCKS,N_FRAMES,KICKOFF_VIDEO_FRAMES
import possession_metrics as pm


def preserved():
    manifest=json.loads((ROOT/'private/final_accuracy/preserved/manifest.json').read_text())
    for record in manifest['files']:
        assert hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()==record['sha256'],record['path']
    return len(manifest['files'])


def main():
    frozen=verify_freeze();count=preserved()
    paths=['submission/candidates/YDSE_v3.csv','submission/candidates/YDSE_v3_reproduced.csv']
    runs=[];commands=[]
    for path in paths:
        commands.append(execute(['scripts/generate_submission.py','--model','v3','--config','configs/audit_v3.json','--out',path]))
        runs.append(json.loads((ROOT/'private'/(Path(path).stem+'_run.json')).read_text()))
        commands.append(execute(['upstream/validate_submission.py',path]))
        commands.append(execute(['scripts/validate_output.py',path]))
        table=pm.read_label_csv(ROOT/path)
        assert len(table)==N_FRAMES and np.array_equal(table['frame'].to_numpy(),np.arange(N_FRAMES))
        labels=pm.label_codes(table);mask=np.zeros(N_FRAMES,bool)
        for a,b in BLOCKS:mask[a:b]=True
        assert np.all(labels[~mask]==pm.X)
        assert np.all(labels[BLOCKS[1][0]:KICKOFF_VIDEO_FRAMES['2nd Half']]==pm.D)
    hashes=[hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths]
    assert hashes[0]==hashes[1]
    for key in ['input_sha256','code_and_config_sha256','learned_model_sha256']:
        assert runs[0][key]==runs[1][key],key
    assert preserved()==count;verify_freeze()
    result=dict(status='PASS',outputs=paths,sha256=hashes[0],runs=runs,commands=commands,
        preservation=f'All {count} protected V1/V2 artifacts unchanged',frozen_candidate=frozen,
        prekickoff='2934 required D frames verified',ungraded='Exactly published halves; X outside',
        promotion='Separate candidate only; no publication, submission or promotion')
    dest=ROOT/'private/final_accuracy/candidate_verification.json'
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('PASS: two V3 full runs officially validated, identical bytes, V1/V2 preserved.')
    print('Candidate SHA-256:',hashes[0]);print('Runtime seconds:',[round(r['runtime_s'],2) for r in runs])


if __name__=='__main__':main()
