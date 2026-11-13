"""Frozen V1/V2 evaluation on one independently licensed OTHER match.

BallStatus/BallPossession are isolated evaluation targets, never model features.
No event/phase annotations are passed to inference and no weights are adjusted.
"""
import hashlib
import json
from pathlib import Path
import sys
import time
import xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from possession.data import Tracking
from possession.pipeline import infer as v1
from possession.v2 import infer as v2
import possession_metrics as pm

def paired_spell_interval(truth,predictions,draws=1000):
    """Exploratory paired possession bootstrap, with prediction counts fixed.

    This follows the scorer's spell-resampling mechanism. It is not a multi-match
    confidence interval and does not correct provider/domain or annotation bias.
    """
    runs=pm.valid_runs(truth);gt=pm.possession_spells(truth,runs);n=len(gt)
    if not n:return None
    rng=np.random.default_rng(20261114);picks=rng.integers(0,n,size=(draws,n))
    scores={}
    for name,pred in predictions.items():
        spells=pm.possession_spells(pm.fill_abstentions(pred,runs),runs)
        overlap=pm.spell_overlaps(gt,spells)
        flags=np.stack([pm.matched_gt_flags(overlap,n,iou) for iou in pm.SPELL_IOUS])
        tp=flags[:,picks].sum(axis=2);fp=np.maximum(0,len(spells)-tp);fn=n-tp
        scores[name]=np.mean(2*tp/np.maximum(1,2*tp+fp+fn),axis=0)
    low,high=np.percentile(scores['v2']-scores['v1'],[2.5,97.5])
    return dict(delta_v2_minus_v1_low95=float(low),delta_v2_minus_v1_high95=float(high),
                draws=draws,seed=20261114,method='Paired GT-spell resampling, fixed prediction counts; exploratory single-match interval')

def stream(path):
    current=None
    for event,node in ET.iterparse(path,events=('start','end')):
        if event=='start' and node.tag=='FrameSet':current=dict(node.attrib)
        elif event=='end' and node.tag=='Frame':
            yield current,dict(node.attrib)
            node.clear()
        elif event=='end' and node.tag=='FrameSet':node.clear()

def parse(folder):
    meta=next(folder.glob('*matchinformation*.xml'));raw=next(folder.glob('*positions_raw_observed*.xml'))
    root=ET.parse(meta).getroot();general=next(root.iter('General'))
    assert general.get('MatchId')=='DFL-MAT-J03WOH'
    assert general.get('Season')=='2022/2023'
    team_ids=[general.get('HomeTeamId'),general.get('GuestTeamId')]
    slots=[];teams=[]
    for team in root.iter('Team'):
        if team.get('TeamId') not in team_ids:continue
        for player in team.iter('Player'):
            slots.append(player.get('PersonId'));teams.append(team_ids.index(team.get('TeamId')))
    spans={};ball_schema=None;pitch=None
    for event,node in ET.iterparse(raw,events=('start','end')):
        if event=='start' and node.tag=='PitchSize':pitch=(float(node.get('X')),float(node.get('Y')))
        if event=='start' and node.tag=='FrameSet':current=dict(node.attrib)
        elif event=='end' and node.tag=='Frame':
            section=current['GameSection'];number=int(node.get('N'))
            if section not in ('firstHalf','secondHalf'):node.clear();continue
            old=spans.get(section,[number,number]);spans[section]=[min(old[0],number),max(old[1],number)]
            if current.get('TeamId') not in team_ids and 'BallStatus' in node.attrib:
                ball_schema=sorted(node.attrib)
            node.clear()
        elif event=='end' and node.tag=='FrameSet':node.clear()
    if pitch is None or ball_schema is None:raise ValueError('Unverified pitch or ball label schema')
    offsets={};blocks=[];n=0
    for section in ('firstHalf','secondHalf'):
        first,last=spans[section];offsets[section]=(n-first,n)
        blocks.append((n,n+last-first+1));n+=last-first+1
    players=np.full((n,len(slots),3),np.nan,np.float32);ball=np.full((n,3),np.nan,np.float32)
    labels=np.full(n,pm.X,np.int8);slot_index={s:i for i,s in enumerate(slots)}
    label_values=set();ball_count=0
    for series,frame in stream(raw):
        section=series['GameSection']
        if section not in offsets:continue
        row=int(frame['N'])+offsets[section][0]
        x=float(frame.get('X','nan'));y=float(frame.get('Y','nan'))
        pid=series.get('PersonId');teamid=series.get('TeamId')
        if teamid in team_ids and pid in slot_index:
            players[row,slot_index[pid],:2]=[(x+pitch[0]/2)/pitch[0],(y+pitch[1]/2)/pitch[1]]
        elif 'BallStatus' in frame:
            ball_count+=1
            ball[row,:2]=[(x+pitch[0]/2)/pitch[0],(y+pitch[1]/2)/pitch[1]]
            status=frame['BallStatus'];owner=frame.get('BallPossession','')
            label_values.add((status,owner))
            # DFL coding is checked below against all observed values.
            if status=='0':labels[row]=pm.D
            elif status=='1' and owner in ('1','2'):labels[row]=int(owner)-1
    if not label_values or any(s not in ('0','1') or o not in ('0','1','2') for s,o in label_values):
        raise ValueError('External label coding must be verified before evaluation')
    # Metadata-clock validation: frames in the source advance by 40 ms (25 Hz).
    times=[]
    for _,frame in stream(raw):
        times.append(frame['T'])
        if len(times)==2:break
    from datetime import datetime
    step=(datetime.fromisoformat(times[1])-datetime.fromisoformat(times[0])).total_seconds()
    if abs(step-.04)>1e-6:raise ValueError('Unexpected external FPS')
    provenance=dict(match_id='J03WOH',pitch=pitch,fps=25,rows=n,players=len(slots),ball_rows=ball_count,
        source_label_codes=sorted(label_values),graded_frames=int(np.sum(labels!=pm.X)),
        target_source='BallStatus and BallPossession; never included in Tracking',
        provider_semantics_warning='DFL owner flags need not exactly match Metrica controlled-possession rules')
    return Tracking(players,ball,np.array(teams)),labels,blocks,pitch,provenance

