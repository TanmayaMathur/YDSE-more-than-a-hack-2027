"""Accuracy-audit candidate. V1 remains unchanged in pipeline.py.

Every rolling/motion/tag operation is local to a graded block. Confidence gates
repair demonstrated evidence bugs; gap bridges express uncertainty about timing,
not an estimated invisible ball trajectory. No match labels are consumed.
"""
import numpy as np
import warnings
from .data import Tracking, load_tracking
from .official import BLOCKS,FPS,PITCH,load_tags,KICKOFF_VIDEO_FRAMES
from .features import extract
from .preprocessing import repair_ball, rolling, velocity, runs
from .temporal import decode
from .tagging import evidence as original_tags, side
from .restarts import localize

SEMANTICS={
    'build up':(1.,1), 'progression':(1.,1),'creating chances':(1.,1),
    'ball in final third':(.5,1),'ball in the box':(.5,1),'long ball':(.35,1),
    'defending in attacking third':(.5,-1),'defending in middle third':(.5,-1),
    'defending in defensive third':(.5,-1),
    # These describe recovery/pressure or player occupation, not settled control.
    'attacking transition':(0.,0),'defensive transition':(0.,0),'players in the box':(0.,0),
    'goals':(0.,0),'set pieces':(0.,0)}

def clipped_events(events,a,b):
    result=[]
    for e in events:
        start=max(a,int(e['start_frame']));stop=min(b,int(e['end_frame']))
        if start<stop:
            result.append(e|{'start_frame':start-a,'end_frame':stop-a})
    return result

def semantic_tags(events,n,fps):
    votes=np.zeros((n,2));live=np.zeros(n)
    # Restart timing stays a context channel, independent of team phase semantics.
    _,_,restart=original_tags(events,n,fps)
    for event in events:
        code=(event['code'] or '').strip().casefold();weight,polarity=SEMANTICS.get(code,(0.,0))
        tags={k.strip().casefold():v for k,v in event['tags'].items() if k}
        team=side(tags.get('team'));a=max(0,event['start_frame']);b=min(n,event['end_frame'])
        if team is None or weight==0 or b<=a:continue
        owner=team if polarity>0 else 1-team
        ramp=np.minimum(1.,np.minimum(np.arange(b-a)+1,np.arange(b-a,0,-1))/max(1,fps/2))
        votes[a:b,owner]=np.maximum(votes[a:b,owner],weight*ramp)
        live[a:b]=np.maximum(live[a:b],weight*ramp)
    return votes[:,0]-votes[:,1],live,restart

def unique_slots(tracking,pitch):
    """Suppress numerically coincident same-team slots; no identity reconstruction.

    Only 5 cm duplicates are removed, far below the tracking's metre-scale error.
    Ties retain the first slot; equal trajectories have equal geometry and speed.
    """
    players=tracking.players.copy();n,s,_=players.shape
    for team in (0,1):
        indices=np.flatnonzero(tracking.teams==team)
        for local,j in enumerate(indices):
            if not local:continue
            earlier=indices[:local]
            delta=(players[:,earlier,:2]-players[:,None,j,:2])*np.asarray(pitch)
            duplicate=np.any(np.linalg.norm(delta,axis=2)<=.05,axis=1)
            players[duplicate,j]=np.nan
    return Tracking(players,tracking.ball,tracking.teams)

def kinematic_velocity(xy,fps,seconds=.2,max_speed=12.):
    """Centered displacement, requiring every sample in the window to be usable.

    Differencing noisy coordinates at 25 Hz then taking their norm creates a
    positive speed bias even for a motionless player. A short displacement window
    reduces that bias; impossible intermediate slot jumps invalidate the window.
    """
    k=max(1,round(seconds*fps/2));n=len(xy);out=np.full_like(xy,np.nan,dtype=float)
    if n<=2*k:return out
    valid=np.isfinite(xy).all(axis=-1)
    jumps=np.zeros_like(valid);jumps[1:]=np.linalg.norm(np.diff(xy,axis=0),axis=-1)*fps>max_speed
    ok=valid&~jumps
    cs=np.concatenate([np.zeros_like(ok[:1],dtype=int),np.cumsum(ok,axis=0)])
    window_ok=(cs[2*k+1:]-cs[:n-2*k])==2*k+1
    value=(xy[2*k:]-xy[:-2*k])/(2*k/fps)
    value[~window_ok]=np.nan
    value[np.linalg.norm(value,axis=-1)>max_speed]=np.nan
    out[k:n-k]=value
    return out

