import json
from pathlib import Path
import numpy as np
import pytest
from possession.preprocessing import repair_ball
from possession.tagging import evidence, side
from possession.temporal import decode
from possession.pipeline import infer
from possession.data import Tracking

CONFIG = json.loads((Path(__file__).resolve().parents[1]/'configs/final.json').read_text())

def test_gaps_confidence_outlier_and_half_reset():
    ball = np.column_stack((np.arange(100)*.1, np.zeros(100)))
    ball[10:15] = np.nan
    ball[30:70] = np.nan
    ball[80] = [900,900]
    ball[0] = np.nan
    repaired, confidence = repair_ball(ball, [(0,50),(50,100)], 25)
    assert np.isfinite(repaired[10:15]).all()
    assert np.all((confidence[10:15] > 0) & (confidence[10:15] < 1))
    assert np.isnan(repaired[30:70]).all()
    assert np.isnan(repaired[0]).all()
    assert np.isfinite(repaired[80]).all() and repaired[80,0] < 10
    longer = ball.copy(); longer[10:25] = np.nan
    _, c2 = repair_ball(longer, [(0,100)],25)
    assert c2[15] < confidence[12]

def event(code, team='Barcelona', start=0, stop=100):
    return dict(code=code, start_frame=start,end_frame=stop,tags={'Team':team})

def test_defensive_polarity_saturation_and_na_restart():
    defense, _, _ = evidence([event('DEFENDING IN MIDDLE THIRD')],100,25)
    assert np.all(defense[20:80] < 0)
    offense, _, _ = evidence([event('BUILD UP')]*20,100,25)
    assert offense.max() <= 1
    prior, live, restart = evidence([event('SET PIECES','N/A')],100,25)
    assert np.all(prior == 0) and restart.max() == 1 and np.all(live == 0)
    assert side('Atletic Club') == 1 and side('N/A') is None

def test_temporal_noise_missing_and_real_short_turnover():
    e = np.zeros((500,3)); e[:,0]=2.4; e[:,1]=-2.4; e[:,2]=-2
    e[60:70,:2] = [-2.4,2.4]  # brief deflection: too little integrated evidence
    e[100:160,:2] = 0        # observation gap: preserve H
    e[230:255,:2] = [-2.4,2.4] # genuine one-second control survives
    e[350:,:2] = [-2.4,2.4]
    out = decode(e)
    assert np.all(out[:230] == 0)
    assert np.all(out[230:255] == 1)
    assert np.all(out[255:350] == 0)
    assert np.all(out[350:] == 1)

def test_dead_duration_and_boundaries():
    e=np.zeros((300,3)); e[:,0]=2; e[:,1]=-2; e[:,2]=-3
    e[100:200]=[-2,-2,5]
    p=decode(e)
    assert np.all(p[100:200]==2)
    assert np.all(p[:100]==0) and np.all(p[200:]==0)
    assert np.array_equal(p,decode(e))

def synthetic_tracking(n=600):
    # Moving players and ball, with a deterministic home->away control change.
    p=np.full((n,16,3),np.nan,np.float32)
    t=np.arange(n)/25
    for j in range(16):
        p[:,j,0]=(15+j*4+2*t)/105.3
        p[:,j,1]=(10+(j%4)*12)/68
        p[:,j,2]=2
    b=np.zeros((n,3),np.float32)
    b[:300,:2]=p[:300,1,:2]
    b[300:,:2]=p[300:,10,:2]
    b[100:130,:2]=np.nan
    return Tracking(p,b,np.r_[np.zeros(8,dtype=int),np.ones(8,dtype=int)])

def test_complete_synthetic_pipeline_missing_and_permutation():
    tr=synthetic_tracking(); cfg=CONFIG|{'official_prekickoff':False}
    labels,stats=infer(tr,[],cfg,blocks=[(0,600)])
    assert np.all(labels[20:280]=='H')
    assert np.all(labels[320:580]=='A')
    assert not np.any(labels=='D')  # ball disappearance alone cannot create dead ball
    order=np.random.default_rng(7).permutation(16)
    reordered=Tracking(tr.players[:,order],tr.ball,tr.teams[order])
    other,_=infer(reordered,[],cfg,blocks=[(0,600)])
    assert np.array_equal(labels,other)
    swapped=Tracking(tr.players,tr.ball,1-tr.teams)
    swapped_labels,_=infer(swapped,[],cfg,blocks=[(0,600)])
    assert np.array_equal(swapped_labels,np.where(labels=='H','A',np.where(labels=='A','H',labels)))

def test_synthetic_stationary_slow_players_are_dead():
    tr=synthetic_tracking()
    tr.players[150:400]=tr.players[150]
    tr.ball[150:400,:2]=tr.players[150,1,:2]
    labels,_=infer(tr,[],CONFIG|{'official_prekickoff':False},blocks=[(0,600)])
    assert np.all(labels[200:350]=='D')

def test_pipeline_does_not_read_ground_truth():
    # Architectural guard: no inference import/path may introduce the public window.
    src=Path(__file__).resolve().parents[1]/'src/possession'
    for path in src.glob('*.py'):
        text=path.read_text()
        assert 'possession_gt' not in text

def test_duration_decoder_agrees_with_bruteforce():
    import itertools
    rng=np.random.default_rng(19)
    e=rng.normal(size=(7,3))
    actual=decode(e,fps=1,minimum_s=(2,2,2),team_switch=.3,dead_switch=.2)
    def objective(seq):
        change=np.r_[0,np.flatnonzero(np.diff(seq))+1,len(seq)]
        # Every segment except the final one must mature before a transition.
        if any(change[i+1]-change[i]<2 for i in range(len(change)-2)):
            return -np.inf
        score=sum(e[t,k] for t,k in enumerate(seq))
        for a,b in zip(seq,seq[1:]):
            if a!=b:
                score-=.3 if a<2 and b<2 else .2
        return score
    optimum=max(objective(seq) for seq in itertools.product(range(3),repeat=len(e)))
    assert objective(actual)==pytest.approx(optimum)

def test_restart_motion_localization_and_no_invented_anchor():
    from possession.restarts import localize
    speed=np.zeros(300); speed[150:]=6
    tag=event('SET PIECES','Atletic Club',100,200)
    live,quiet,vote,n=localize([tag],speed,np.ones(300),np.ones(300),25)
    assert n==1 and np.argmax(live)==150
    assert quiet[140]>0 and vote[150]<0
    live,quiet,vote,n=localize([tag],np.full(300,np.nan),np.zeros(300),np.ones(300),25)
    assert n==0 and np.all(live==0) and np.all(vote==0)
