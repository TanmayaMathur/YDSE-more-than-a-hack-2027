"""Additional fixed-model diagnostics; no tuning, outside the preregistered suite."""
import json
import sys
import hashlib
from pathlib import Path
import numpy as np
from freeze_final_candidate import verify_freeze
from final_metrics import evaluate
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from possession.audit_scenarios import make
from possession.data import Tracking
from possession.pipeline import infer as v1
from possession.v2 import infer as v2
from possession.v3 import infer as v3
from possession.official import PITCH


def main():
    frozen=verify_freeze();rows=[]
    cfg=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}
    c1=json.loads((ROOT/'configs/final.json').read_text())|{'official_prekickoff':False}
    c3=json.loads((ROOT/'configs/audit_v3.json').read_text())|{'official_prekickoff':False}
    design={'seeds':[27011,36007,49157],
            'families':['trajectory_corruption','slot_switch','rapid_turnovers','conflicting_evidence','strong_noise_2m'],
            'role':'Additional post-freeze diagnostics, not the preregistered holdout or model selection'}
    manifest=ROOT/'research/final_accuracy/additional_stress_design.json'
    if manifest.exists():assert json.loads(manifest.read_text())==design
    else:manifest.write_text(json.dumps(design,indent=2),newline='\n')
    for family in design['families']:
        for seed in design['seeds']:
            s=make('stable_gaps' if family=='strong_noise_2m' else family,seed)
            if family=='strong_noise_2m':
                rng=np.random.default_rng(seed+420);p=s.tracking.players.copy();b=s.tracking.ball.copy()
                p[:,:,:2]+=rng.normal(0,2,p[:,:,:2].shape)/np.asarray(PITCH)
                b[:,:2]+=rng.normal(0,2,b[:,:2].shape)/np.asarray(PITCH)
                s.tracking=Tracking(p,b,s.tracking.teams)
            for name,predict,c in [('v1',v1,c1),('v2',v2,cfg),('v3',v3,c3)]:
                labels=predict(s.tracking,s.events,c,blocks=s.blocks)[0]
                rows.append(dict(family=family,seed=seed,variant=name,**evaluate(s.truth,labels)))
    result=dict(design=design,rows=rows,candidate_unchanged=verify_freeze()==frozen,
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'reports/final_adversarial.json').write_text(json.dumps(result,indent=2),newline='\n')
    print({v:{f:round(float(np.mean([r['spell_f1_mean'] for r in rows if r['variant']==v and r['family']==f])),4) for f in design['families']} for v in ['v1','v2','v3']})


if __name__=='__main__':main()
