"""Read-only failure probes; exploratory diagnostics cannot modify frozen V3."""
import json
import sys
from pathlib import Path
import numpy as np
from final_metrics import evaluate
from freeze_final_candidate import verify_freeze
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from possession.final_scenarios import make,FAMILIES,DEV_SEEDS
from possession.v2 import infer
from possession.live_dead_experiment import prepare,infer_prepared
from possession.temporal import decode
import possession_metrics as pm


def adaptive_decode(emission,config,fps=25):
    """Research-only confidence-dependent switch costs, with identical age states."""
    duration=np.maximum(1,np.rint(np.array(config['minimum_s'])*fps).astype(int))
    starts=np.r_[0,np.cumsum(duration)[:-1]];mature=np.cumsum(duration)-1
    state_of=np.repeat(np.arange(3),duration);n=len(emission)
    score=np.full(duration.sum(),-np.inf);score[starts]=emission[0]/fps
    back=np.zeros((n,duration.sum()),np.int16)
    for t in range(1,n):
        margin=abs(emission[t,0]-emission[t,1])/2
        multiplier=1.25-.5*np.clip(margin/3,0,1)
        trans=np.full((3,3),config['dead_switch']*multiplier)
        trans[:2,:2]=config['team_switch']*multiplier;np.fill_diagonal(trans,np.inf)
        new=np.full_like(score,-np.inf)
        for k in range(3):
            a,m=starts[k],mature[k];candidate=score[mature]-trans[:,k];source=int(np.argmax(candidate))
            new[a]=candidate[source];back[t,a]=mature[source]
            if m>a:new[a+1:m+1]=score[a:m];back[t,a+1:m+1]=np.arange(a,m)
            if score[m]>=new[m]:new[m]=score[m];back[t,m]=m
        score=new+emission[t,state_of]/fps
    state=int(np.argmax(score));path=np.empty(n,np.int8)
    for t in range(n-1,-1,-1):path[t]=state_of[state];state=back[t,state]
    return path


def main():
    verify_freeze();cfg=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}
    model=json.loads((ROOT/'models/ydse_live_dead.json').read_text());mechanisms=[];cost_rows=[]
    for family in ['stationary_live','stationary_dead','hidden_early','hidden_late','hidden_multiple','short_control','deflection']:
        s=make(family,31);parts=prepare(s.tracking,s.events,cfg,s.blocks)
        for mode in ['v2','blend']:
            pred,_,diag=infer_prepared(parts,len(s.truth),cfg,model,mode,return_diagnostics=True)
            labels=pm.label_codes(pred);valid=pm.valid_runs(s.truth)
            target=[(t[0]/25,int(t[1]),int(t[2])) for t in pm.transitions(s.truth,valid)]
            observed=[(t[0]/25,int(t[1]),int(t[2])) for t in pm.transitions(labels,valid)]
            emissions=np.concatenate([d['emission'] for d in diag])
            mechanisms.append(dict(family=family,mode=mode,truth_transitions=target,predicted_transitions=observed,
                centre_10_to18s_mean_emission=emissions[250:450].mean(0).tolist(),
                gap_brackets_seconds=[(a/25,b/25) for d in diag for a,b in d['gap_brackets']],
                **evaluate(s.truth,pred,np.isfinite(s.tracking.ball[:,:2]).all(axis=1))))
    # Development seeds only. These diagnostics do not select or alter the candidate.
    for family in FAMILIES:
        for seed in DEV_SEEDS:
            s=make(family,seed);parts=prepare(s.tracking,s.events,cfg,s.blocks)
            for name in ['fixed','cost_minus25','cost_plus25','shorter_minimum','confidence_adaptive']:
                labels=np.full(len(s.truth),'X',dtype='<U1')
                for c in parts:
                    e=np.c_[c['team'],-c['team'],c['dead']]
                    factor=.75 if name=='cost_minus25' else 1.25 if name=='cost_plus25' else 1.
                    mins=[.16,.16,.32] if name=='shorter_minimum' else cfg['minimum_s']
                    path=adaptive_decode(e,cfg) if name=='confidence_adaptive' else decode(e,25,mins,cfg['team_switch']*factor,cfg['dead_switch']*factor)
                    labels[c['first']:c['stop']]=np.array(['H','A','D'])[path]
                cost_rows.append(dict(family=family,seed=seed,variant=name,**evaluate(s.truth,labels)))
        print('Duration development probe:',family,flush=True)
    result=dict(mechanisms=mechanisms,duration_development=cost_rows,
        duration_summary={name:float(np.mean([r['spell_f1_mean'] for r in cost_rows if r['variant']==name])) for name in sorted({r['variant'] for r in cost_rows})},
        limitation='Exploratory post-freeze development-only diagnostics; no candidate changes or new-match tuning')
    (ROOT/'reports/final_failure_probes.json').write_text(json.dumps(result,indent=2),newline='\n')
    verify_freeze();print(json.dumps(result['duration_summary'],indent=2))


if __name__=='__main__':main()