def corrupt(tracking,seed):
    rng=np.random.default_rng(seed);n=len(tracking.ball)
    state=False;mask=np.zeros(n,bool);up=1/40;down=.41/.59*up
    for i in range(n):
        if state:state=rng.random()>=up
        else:state=rng.random()<down
        mask[i]=state
    ball=tracking.ball.copy();ball[mask,:2]=np.nan
    return Tracking(tracking.players,ball,tracking.teams),float(mask.mean())

def main():
    start=time.perf_counter();folder=ROOT/'private/accuracy_audit/external_dfl'
    tracking,truth,blocks,pitch,provenance=parse(folder)
    c1=json.loads((ROOT/'configs/final.json').read_text())|{'official_prekickoff':False}
    c2=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}
    frozen=json.loads((ROOT/'research/accuracy_audit/holdout_candidate_freeze.json').read_text())['candidate_sha256']
    digest=hashlib.sha256((ROOT/'src/possession/v2.py').read_bytes()+(ROOT/'configs/audit_v2.json').read_bytes()).hexdigest()
    assert digest==frozen,'Candidate changed after holdout freeze'
    rows=[];intervals={}
    for condition,seed in [('clean',None),('bursty_ball_missing_seed1729',1729),('bursty_ball_missing_seed3253',3253)]:
        obs,fraction=(tracking,0.) if seed is None else corrupt(tracking,seed)
        predictions={}
        for name,method,config in [('v1',v1,c1),('v2',v2,c2)]:
            t=time.perf_counter();labels,_=method(obs,[],config,blocks,fps=25,pitch=pitch)
            result=pm.evaluate(truth,pm.label_codes(labels))
            predictions[name]=pm.label_codes(labels)
            row=dict(condition=condition,model=name,injected_missing_fraction=fraction,runtime_s=time.perf_counter()-t,
                **{k:result[k] for k in ['spell_f1_mean','macro_f1','n_gt_spells','n_pred_spells','alive_dead_f1']})
            rows.append(row);print(json.dumps(row),flush=True)
        intervals[condition]=paired_spell_interval(truth,predictions)
        np.savez_compressed(folder/('predictions_'+condition+'.npz'),truth=truth,**predictions)
    report=dict(source='https://springernature.figshare.com/articles/dataset/28196177',
        doi='10.6084/m9.figshare.28196177.v1',licence='CC BY 4.0',
        attribution='Bassek, Rein, Weber and Memmert (2025), An integrated dataset of spatiotemporal and event data in elite soccer',
        plan='research/accuracy_audit/external_validation_plan.json',provenance=provenance,
        candidate_sha256=digest,results=rows,paired_intervals=intervals,total_seconds=time.perf_counter()-start,
        warning='One external match with provider-defined tracking labels; not a competition score or proof of broad generalization')
    (ROOT/'reports/external_dfl_validation.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':main()
