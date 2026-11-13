"""Freeze the small LIVE/DEAD model using development match J03WOH only."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
import numpy as np
from final_external_data import load,condition,ROOT
sys.path.insert(0,str(ROOT/'src'))
from possession.live_dead_experiment import prepare
from possession.learned_dead import fit

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=ROOT/'models/ydse_live_dead.json')
    ap.add_argument('--report',type=Path,default=ROOT/'reports/final_model_training.json')
    args=ap.parse_args()
    start=time.perf_counter();tr,gt,blocks,pitch,info=load('J03WOH')
    assert info['match_id']=='J03WOH'
    config=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}
    x=[];y=[]
    for name in ['clean','burst1729','coordinate_noise']:
        parts=prepare(condition(tr,name,pitch),[],config,blocks,pitch=pitch)
        for part in parts:
            a,b=part['first'],part['stop'];idx=np.arange(0,b-a,5);idx=idx[gt[a:b][idx]!=3]
            x.append(part['features'][idx]);y.append((gt[a:b][idx]==2).astype(float))
        print('Prepared final external training view:',name,flush=True)
    x=np.concatenate(x);y=np.concatenate(y)
    first=fit(x,y,l2=.05);second=fit(x,y,l2=.05)
    assert first==second,'Training is not deterministic'
    first.update(training_matches=['J03WOH'],training_sections=['firstHalf','secondHalf'],
        training_views=['clean','burst1729','coordinate_noise'],label_source='External DFL BallStatus only',
        source='https://doi.org/10.6084/m9.figshare.28196177.v1',licence='CC BY 4.0',
        attribution='Bassek, Rein, Weber and Memmert (2025)',no_competition_training=True,
        no_new_evaluation_match_training=True,selected_mode='50 percent learned/heuristic dead-energy blend')
    dest=args.out;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():raise FileExistsError('Frozen trained model exists; do not overwrite')
    dest.write_text(json.dumps(first,indent=2),encoding='utf-8',newline='\n')
    result=dict(training=info,training_frames=len(y),l2=.05,deterministic_fit='Two fits exactly equal',
                model_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),seconds=time.perf_counter()-start,
                warning='Development match explicitly used for training; not an untouched evaluation match')
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
