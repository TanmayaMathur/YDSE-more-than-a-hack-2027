"""Local-only match diagnostics. Exports raw transition rows only into private/."""
import json
import os
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from possession.data import load_tracking
from possession.official import load_tags,N_FRAMES
from possession.v2 import infer,audit_features
from possession.preprocessing import repair_ball
from possession.official import PITCH,FPS
from possession.data import Tracking
from possession.audit_diagnostics import original_diagnostics,summarize,restart_rejection_summary
import possession_metrics as pm

def main():
    data=Path(os.environ.get('MTAH_DATA_DIR',ROOT/'data'))
    tracking=load_tracking(data);events=load_tags(data_dir=str(data))
    c1=json.loads((ROOT/'configs/final.json').read_text());c2=json.loads((ROOT/'configs/audit_v2.json').read_text())
    private=ROOT/'private/accuracy_audit';private.mkdir(parents=True,exist_ok=True)
    chunks=original_diagnostics(tracking,events,c1)
    expected=pm.read_label_csv(ROOT/'submission/YDSE.csv')['label'].to_numpy()
    v1=np.full(N_FRAMES,'X')
    for c in chunks:v1[c['first']:c['first']+len(c['labels'])]=c['labels']
    assert np.array_equal(v1,expected),'Diagnostic V1 reconstruction diverged from protected release'
    labels,stats,new_chunks=infer(tracking,events,c2,return_diagnostics=True)
    expected_v2=pm.read_label_csv(ROOT/'submission/candidates/YDSE_v2.csv')['label'].to_numpy()
    assert np.array_equal(labels,expected_v2),'V2 diagnostics diverged from generated candidate'
    for chunk in new_chunks:
        a=chunk['first'];b=a+len(chunk['labels'])
        local=Tracking(tracking.players[a:b],tracking.ball[a:b],tracking.teams)
        ball,rel=repair_ball(local.ball[:,:2]*np.asarray(PITCH),[(0,b-a)],FPS,c2['max_gap_s'],c2['max_ball_speed'])
        features=audit_features(local,ball,rel,PITCH,FPS,c2['contact_gate'])
        chunk['ball_speed']=features['ball_speed'];chunk['slow']=features['slow']
    aggregate={}
    for name,parts,cfg in [('v1',chunks,c1),('v2',new_chunks,c2)]:
        rows,summary=summarize(parts,cfg)
        (private/(name+'_transitions.json')).write_text(json.dumps(rows,indent=2))
        aggregate[name]=summary
    aggregate['v2']['supported_restart_anchors']=stats['restarts_localized_by_motion']
    aggregate['v2']['hidden_turnover_brackets']=stats['hidden_turnover_brackets']
    aggregate['restart_rejection_summary']=restart_rejection_summary(events,new_chunks)
    aggregate['label_disagreements']=int(np.sum(labels!=v1))
    aggregate['warning']='Label-free model diagnostics, not accuracy or targets for fitting'
    (ROOT/'reports/accuracy_match_aggregates.json').write_text(json.dumps(aggregate,indent=2))
    print('PASS: diagnostics agree with exact V1 and V2 files; per-transition rows kept private.')
    print(json.dumps({k:{f:v for f,v in values.items() if f in ['spell_count','dead_segments','transitions','weak_instantaneous_transition_margins']}
                      for k,values in aggregate.items() if isinstance(values,dict)},indent=2))

if __name__=='__main__':main()
