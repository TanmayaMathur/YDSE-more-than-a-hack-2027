import itertools
import json
from pathlib import Path
import numpy as np
import pytest
from possession.data import Tracking
from possession.features import extract
from possession.temporal import decode
from possession.pipeline import infer as v1
from possession.v2 import infer as v2,audit_features,semantic_tags,gap_evidence,clipped_events
from possession.audit_scenarios import make,FAMILIES
from possession.official import PITCH
import possession_metrics as pm

ROOT=Path(__file__).resolve().parents[1]
C1=json.loads((ROOT/'configs/final.json').read_text())|{'official_prekickoff':False}
C2=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}

def test_repair_confidence_cannot_become_full_stationary_evidence():
    s=make('stationary_live',11);n=len(s.truth);ball=np.tile([35.,30.],(n,1))
    low=audit_features(s.tracking,ball,np.full(n,.01),PITCH,25)
    high=audit_features(s.tracking,ball,np.ones(n),PITCH,25)
    assert low['stationary'].max()<=.0100001
    assert high['stationary'].max()>.9

def test_one_static_player_is_not_collective_stillness():
    n=200;p=np.full((n,16,3),np.nan);p[:,0,:2]=[.3,.4]
    tr=Tracking(p,np.full((n,3),np.nan),np.r_[np.zeros(8,int),np.ones(8,int)])
    old=extract(tr,np.full((n,2),np.nan),np.zeros(n),PITCH,25,[(0,n)])
    new=audit_features(tr,np.full((n,2),np.nan),np.zeros(n),PITCH,25)
    assert old['slow'][100]==1 and new['slow'][100]==0

def test_motion_noise_bias_and_constant_velocity():
    from possession.v2 import kinematic_velocity
    rng=np.random.default_rng(993)
    xy=np.tile([20.,30.],(500,16,1))+rng.normal(0,.04,(500,16,2))
    naive=np.linalg.norm(np.diff(xy,axis=0),axis=2)*25
    robust=np.linalg.norm(kinematic_velocity(xy,25),axis=2)
    assert np.nanmedian(naive)>1 and np.nanmedian(robust)<.5
    linear=np.c_[np.arange(200)/25,np.zeros(200)]
    assert np.nanmedian(np.linalg.norm(kinematic_velocity(linear,25),axis=1))==pytest.approx(1.)

def test_ungraded_observations_cannot_change_v2_graded_output():
    s=make('long_stoppage_blocks',11);a,b=s.blocks[1]
    original=v2(s.tracking,s.events,C2,s.blocks)[0]
    changed=s.tracking.players.copy();changed[:a]=np.random.default_rng(8).normal(size=changed[:a].shape)
    changed_ball=s.tracking.ball.copy();changed_ball[:a]=np.random.default_rng(9).normal(size=changed_ball[:a].shape)
    tr=Tracking(changed,changed_ball,s.tracking.teams)
    new=v2(tr,s.events,C2,[(a,b)])[0]
    assert np.array_equal(original[a:b],new[a:b])

def test_event_clipping_and_unknown_semantics_are_neutral():
    e={'code':'DEFENDING UNDOCUMENTED','start_frame':-100,'end_frame':1000,'tags':{'Team':'Barcelona'}}
    es=clipped_events([e],50,150)
    assert es[0]['start_frame']==0 and es[0]['end_frame']==100
    prior,_,_=semantic_tags(es,100,25);assert np.all(prior==0)
    for code in ['DEFENSIVE TRANSITION','ATTACKING TRANSITION','PLAYERS IN THE BOX']:
        p,_,_=semantic_tags([e|{'code':code,'start_frame':0,'end_frame':100}],100,25)
        assert np.all(p==0)

def test_correlated_and_conflicting_tags_are_bounded():
    e={'code':'BUILD UP','start_frame':0,'end_frame':200,'tags':{'Team':'Barcelona'}}
    a=semantic_tags([e],200,25)[0];b=semantic_tags([e]*50,200,25)[0]
    assert np.array_equal(a,b)
    opposite=e|{'tags':{'Team':'Atletic Club'}}
    assert np.all(semantic_tags([e,opposite],200,25)[0]==0)

def test_exact_duplicate_slots_do_not_create_independent_votes():
    s=make('stable_gaps',29)
    base=v2(s.tracking,[],C2,s.blocks)[0]
    p=np.concatenate([s.tracking.players,s.tracking.players[:,[2,2,2,10,10,10]]],axis=1)
    teams=np.r_[s.tracking.teams,s.tracking.teams[[2,2,2,10,10,10]]]
    copy=v2(Tracking(p,s.tracking.ball,teams),[],C2,s.blocks)[0]
    assert np.array_equal(base,copy)

def test_missing_turnover_boundary_is_bracketed_not_known():
    c=np.r_[np.ones(100),np.zeros(200),-np.ones(100)]
    rel=np.r_[np.ones(100),np.zeros(200),np.ones(100)]
    bridge,brackets=gap_evidence(c,rel,25)
    assert brackets==[(100,300)] and bridge[110]>0 and bridge[290]<0
    e=np.c_[2.4*c,-2.4*c,np.full(400,-2.)]
    original=decode(e);e[:,:2]+=np.c_[bridge,-bridge]
    revised=decode(e)
    assert np.flatnonzero(np.diff(original))[0]+1==100
    assert abs((np.flatnonzero(np.diff(revised))[0]+1)-200)<=1