def audit_features(tracking,ball,reliability,pitch,fps,contact_gate=False):
    n=len(ball);tracking=unique_slots(tracking,pitch)
    f=extract(tracking,ball,reliability,pitch,fps,[(0,n)])
    xy=tracking.players[:,:,:2].astype(float)*np.asarray(pitch)
    pv=kinematic_velocity(xy,fps);bv=velocity(ball,fps,45.)
    count_valid=np.isfinite(pv).all(axis=2).sum(axis=1)
    supported=(count_valid>=6)&(f['count']>=8)&(count_valid>=.5*f['count'])
    # Unknown motion cannot become evidence that the whole team is stationary.
    motion_coverage=rolling(supported.astype(float),fps*2)
    f['motion_support']=motion_coverage
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        med=rolling(np.nanmedian(np.linalg.norm(pv,axis=2),axis=1),fps*2,'median')
    f['slow']=np.clip((1.3-np.nan_to_num(med,nan=2.))/.8,0,1)*motion_coverage
    f['active']=np.clip((np.nan_to_num(med,nan=1.4)-1.)/1.5,0,1)*motion_coverage
    bs=np.linalg.norm(bv,axis=1)
    speed_weight=np.minimum(reliability,np.r_[0,reliability[:-1]])
    speed_weight[~np.isfinite(bs)]=0
    # A weighted fraction, with coverage retained. Missing samples are neither
    # moving nor stationary and low-confidence repair cannot get full weight.
    stationary_mass=rolling(speed_weight*(np.nan_to_num(bs,nan=100.)<.65),fps*2)
    f['stationary']=stationary_mass
    if contact_gate:
        distance=np.linalg.norm(xy-ball[:,None,:],axis=2)
        distance[~np.isfinite(distance)]=np.inf
        slot=distance.argmin(axis=1);row=np.arange(n)
        relative=np.linalg.norm(pv[row,slot]-bv,axis=1)
        old=.7+.3*np.exp(-np.nan_to_num(relative,nan=10.)/6.)
        new=np.where(np.isfinite(relative),.25+.75*np.exp(-relative/4.),.4)
        factor=new/old
        f['control']*=factor;f['quality']*=factor
    f['ball_speed']=bs
    return f

def gap_evidence(control,reliability,fps):
    """Weak two-sided ownership bridge, only after sustained confident endpoints.

    An unseen opposing-control interval is unidentifiable. A symmetric weak bridge
    chooses its midpoint rather than a DP tie's arbitrary early edge. Strong tags
    can still disagree; the uncertainty bracket is retained in diagnostics.
    """
    bridge=np.zeros(len(control));brackets=[];width=max(2,round(.6*fps))
    for a,b in runs(reliability==0):
        if a<width or b+width>len(control):continue
        left=control[a-width:a];right=control[b:b+width]
        if np.mean(reliability[a-width:a]>=.5)<.8 or np.mean(reliability[b:b+width]>=.5)<.8:continue
        lo=float(np.median(left));hi=float(np.median(right))
        if abs(lo)<.4 or abs(hi)<.4:continue
        l,r=np.sign(lo),np.sign(hi)
        if l==r:
            bridge[a:b]=.2*l
        else:
            bridge[a:b]=.2*np.linspace(l,r,b-a)
            brackets.append((int(a),int(b)))
    return bridge,brackets

