import json
from pathlib import Path
import numpy as np
import pytest
from possession.final_scenarios import make
from possession.learned_dead import FEATURE_NAMES,fit,predict
from possession.live_dead_experiment import prepare,infer_prepared
from possession.v2 import infer as v2
from possession.official import PITCH

ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}

@pytest.mark.parametrize('family',['throw_in','corner','fast_restart'])
def test_restart_fixture_has_a_controlled_receiver(family):
    s=make(family,31);n=len(s.truth)
    distance=np.linalg.norm((s.tracking.players[:,8,:2]-s.tracking.ball[:,:2])*np.asarray(PITCH),axis=1)
    assert np.mean(distance[n-200:n-50]<2.)>.95

def test_external_learner_is_deterministic_and_fits_a_small_signal():
    rng=np.random.default_rng(882);x=rng.normal(size=(500,len(FEATURE_NAMES)));y=(x[:,0]+x[:,1]>0).astype(int)
    a=fit(x,y);b=fit(x,y)
    assert a==b and np.mean((predict(a,x)>0)==y)>.9

def test_invalid_learned_parameters_are_rejected():
    x=np.zeros((20,len(FEATURE_NAMES)));y=np.r_[np.zeros(10),np.ones(10)]
    model=fit(x,y);model['coef'][0]=float('nan')
    with pytest.raises(ValueError):predict(model,x)

def test_prepared_v2_is_identical_to_preserved_v2():
    s=make('aerial',31)
    expected=v2(s.tracking,s.events,CONFIG,s.blocks)[0]
    parts=prepare(s.tracking,s.events,CONFIG,s.blocks)
    actual=infer_prepared(parts,len(s.truth),CONFIG,None,'v2')[0]
    assert np.array_equal(expected,actual)

def test_targets_cannot_affect_learned_input_features():
    s=make('short_control',31);before=prepare(s.tracking,s.events,CONFIG,s.blocks)[0]['features']
    s.truth[:]=2
    after=prepare(s.tracking,s.events,CONFIG,s.blocks)[0]['features']
    assert np.array_equal(before,after)

def test_tag_stress_contains_useful_and_incorrect_primary_priors():
    s=make('tag_errors',31)
    phases=[e for e in s.events if e['code']=='BUILD UP']
    assert any(np.all(s.truth[e['start_frame']:e['end_frame']]==1) for e in phases)
    assert any(np.all(s.truth[e['start_frame']:e['end_frame']]==0) for e in phases)


def test_identical_stationary_inputs_cannot_resolve_referee_truth():
    a=make('stationary_live',31);b=make('stationary_dead',31)
    assert np.array_equal(a.tracking.players,b.tracking.players,equal_nan=True)
    assert np.array_equal(a.tracking.ball,b.tracking.ball,equal_nan=True)
    assert np.any(a.truth!=b.truth)
    assert np.array_equal(v2(a.tracking,a.events,CONFIG,a.blocks)[0],v2(b.tracking,b.events,CONFIG,b.blocks)[0])


def test_v3_preserves_block_isolation():
    from possession.v3 import infer,load_model
    from possession.data import Tracking
    cfg=json.loads((ROOT/'configs/audit_v3.json').read_text())|{'official_prekickoff':False}
    s=make('boundary_noise',31);model=load_model(cfg)
    baseline=infer(s.tracking,s.events,cfg,model,s.blocks)[0]
    inside=np.zeros(len(s.truth),bool)
    for a,b in s.blocks:inside[a:b]=True
    p=s.tracking.players.copy();ball=s.tracking.ball.copy();p[~inside]=1e6;ball[~inside]=-1e6
    changed=infer(Tracking(p,ball,s.tracking.teams),s.events,cfg,model,s.blocks)[0]
    assert np.array_equal(baseline,changed) and np.all(changed[~inside]=='X')


@pytest.mark.parametrize('path',['submission/YDSE.csv','submission/YDSE_reproduced.csv',
    'submission/candidates/YDSE_v2.csv','submission/candidates/YDSE_v2_reproduced.csv'])
def test_v3_generator_rejects_preserved_output_paths_before_loading_data(path):
    import subprocess
    import sys
    result=subprocess.run([sys.executable,str(ROOT/'scripts/generate_submission.py'),
        '--model','v3','--config',str(ROOT/'configs/audit_v3.json'),'--out',str(ROOT/path)],
        cwd=ROOT,capture_output=True,text=True)
    assert result.returncode!=0 and 'V1 and V2 artifacts are protected' in result.stderr
