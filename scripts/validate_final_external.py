"""One locked evaluation of two preselected other matches; never trains models."""
import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np
from final_external_data import load,condition,ROOT
from final_metrics import evaluate
from freeze_final_candidate import verify_freeze
sys.path.insert(0,str(ROOT/'src'))
from possession.pipeline import infer as v1
from possession.live_dead_experiment import prepare,infer_prepared


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=ROOT/'reports/external_validation_expanded.json')
    args=ap.parse_args()
    frozen=verify_freeze()
    dest=args.out
    if dest.exists():raise FileExistsError('Evaluation already recorded; do not overwrite outcomes')
    plan=json.loads((ROOT/'research/final_accuracy/experiment_plan.json').read_text())
    model=json.loads((ROOT/'models/ydse_live_dead.json').read_text())
    cfg=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}
    c1=json.loads((ROOT/'configs/final.json').read_text())|{'official_prekickoff':False}
    rows=[];matches=[];started=time.perf_counter()
    for match in plan['new_evaluation_matches']:
        tracking,truth,blocks,pitch,info=load(match);matches.append(info)
        print('Loaded independent evaluation match:',match,info['title'],flush=True)
        folder=ROOT/'private/final_accuracy/external'/match
        for name in plan['evaluation_conditions']:
            tr=condition(tracking,name,pitch);parts=prepare(tr,[],cfg,blocks,pitch=pitch)
            outputs={'v1':v1(tr,[],c1,blocks,pitch=pitch)[0],
                'v2':infer_prepared(parts,len(tr.ball),cfg,model,'v2')[0],
                'v3':infer_prepared(parts,len(tr.ball),cfg,model,'blend')[0]}
            visible=np.isfinite(tr.ball[:,:2]).all(axis=1)
            np.savez_compressed(folder/f'predictions_{name}.npz',truth=truth,visible=visible,**outputs)
            for variant,labels in outputs.items():
                m=evaluate(truth,labels,visible)
                rows.append(dict(match=match,condition=name,variant=variant,
                    missing_ball_fraction=float(np.mean(~visible)),**m))
                print(match,name,variant,round(m['spell_f1_mean'],6),flush=True)
            verify_freeze()
    result=dict(matches=matches,rows=rows,seconds=time.perf_counter()-started,
        frozen_candidate=frozen,training_match='J03WOH only; not included as evaluation',
        labels='DFL BallPossession only while BallStatus=1; BallStatus=0 is D; unknown live owner is X',
        tags='No Smart Tagging is supplied for these matches; no XML tactical prior used in any model',
        warning='Two other matches and correlated perturbations; no competition score or broad generalization claim')
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8',newline='\n')
    print('Locked external evaluation complete:',dest,flush=True)


if __name__=='__main__':main()
