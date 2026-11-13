"""Frozen-family diagnostics and ablations; never opens competition assets or labels."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from possession.audit_scenarios import make,FAMILIES,DEV_SEEDS,HOLDOUT_SEEDS
from possession.pipeline import infer as v1
from possession.v2 import infer as v2
import possession_metrics as pm

def variants(base):
    return {
        'v1':None,'v2':base,
        'reliability_only':base|{'contact_gate':False,'fix_semantics':False,'gap_bridge':False},
        'no_tags':base|{'use_tags':False,'use_restarts':False},
        'no_restarts':base|{'use_restarts':False},
        'no_gap_bridge':base|{'gap_bridge':False},
        'experimental_contact_gate':base|{'contact_gate':True},
        'old_semantics':base|{'fix_semantics':False},
        'conservative_dead':base|{'conservative_dead':True},
        'cost_minus25':base|{'team_switch':base['team_switch']*.75,'dead_switch':base['dead_switch']*.75},
        'cost_plus25':base|{'team_switch':base['team_switch']*1.25,'dead_switch':base['dead_switch']*1.25}}

def metric(gt,pred):
    r=pm.evaluate(gt,pred)
    spells=r['spell_f1'][.5]
    valid=gt!=pm.X;live=valid&(gt<pm.D);dead=gt==pm.D
    transitions=pm.transitions(pred,pm.valid_runs(gt))
    return dict(spellF1=r['spell_f1_mean'],macroF1=r['macro_f1'],
        false_dead_fraction=float(np.mean(pred[live]==pm.D)) if live.any() else None,
        missed_dead_fraction=float(np.mean(pred[dead]!=pm.D)) if dead.any() else None,
        missed_spells=spells['n_missed'],spurious_spells=spells['n_spurious'],
        predicted_transitions=[{'frame':int(f),'from':int(a),'to':int(b)} for f,a,b in transitions],
        failure_types=[name for name,condition in [('false_dead',np.any((pred==pm.D)&live)),
            ('missed_dead',np.any((pred!=pm.D)&dead)),('false_or_fragmented_spell',spells['n_spurious']>0),
            ('missed_or_merged_spell',spells['n_missed']>0)] if condition])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split',choices=['development','holdout'],required=True)
    args=parser.parse_args()
    folder=ROOT/'research/accuracy_audit';folder.mkdir(parents=True,exist_ok=True)
    design=ROOT/'src/possession/audit_scenarios.py'
    freeze=folder/'design_freeze.json'
    digest=hashlib.sha256(design.read_bytes()).hexdigest()
    if not freeze.exists():
        if args.split!='development':raise ValueError('Freeze development design before holdout')
        freeze.write_text(json.dumps({'scenario_sha256':digest,'development_seeds':DEV_SEEDS,
            'holdout_seeds':HOLDOUT_SEEDS,'families':FAMILIES,'frozen_utc':datetime.now(timezone.utc).isoformat()},indent=2))
    elif json.loads(freeze.read_text())['scenario_sha256']!=digest:
        raise ValueError('Scenario design changed after freeze; disclose a new suite instead')
    c1=json.loads((ROOT/'configs/final.json').read_text())|{'official_prekickoff':False}
    c2=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}
    source_digest=hashlib.sha256((ROOT/'src/possession/v2.py').read_bytes()+(ROOT/'configs/audit_v2.json').read_bytes()).hexdigest()
    holdout=folder/'holdout_candidate_freeze.json'
    if args.split=='holdout':
        if holdout.exists():
            if json.loads(holdout.read_text())['candidate_sha256']!=source_digest:
                raise ValueError('Candidate changed after holdout exposure; cannot reuse as unseen holdout')
        else:
            holdout.write_text(json.dumps({'candidate_sha256':source_digest,'frozen_utc':datetime.now(timezone.utc).isoformat()},indent=2))
    rows=[];start=time.perf_counter()
    seeds=DEV_SEEDS if args.split=='development' else HOLDOUT_SEEDS
    for family in FAMILIES:
        for seed in seeds:
            scenario=make(family,seed)
            for name,cfg in variants(c2).items():
                labels,_=(v1(scenario.tracking,scenario.events,c1,scenario.blocks) if name=='v1'
                          else v2(scenario.tracking,scenario.events,cfg,scenario.blocks))
                row=metric(scenario.truth,pm.label_codes(labels))
                rows.append(dict(family=family,seed=seed,variant=name,**row))
        print(f'{args.split}: completed {family}',flush=True)
    names=list(variants(c2));summary={}
    for name in names:
        subset=[r for r in rows if r['variant']==name]
        summary[name]={'mean_spellF1':float(np.mean([r['spellF1'] for r in subset])),
                       'mean_macroF1':float(np.mean([r['macroF1'] for r in subset])),
                       'family_spellF1':{f:float(np.mean([r['spellF1'] for r in subset if r['family']==f])) for f in FAMILIES}}
    result={'split':args.split,'scenario_sha256':digest,'candidate_sha256':source_digest,
        'warning':'Procedural mechanism diagnostics; not an unbiased real-match or leaderboard estimate',
        'cases':len(FAMILIES)*len(seeds),'seconds':time.perf_counter()-start,'summary':summary,'rows':rows}
    (ROOT/f'reports/accuracy_stress_{args.split}.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({'split':args.split,'cases':result['cases'],'seconds':result['seconds'],
                      'mean_spellF1':{k:v['mean_spellF1'] for k,v in summary.items()}},indent=2))

if __name__=='__main__':main()
