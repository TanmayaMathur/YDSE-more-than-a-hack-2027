"""Train only on the declared OTHER development match; new matches are forbidden here."""
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from final_external_data import load,condition,ROOT
sys.path.insert(0,str(ROOT/'src'))
from possession.live_dead_experiment import prepare,infer_prepared
from possession.learned_dead import fit,predict
import possession_metrics as pm

def main():
    started=time.perf_counter();folder=ROOT/'private/final_accuracy/training';folder.mkdir(parents=True,exist_ok=True)
    tr,gt,blocks,pitch,provenance=load('J03WOH')
    assert provenance['match_id']=='J03WOH'
    config=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}
    sets={};xs=[];ys=[]
    for name in ['clean','burst1729','coordinate_noise']:
        obs=condition(tr,name,pitch);parts=prepare(obs,[],config,blocks,pitch=pitch)
        sets[name]=parts;first=parts[0];a,b=blocks[0];idx=np.arange(0,b-a,5)
        valid=gt[a:b][idx]!=pm.X;idx=idx[valid]
        xs.append(first['features'][idx]);ys.append((gt[a:b][idx]==pm.D).astype(float))
        print('Prepared external development condition:',name,flush=True)
    x=np.concatenate(xs);y=np.concatenate(ys)
    model=fit(x,y,l2=.05)
    model.update(training_match='J03WOH',training_section='firstHalf only',label_source='external DFL BallStatus',
        source='https://doi.org/10.6084/m9.figshare.28196177.v1',licence='CC BY 4.0',
        attribution='Bassek, Rein, Weber and Memmert (2025)',no_competition_training=True)
    (folder/'first_half_model.json').write_text(json.dumps(model,indent=2))
    results=[]
    for condition_name,parts in sets.items():
        # Second-half validation is development only, not an independent match.
        reference=gt.copy();reference[:blocks[1][0]]=pm.X
        for mode in ['v2','learned','blend']:
            labels,_=infer_prepared(parts,len(gt),config,model,mode=mode)
            r=pm.evaluate(reference,pm.label_codes(labels))
            row=dict(condition=condition_name,mode=mode,spellF1=r['spell_f1_mean'],macroF1=r['macro_f1'],
                alive_dead_f1=r['alive_dead_f1'],pred_spells=r['n_pred_spells'],reference_spells=r['n_gt_spells'])
            results.append(row);print(json.dumps(row),flush=True)
    report=dict(training=provenance,training_frames=model['training_frames'],
        validation='Second half of development match; correlated within-match development, not holdout',
        parameters='Fixed l2=.05; 18 features; 1-in-5 training frames; clean/burst/noise views',
        results=results,seconds=time.perf_counter()-started,
        warning='No new evaluation match labels or competition labels consumed')
    (ROOT/'reports/live_dead_development.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':main()
