"""Read-only frozen-candidate audit. Never trains, tunes or rewrites candidates."""
import csv
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'upstream'))
from possession.official import BLOCKS,N_FRAMES,FPS,PITCH,load_tags
from possession.data import load_tracking
from possession.live_dead_experiment import prepare,infer_prepared
from possession.learned_dead import predict
from freeze_final_candidate import verify_freeze
import possession_metrics as pm


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_preservation():
    manifest=json.loads((ROOT/'private/release_audit/preserved_manifest.json').read_text())
    for r in manifest['files']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
    return len(manifest['files'])


def segments(labels):
    change=np.r_[True,labels[1:]!=labels[:-1]];starts=np.flatnonzero(change)
    return [(int(a),int(b),str(labels[a])) for a,b in zip(starts,np.r_[starts[1:],len(labels)])]


def read_candidate(path):
    # Independent stdlib CSV reader, before the official validator check.
    with path.open(newline='',encoding='utf-8') as stream:
        reader=csv.DictReader(stream);assert reader.fieldnames==['frame','label']
        labels=[]
        for expected,row in enumerate(reader):
            assert row['frame']==str(expected) and row['label'] in 'HADX'
            labels.append(row['label'])
    assert len(labels)==N_FRAMES
    labels=np.array(labels);s=segments(labels)
    d=sum(k=='D' for a,b,k in s);spells=sum(k in 'HA' for a,b,k in s)
    # Second, direct sequential count independent of vectorized run extraction.
    assert d==sum(k=='D' and (i==0 or labels[i-1]!='D') for i,k in enumerate(labels))
    assert spells==sum(k in 'HA' and (i==0 or labels[i-1]!=k) for i,k in enumerate(labels))
    table=pm.read_label_csv(path);assert pm.validate_submission(table,N_FRAMES) is None
    mask=np.zeros(N_FRAMES,bool)
    for a,b in BLOCKS:mask[a:b]=True
    assert np.all(labels[~mask]=='X') and np.all(labels[110808:113742]=='D')
    return labels,dict(sha256=sha(path),frames=N_FRAMES,labels={k:int(np.sum(labels==k)) for k in 'HADX'},
        dead_segments=d,possession_spells=spells,official_validation='PASS',prekickoff_D_frames=2934)


def external_metrics():
    rows=[]
    for match in ['J03WQQ','J03WN1']:
        for condition in ['clean','burst1729','burst3253','coordinate_noise','slot_switches','combined']:
            path=ROOT/'private/final_accuracy/external'/match/f'predictions_{condition}.npz'
            with np.load(path,allow_pickle=False) as z:
                gt=z['truth'];runs=pm.valid_runs(gt);true_spells=pm.possession_spells(gt,runs)
                for model in ['v2','v3']:
                    pred=pm.label_codes(z[model]);valid=gt!=pm.X
                    tp=int(np.sum((gt==pm.D)&(pred==pm.D)));fp=int(np.sum((gt<pm.D)&(pred==pm.D)))
                    fn=int(np.sum((gt==pm.D)&(pred!=pm.D)))
                    ps=pm.possession_spells(pred,runs);fragmented=0;excess=0;interior_d=0;affected=0
                    for a,b,k in true_spells:
                        overlaps=sum(s==k and y>a and x<b for x,y,s in ps)
                        excess+=max(0,overlaps-1);fragmented+=overlaps>1
                        d_runs=[(x+a,y+a) for x,y,s in segments(np.array(['H','A','D','X'])[pred[a:b]]) if s=='D']
                        interior_d+=sum(x>a and y<b for x,y in d_runs)
                        affected+=bool(d_runs)
                    score=pm.evaluate(gt,pred)
                    rows.append(dict(match=match,condition=condition,model=model,
                        dead_precision=tp/(tp+fp) if tp+fp else None,dead_recall=tp/(tp+fn) if tp+fn else None,
                        tp_D_frames=tp,fp_D_frames=fp,fn_D_frames=fn,false_positive_D_seconds=fp/FPS,
                        dead_segments=sum(k=='D' for a,b,k in segments(np.array(['H','A','D','X'])[pred])),
                        true_HA_spells=len(true_spells),predicted_HA_spells=len(ps),fragmented_true_spells=fragmented,
                        excess_same_team_fragments=excess,interior_false_D_segments=interior_d,
                        true_spells_with_any_false_D=affected,spellF1=score['spell_f1_mean']))
    return rows