def test_reappearance_false_touch_cannot_trigger_a_gap_bridge():
    c=np.ones(400);c[100:300]=0;c[300:303]=-1
    rel=np.ones(400);rel[100:300]=0
    bridge,brackets=gap_evidence(c,rel,25)
    assert not brackets and np.all(bridge[100:300]>=0)

@pytest.mark.parametrize('fps',[20,25,50])
def test_decoder_physical_time_scales_with_fps(fps):
    n=round(12*fps);e=np.tile([2.,-2.,-2.],(n,1));e[6*fps:,:2]=[-2.,2.]
    path=decode(e,fps=fps)
    assert abs((np.flatnonzero(np.diff(path))[0]+1)/fps-6.)<=1/fps

def test_rowwise_log_normalization_cannot_change_the_energy_optimum():
    rng=np.random.default_rng(177);e=rng.normal(size=(200,3))
    shift=np.log(np.exp(e).sum(axis=1))[:,None]
    assert np.array_equal(decode(e),decode(e-shift))

@pytest.mark.parametrize('durations',[(1,1,1),(1,2,1),(2,1,3),(2,2,2)])
def test_decoder_exhaustive_optimum(durations):
    rng=np.random.default_rng(71);e=rng.normal(size=(6,3))
    def score(seq):
        starts=np.r_[0,np.flatnonzero(np.diff(seq))+1,len(seq)]
        if any(starts[i+1]-starts[i]<durations[seq[starts[i]]] for i in range(len(starts)-2)):
            return -np.inf
        return sum(e[i,s] for i,s in enumerate(seq))-sum(.3 if a<2 and b<2 else .2 for a,b in zip(seq,seq[1:]) if a!=b)
    path=decode(e,fps=1,minimum_s=durations,team_switch=.3,dead_switch=.2)
    assert score(path)==pytest.approx(max(score(s) for s in itertools.product(range(3),repeat=6)))

def test_actual_metric_false_dead_splits_real_possession():
    gt=np.zeros(100,np.int8);pred=gt.copy();pred[40:60]=pm.D
    assert pm.evaluate(gt,pred)['spell_f1_mean']<1
    # Leading/trailing ungraded data must not join halves.
    gt=np.array([0,0,3,3,0,0],np.int8)
    assert len(pm.possession_spells(gt,pm.valid_runs(gt)))==2

def test_actual_metric_x_propagates_old_state_across_turnover():
    gt=np.r_[np.zeros(100,int),np.ones(100,int)]
    pred=gt.copy();pred[90:170]=pm.X
    filled=pm.fill_abstentions(pred,pm.valid_runs(gt))
    assert np.all(filled[100:170]==pm.H)
    assert pm.evaluate(gt,pred)['spell_f1_mean']<1

def test_external_target_fields_never_enter_model_inputs(tmp_path):
    from validate_external_dfl import parse
    meta='<root><General MatchId="DFL-MAT-J03WOH" Season="2022/2023" HomeTeamId="H" GuestTeamId="A"/>'
    meta+='<Team TeamId="H"><Player PersonId="p1"/></Team><Team TeamId="A"><Player PersonId="p2"/></Team></root>'
    (tmp_path/'test_matchinformation.xml').write_text(meta)
    xml='<root><PitchSize X="105" Y="68"/>'
    for section,start in [('firstHalf',10000),('secondHalf',20000)]:
        for team,person in [('H','p1'),('A','p2'),('BALL','BALL')]:
            xml+=f'<FrameSet GameSection="{section}" TeamId="{team}" PersonId="{person}">'
            for i in range(3):
                target=' BallStatus="1" BallPossession="1"' if team=='BALL' else ''
                xml+=f'<Frame N="{start+i}" T="2022-08-26T16:32:09.{720+40*i:03d}+00:00" X="0" Y="0"{target}/>'
            xml+='</FrameSet>'
    xml+='</root>';path=tmp_path/'test_positions_raw_observed.xml';path.write_text(xml)
    a,gt,_,_,_=parse(tmp_path)
    path.write_text(xml.replace('BallPossession="1"','BallPossession="2"'))
    b,other,_,_,_=parse(tmp_path)
    assert np.all(gt==0) and np.all(other==1)
    assert np.array_equal(a.ball,b.ball,equal_nan=True)
    assert np.array_equal(a.players,b.players,equal_nan=True)

@pytest.mark.parametrize('family',FAMILIES)
def test_stress_family_contracts(family):
    s=make(family,11)
    labels,_=v2(s.tracking,s.events,C2,s.blocks)
    assert len(labels)==len(s.truth) and set(labels)<=set('HADX')
    mask=np.zeros(len(labels),bool)
    for a,b in s.blocks:mask[a:b]=True
    assert np.all(labels[~mask]=='X')
