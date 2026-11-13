"""Final synthetic development/holdout; reads no competition or external match labels."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from final_metrics import evaluate
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from possession.final_scenarios import make,FAMILIES,DEV_SEEDS,HOLDOUT_SEEDS
from possession.pipeline import infer as v1
from possession.v2 import infer as v2
from possession.live_dead_experiment import prepare,infer_prepared

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--split',choices=['development','holdout'],required=True)
    ap.add_argument('--model',type=Path,default=ROOT/'private/final_accuracy/training/first_half_model.json')
    args=ap.parse_args();model=json.loads(args.model.read_text())
    if args.split=='holdout':
        from freeze_final_candidate import verify_freeze,text_hash
        frozen=verify_freeze()
        assert text_hash(args.model)==frozen['files']['models/ydse_live_dead.json']
    cfg=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}
    c1=json.loads((ROOT/'configs/final.json').read_text())|{'official_prekickoff':False}
    design=ROOT/'src/possession/final_scenarios.py';freeze=ROOT/'research/final_accuracy/scenario_freeze.json'
    sha=hashlib.sha256(design.read_text(encoding='utf-8').encode()).hexdigest()
    if freeze.exists():assert json.loads(freeze.read_text())['scenario_sha256']==sha
    else:freeze.write_text(json.dumps({'scenario_sha256':sha,'development_seeds':DEV_SEEDS,'holdout_seeds':HOLDOUT_SEEDS},indent=2))
    rows=[]
    for family in FAMILIES:
        for seed in DEV_SEEDS if args.split=='development' else HOLDOUT_SEEDS:
            s=make(family,seed);parts=prepare(s.tracking,s.events,cfg,s.blocks)
            variants={
                'v1':v1(s.tracking,s.events,c1,s.blocks)[0],
                'v2':v2(s.tracking,s.events,cfg,s.blocks)[0],
                'no_tags':v2(s.tracking,s.events,cfg|{'use_tags':False,'use_restarts':False},s.blocks)[0],
                'no_restarts':v2(s.tracking,s.events,cfg|{'use_restarts':False},s.blocks)[0],
                'no_bridge':v2(s.tracking,s.events,cfg|{'gap_bridge':False},s.blocks)[0],
                'dead_cap':v2(s.tracking,s.events,cfg|{'conservative_dead':True},s.blocks)[0],
                'learned_dead':infer_prepared(parts,len(s.truth),cfg,model,'learned')[0],
                'blend_dead':infer_prepared(parts,len(s.truth),cfg,model,'blend')[0]}
            for name,labels in variants.items():
                m=evaluate(s.truth,labels,np.isfinite(s.tracking.ball[:,:2]).all(axis=1))
                rows.append(dict(family=family,seed=seed,variant=name,**m))
        print(f'{args.split}: completed {family}',flush=True)
    names=sorted({r['variant'] for r in rows});summary={}
    for name in names:
        summary[name]=dict(mean_spellF1=float(np.mean([r['spell_f1_mean'] for r in rows if r['variant']==name])),
            families={f:float(np.mean([r['spell_f1_mean'] for r in rows if r['variant']==name and r['family']==f])) for f in FAMILIES})
    result=dict(split=args.split,cases=len(rows)//len(names),variants=len(names),summary=summary,rows=rows,
        scenario_sha256=sha,model_sha256=hashlib.sha256(args.model.read_bytes()).hexdigest(),
        warning='Artificial mechanism diagnostics; not real match frequencies or competition accuracy')
    (ROOT/f'reports/final_stress_{args.split}.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({'split':args.split,'cases':result['cases'],'mean_spellF1':{k:v['mean_spellF1'] for k,v in summary.items()}},indent=2))

if __name__=='__main__':main()
