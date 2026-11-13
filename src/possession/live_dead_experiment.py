"""Isolated learned-head experiment reusing frozen V2 geometry and decoder.

This is not automatically a selected V3. Learning happens only in the external
development script. Inference receives features and a small supplied JSON model.
"""
import numpy as np
from .data import Tracking
from .official import BLOCKS,FPS,PITCH,KICKOFF_VIDEO_FRAMES
from .preprocessing import repair_ball
from .v2 import clipped_events,audit_features,semantic_tags,gap_evidence,validate_config
from .restarts import localize
from .temporal import decode
from .learned_dead import features,predict

def prepare(tracking,events,config,blocks=BLOCKS,fps=FPS,pitch=PITCH):
    validate_config(config,fps,blocks,len(tracking.ball));chunks=[]
    for a,b in blocks:
        tr=Tracking(tracking.players[a:b],tracking.ball[a:b],tracking.teams)
        ball,rel=repair_ball(tr.ball[:,:2]*np.asarray(pitch),[(0,b-a)],fps,config['max_gap_s'],config['max_ball_speed'])
        f=audit_features(tr,ball,rel,pitch,fps,False);scoped=clipped_events(events,a,b)
        if config.get('use_tags',True):tag,live,restart=semantic_tags(scoped,b-a,fps)
        else:tag=live=restart=np.zeros(b-a)
        rl,rq,rt,located=localize(scoped,f['ball_speed'],rel,f['slow'],fps)
        if not config.get('use_restarts',True):rl=rq=rt=restart=np.zeros(b-a);located=0
        bridge,brackets=gap_evidence(f['control'],rel,fps) if config.get('gap_bridge',True) else (np.zeros(b-a),[])
        team=config['geometry_weight']*f['control']+config['tag_weight']*tag+.5*rt+bridge
        dead=(config['dead_bias']+4.5*f['outside']*rel+5*f['stationary']*f['slow']+2.6*f['missing']*f['slow']+
              1.1*restart*f['slow']-1.3*f['active']-.7*live-.8*f['quality']+.8*rq-2*rl)
        values,available=features(tr,ball,rel,f,pitch,fps)
        chunks.append(dict(first=a,stop=b,team=team,dead=dead,features=values,available=available,
            restart_delta=.8*rq-2*rl-.7*live,restart_count=located,gap_brackets=brackets,
            reliability=rel,control=f['control'],tag=tag,raw_visible=np.isfinite(tr.ball[:,:2]).all(axis=1)))
    return chunks

def infer_prepared(chunks,n,config,model,mode='blend',fps=FPS,return_diagnostics=False):
    labels=np.full(n,'X',dtype='<U1');diag=[]
    if mode not in ('v2','learned','blend'):raise ValueError('Unknown prototype mode')
    for c in chunks:
        a,b=c['first'],c['stop'];team=c['team'];original=c['dead']
        if mode=='v2':dead=original.copy()
        else:
            log_odds=predict(model,c['features'])
            # Binary LIVE/DEAD odds are relative to the best live team score.
            # This avoids confusing uncertain team identity with dead-ball evidence.
            learned=np.abs(team)+log_odds+c['restart_delta']
            learned[~c['available']]=original[~c['available']]
            weight=1. if mode=='learned' else .5
            dead=(1-weight)*original+weight*learned
        emission=np.c_[team,-team,dead];pre=0
        if config.get('official_prekickoff',True) and (a,b) in BLOCKS and a==BLOCKS[1][0]:
            pre=min(b-a,KICKOFF_VIDEO_FRAMES['2nd Half']-a);emission[:pre]=[-1e6,-1e6,0]
        path=decode(emission,fps,config['minimum_s'],config['team_switch'],config['dead_switch']);path[:pre]=2
        labels[a:b]=np.array(['H','A','D'])[path]
        if return_diagnostics:diag.append(c|{'emission':emission,'labels':labels[a:b]})
    stats=dict(model_mode=mode,labels={k:int(np.sum(labels==k)) for k in 'HADX'},
        restarts_localized_by_motion=sum(c['restart_count'] for c in chunks))
    return (labels,stats,diag) if return_diagnostics else (labels,stats)