def validate_config(config,fps,blocks,n):
    keys=['max_gap_s','max_ball_speed','geometry_weight','tag_weight','team_switch','dead_switch']
    if not np.isfinite(fps) or fps<=0:raise ValueError('FPS must be positive')
    if any(not np.isfinite(config[k]) or config[k]<0 for k in keys):raise ValueError('Invalid nonnegative configuration')
    duration=np.asarray(config['minimum_s'],float)
    if duration.shape!=(3,) or not np.isfinite(duration).all() or np.any(duration<=0):raise ValueError('Invalid durations')
    previous=0
    for a,b in blocks:
        if not 0<=a<b<=n or a<previous:raise ValueError('Invalid/non-disjoint blocks')
        previous=b

def infer(tracking,events,config,blocks=BLOCKS,fps=FPS,pitch=PITCH,return_diagnostics=False):
    n=len(tracking.ball);validate_config(config,fps,blocks,n)
    labels=np.full(n,'X',dtype='<U1');alphabet=np.array(['H','A','D']);diagnostics=[]
    totals={'restarts_localized_by_motion':0,'hidden_turnover_brackets':0}
    for a,b in blocks:
        local=Tracking(tracking.players[a:b],tracking.ball[a:b],tracking.teams)
        ball,reliability=repair_ball(local.ball[:,:2]*np.asarray(pitch),[(0,b-a)],fps,config['max_gap_s'],config['max_ball_speed'])
        scoped=clipped_events(events,a,b)
        if config.get('fix_reliability',True):
            f=audit_features(local,ball,reliability,pitch,fps,config.get('contact_gate',False))
        else:
            f=extract(local,ball,reliability,pitch,fps,[(0,b-a)])
        if config.get('use_tags',True):
            tag,live,restart=(semantic_tags if config.get('fix_semantics',True) else original_tags)(scoped,b-a,fps)
        else:tag=live=restart=np.zeros(b-a)
        rl,rq,rt,located=localize(scoped,f['ball_speed'],reliability,f['slow'],fps)
        if not config.get('use_restarts',True):
            rl=rq=rt=restart=np.zeros(b-a);located=0
        bridge,brackets=gap_evidence(f['control'],reliability,fps) if config.get('gap_bridge',True) else (np.zeros(b-a),[])
        geom=config['geometry_weight']*f['control']
        tag_score=config['tag_weight']*tag
        team=geom+tag_score+.5*rt+bridge
        dead=(config['dead_bias']+4.5*f['outside']*reliability+5*f['stationary']*f['slow']+
              2.6*f['missing']*f['slow']+1.1*restart*f['slow']-1.3*f['active']-.7*live-.8*f['quality']+.8*rq-2*rl)
        if config.get('conservative_dead',False):
            # Experimental tradeoff: prevent uncorroborated quiet live play from
            # being called dead, at the cost of missing untagged quiet stoppages.
            no_context=(restart==0)&(f['outside']==0)&(rq==0)
            dead[no_context]=np.minimum(dead[no_context],-.4)
        e=np.column_stack((team,-team,dead))
        pre=0
        if config.get('official_prekickoff',True) and (a,b) in BLOCKS and a==BLOCKS[1][0]:
            pre=min(b-a,max(0,KICKOFF_VIDEO_FRAMES['2nd Half']-a));e[:pre]=[-1e6,-1e6,0]
        path=decode(e,fps,config['minimum_s'],config['team_switch'],config['dead_switch'])
        # Explicit contract, independent of soft costs and duration truncation.
        path[:pre]=2;labels[a:b]=alphabet[path]
        totals['restarts_localized_by_motion']+=located;totals['hidden_turnover_brackets']+=len(brackets)
        if return_diagnostics:
            diagnostics.append(dict(first=a,labels=labels[a:b],emission=e,reliability=reliability,
                raw_visible=np.isfinite(local.ball[:,:2]).all(axis=1),geometry=geom,tag=tag_score,
                bridge=bridge,dead=dead,restart_live=rl,restart_quiet=rq,restart_team=rt,
                gap_brackets=brackets,half_length=b-a))
    totals['labels']={k:int(np.sum(labels==k)) for k in 'HADX'}
    return (labels,totals,diagnostics) if return_diagnostics else (labels,totals)

def run(data_dir,config):
    return infer(load_tracking(data_dir),load_tags(data_dir=str(data_dir)),config)
