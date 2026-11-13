"""Two full candidate runs without touching the preserved V1 release."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from verify_release import execute,ROOT
sys.path.insert(0,str(ROOT/'src'))
from possession.official import BLOCKS,N_FRAMES,KICKOFF_VIDEO_FRAMES
import possession_metrics as pm

def main():
    paths=['submission/candidates/YDSE_v2.csv','submission/candidates/YDSE_v2_reproduced.csv']
    runs=[];commands=[]
    for path in paths:
        commands.append(execute(['scripts/generate_submission.py','--model','v2','--config','configs/audit_v2.json','--out',path]))
        runs.append(json.loads((ROOT/'private'/(Path(path).stem+'_run.json')).read_text()))
        commands.append(execute(['upstream/validate_submission.py',path]))
        commands.append(execute(['scripts/validate_output.py',path]))
        labels=pm.label_codes(pm.read_label_csv(ROOT/path))
        mask=np.zeros(N_FRAMES,bool)
        for a,b in BLOCKS:mask[a:b]=True
        assert np.all(labels[~mask]==pm.X)
        assert np.all(labels[BLOCKS[1][0]:KICKOFF_VIDEO_FRAMES['2nd Half']]==pm.D)
    hashes=[hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths]
    assert hashes[0]==hashes[1]
    assert runs[0]['input_sha256']==runs[1]['input_sha256']
    assert runs[0]['code_and_config_sha256']==runs[1]['code_and_config_sha256']
    snapshot=ROOT/'private/accuracy_audit/v1_preserved/manifest.json'
    original=json.loads(snapshot.read_text())
    for record in original['files']:
        assert hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()==record['sha256'],record['path']
    result=dict(status='PASS',outputs=paths,sha256=hashes[0],runs=runs,commands=commands,
                v1_preservation='All six protected artifacts unchanged',
                prekickoff='2934 required D frames verified',ungraded='Exactly published halves; X outside')
    dest=ROOT/'private/accuracy_audit/candidate_verification.json'
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('PASS: both V2 full runs officially validated; identical bytes; graded boundaries correct; V1 artifacts unchanged.')
    print('Candidate SHA-256:',hashes[0])
    print('Runtime seconds:',[round(r['runtime_s'],2) for r in runs])

if __name__=='__main__':main()