def mechanisms(v2,v3):
    config=json.loads((ROOT/'configs/audit_v3.json').read_text());model=json.loads((ROOT/'models/ydse_live_dead.json').read_text())
    tracking=load_tracking(ROOT/'data');parts=prepare(tracking,load_tags(data_dir=str(ROOT/'data')),config)
    n=len(v3)
    assert np.array_equal(v2,infer_prepared(parts,n,config,model,'v2')[0])
    assert np.array_equal(v3,infer_prepared(parts,n,config,model,'blend')[0])
    additions=(v2!='D')&(v3=='D');removals=(v2=='D')&(v3!='D')
    features=np.concatenate([c['features'] for c in parts]);names=model['feature_names']
    eligible=np.concatenate([c['available'] for c in parts]);a=np.concatenate([additions[c['first']:c['stop']] for c in parts])
    original=np.concatenate([c['dead'] for c in parts]);team=np.concatenate([c['team'] for c in parts])
    restart=np.concatenate([c['restart_delta'] for c in parts]);raw_visible=np.concatenate([c['raw_visible'] for c in parts])
    z=predict(model,features);learned=abs(team)+z+restart
    delta=np.where(eligible,.5*(learned-original),0.)
    terms=((features-np.asarray(model['mean']))/np.asarray(model['scale']))*np.asarray(model['coef'])[1:]
    v2d=[(x,y) for x,y,k in segments(v2) if k=='D'];v3d=[(x,y) for x,y,k in segments(v3) if k=='D']
    structure=dict(v3_dead_segments_without_v2_overlap=sum(not any(y>x2 and y2>x for x2,y2 in v2d) for x,y in v3d),
        v3_dead_segments_overlapping_multiple_v2_segments=sum(sum(y>x2 and y2>x for x2,y2 in v2d)>1 for x,y in v3d),
        v2_dead_segments_split_into_multiple_v3_segments=sum(sum(y>x2 and y2>x for x2,y2 in v3d)>1 for x,y in v2d))
    selected=lambda name:features[:,names.index(name)]
    result=dict(added_D_frames=int(additions.sum()),removed_D_frames=int(removals.sum()),
        raw_ball_missing_among_added=int(np.sum(a&~raw_visible)),
        raw_ball_observed_among_added=int(np.sum(a&raw_visible)),
        learned_head_available_among_added=int(np.sum(a&eligible)),
        D_energy_raised_among_added=int(np.sum(a&(delta>0))),
        D_energy_unchanged_or_lower_among_added=int(np.sum(a&(delta<=0))),
        mean_D_energy_increase_among_added=float(delta[a].mean()),
        mean_team_abs_among_added=float(abs(team[a]).mean()),
        mean_clipped_logodds_among_added=float(z[a].mean()),
        logodds_clip_positive_among_added=int(np.sum(a&(z==5))),
        logodds_clip_negative_among_added=int(np.sum(a&(z==-5))),
        slow_score_above_half_among_added=int(np.sum(a&(selected('slow')>.5))),
        stationary_score_above_half_among_added=int(np.sum(a&(selected('stationary')>.5))),
        mean_logit_feature_contributions_among_added={name:float(terms[a,i].mean()) for i,name in enumerate(names)},
        logit_intercept=float(model['coef'][0]),
        half_additions=[dict(half=i+1,added=int(additions[x:y].sum()),removed=int(removals[x:y].sum())) for i,(x,y) in enumerate(BLOCKS)],
        segment_structure=structure,
        warning='Aggregate automatic input diagnostics only; no competition human truth, no manual video inspection. Correlated standardized feature terms are descriptive, not causal attribution.')
    return result


def main():
    verify_freeze();protected=verify_preservation();candidates={};labels={}
    for name,path in [('v1','submission/YDSE.csv'),('v2','submission/candidates/YDSE_v2.csv'),('v3','submission/candidates/YDSE_v3.csv')]:
        labels[name],candidates[name]=read_candidate(ROOT/path)
    v2=labels['v2'];v3=labels['v3']
    comparison=dict(changed_frames=int(np.sum(v2!=v3)),net_D_frames=candidates['v3']['labels']['D']-candidates['v2']['labels']['D'],
        label_transition_counts={a+'->'+b:int(np.sum((v2==a)&(v3==b))) for a in 'HADX' for b in 'HADX' if a!=b},
        seconds_per_frame=1/FPS)
    result=dict(candidates=candidates,comparison=comparison,external=external_metrics(),
        mechanisms=mechanisms(v2,v3),protected_files_unchanged=protected,
        evaluation_status='Previously exposed external evaluations; reused only for fixed-output error accounting, not tuning or future holdout claims')
    verify_freeze();verify_preservation()
    out=ROOT/'private/release_audit/readiness_metrics.json';assert not out.exists(),'Never replace audit results'
    out.write_text(json.dumps(result,indent=2),newline='\n')
    print(json.dumps({'candidates':candidates,'comparison':comparison,'mechanisms':result['mechanisms']},indent=2))


if __name__=='__main__':main()
