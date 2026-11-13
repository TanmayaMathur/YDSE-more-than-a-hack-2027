"""Independent stress families. Latent ownership is generated before observations.

These artificial labels never describe the competition game. Some paired cases
are intentionally observationally ambiguous and cannot be solved by tracking alone.
"""
from dataclasses import dataclass
import numpy as np
from .data import Tracking
from .official import PITCH

FAMILIES=('stable_gaps','hidden_turnover','incidental_touch','rapid_turnovers','aerial',
          'crowded_box','stationary_live','restart_uncertain','ambiguous_tags','slot_switch',
          'duplicates_sparse','conflicting_evidence','short_control','long_stoppage_blocks',
          'zones_directions','trajectory_corruption')
DEV_SEEDS=(11,29,47,83)
# Freeze before development runs. Holdout may be evaluated only after candidate freeze.
HOLDOUT_SEEDS=(1031,2063,4099,8209,16411,32771,65537,131101)

@dataclass
class Scenario:
    tracking: Tracking
    truth: np.ndarray
    events: list
    blocks: list
    fps: int
    meta: dict

def phase(code,team,a,b):
    return dict(code=code,start_frame=int(a),end_frame=int(b),tags={'Team':team})

def make(family,seed,fps=25,seconds=30):
    if family not in FAMILIES:raise ValueError('Unknown synthetic family')
    rng=np.random.default_rng(seed)
    n=round(seconds*fps);t=np.arange(n)/fps;mid=n//2
    truth=np.zeros(n,np.int8);events=[];blocks=[(0,n)]
    v=float(rng.uniform(.8,1.8));direction=float(rng.choice([-1,1]))
    # Team shapes move independently of possession/dead state.
    base=np.array([40.,34.]);path=np.column_stack((base[0]+direction*v*(t-seconds/2),base[1]+1.2*np.sin(t/2)))
    if family=='hidden_turnover':truth[mid:]=1
    elif family=='rapid_turnovers':
        for start in np.arange(8.,22.,2.):truth[round(start*fps):round((start+rng.uniform(.4,1.3))*fps)]=1
    elif family=='short_control':truth[mid:mid+round(rng.uniform(.24,.9)*fps)]=1
    elif family=='restart_uncertain':
        truth[round(7*fps):mid]=2;truth[mid:]=1
        events=[phase('SET PIECES',rng.choice(['Atletic Club','N/A']),round(10*fps),round(20*fps))]
    elif family=='long_stoppage_blocks':
        blocks=[(0,n//3),(2*n//3,n)];truth[n//6:n//3]=2;truth[2*n//3:5*n//6]=2;truth[5*n//6:]=1
        truth[n//3:2*n//3]=3
    elif family=='zones_directions':
        path[:,0]=np.clip(path[:,0]+rng.choice([-20.,20.]),4,101)
        path[:,1]=rng.choice([7.,61.])+1.5*np.sin(t/2)
        truth[mid:]=1
    # Correlated players are not frozen just because truth says D.
    p=np.zeros((n,16,3),np.float32)
    for slot in range(16):
        offset=np.array([((slot%8)-3.5)*5,(-1 if slot<8 else 1)*(6+(slot%4)*4)])
        p[:,slot,:2]=path+offset+np.column_stack((1.5*np.sin(t/(2+slot%3)+slot),.8*np.cos(t/3+slot)))
    def smooth(a,width):
        width=max(1,int(width)|1);return np.convolve(np.pad(a,width//2,mode='edge'),np.ones(width)/width,mode='valid')
    home_distance=smooth(np.where(truth==1,4.,.65),.45*fps)
    away_distance=smooth(np.where(truth==1,.65,4.),.45*fps)
    p[:,0,:2]=path+np.c_[home_distance,np.zeros(n)]
    p[:,8,:2]=path-np.c_[away_distance,np.zeros(n)]
    ball=path.copy()
    # A stoppage's actors may keep moving; some also settle before the restart.
    if family in ('restart_uncertain','long_stoppage_blocks'):
        for a,b in _runs(truth==2):
            rest=min(b,a+round(1.5*fps))
            p[rest:b,:,:2]=p[rest,:,:2];ball[rest:b]=ball[rest]
    if family=='stationary_live':
        a,b=round(9*fps),round(20*fps)
        p[a:b,:,:2]=p[a,:,:2];ball[a:b]=ball[a]
    if family in ('incidental_touch','aerial'):
        a=round(10*fps);length=round((.6 if family=='incidental_touch' else 5.)*fps);b=a+length
        # Ball flies past an opponent, not necessarily controlled by that opponent.
        ball[a:b,0]=path[a,0]+np.arange(length)*(.08 if family=='incidental_touch' else .4)
        ball[a:b,1]=path[a,1]
        p[a:b,8,:2]=ball[a:b]+[.3,0] if family=='incidental_touch' else np.c_[np.full(length,path[a,0]+10),np.full(length,path[a,1])]
        if family=='incidental_touch':
            # The defender stands still, so the ball merely passes through proximity.
            p[a:b,8,:2]=[ball[a,0]+.6,ball[a,1]]
    if family=='crowded_box':
        for slot in range(16):p[:,slot,:2]=path+[rng.uniform(-2,2),rng.uniform(-2,2)]
        p[:,0,:2]=path+[.4,0];p[:,8,:2]=path+[-.7,0]
    if family in ('ambiguous_tags','conflicting_evidence'):
        code='DEFENSIVE TRANSITION' if family=='ambiguous_tags' else 'BUILD UP'
        team='Barcelona' if family=='ambiguous_tags' else 'Atletic Club'
        events=[phase(code,team,round(6*fps),round(24*fps))]*3
    if family=='duplicates_sparse':
        # Many identical stationary slots must not act like many independent players.
        p[round(8*fps):round(22*fps),1:8,:2]=p[round(8*fps),1,:2]
        p[round(8*fps):round(22*fps),9:,:2]=np.nan
        ball[round(8*fps):round(22*fps)]=np.nan
    if family=='slot_switch':
        for start in range(round(5*fps),n,round(2*fps)):
            for indices in [np.arange(8),np.arange(8,16)]:
                p[start:,indices,:]=p[start:,rng.permutation(indices),:]
    if family in ('stable_gaps','hidden_turnover','aerial','ambiguous_tags','conflicting_evidence'):
        if family=='hidden_turnover':a,b=round(9*fps),round(21*fps)
        elif family=='aerial':a,b=round(11*fps),round(14*fps)
        else:a,b=round(10*fps),round(18*fps)
        ball[a:b]=np.nan
        if family=='stable_gaps':
            for a in rng.integers(fps,n-2*fps,4):ball[a:a+round(.5*fps)]=np.nan
    # Detector noise is independent of the labels; holdout adds larger drift/dropout.
    noise=.04 if seed<1000 else .10
    p[:,:,:2]+=rng.normal(0,noise,p[:,:,:2].shape)
    ball+=rng.normal(0,noise*.4,ball.shape)
    if family=='trajectory_corruption':
        for a in rng.integers(fps,n-fps,12):ball[a]+=rng.normal(0,25,2)
        p[:,:,:2]+=rng.normal(0,.22,p[:,:,:2].shape)
        ball[round(12*fps):round(14*fps)]=np.nan
    p[:,:,:2]/=np.asarray(PITCH);raw=np.c_[ball/np.asarray(PITCH),np.zeros(n)].astype(np.float32)
    teams=np.r_[np.zeros(8,int),np.ones(8,int)]
    return Scenario(Tracking(p,raw,teams),truth,events,blocks,fps,
                    {'family':family,'seed':seed,'identifiability_warning':family in ('hidden_turnover','stationary_live','long_stoppage_blocks')})

def _runs(mask):
    d=np.diff(np.r_[False,mask,False].astype(int))
    return zip(np.flatnonzero(d==1),np.flatnonzero(d==-1))
