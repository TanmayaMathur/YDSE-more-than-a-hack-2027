"""Transition evidence export. Match-specific rows MUST remain private/local."""
import numpy as np
from .official import BLOCKS,FPS,PITCH,KICKOFF_VIDEO_FRAMES
from .preprocessing import repair_ball
from .features import extract
from .tagging import evidence
from .restarts import localize
from .temporal import decode

def original_diagnostics(tracking,events,config):
    n=len(tracking.ball)
    ball,rel=repair_ball(tracking.ball[:,:2]*np.asarray(PITCH),BLOCKS,FPS,config['max_gap_s'],config['max_ball_speed'])
    f=extract(tracking,ball,rel,PITCH,FPS,BLOCKS)
    tag,live,restart=evidence(events,n,FPS)
    rl,rq,rt,_=localize(events,f['ball_speed'],rel,f['slow'],FPS)
    geometry=config['geometry_weight']*f['control'];ts=config['tag_weight']*tag
    signal=geometry+ts+.5*rt
    dead=(config['dead_bias']+4.5*f['outside']*rel+5*f['stationary']*f['slow']+2.6*f['missing']*f['slow']+
          1.1*restart*f['slow']-1.3*f['active']-.7*live-.8*f['quality']+.8*rq-2*rl)
    emission=np.c_[signal,-signal,dead];chunks=[]
    for index,(a,b) in enumerate(BLOCKS):
        e=emission[a:b].copy()
        if index==1:
            pre=KICKOFF_VIDEO_FRAMES['2nd Half']-a;e[:pre,:2]=-1e6;e[:pre,2]=1e6
        path=decode(e,FPS,config['minimum_s'],config['team_switch'],config['dead_switch'])
        chunks.append(dict(first=a,labels=np.array(['H','A','D'])[path],emission=e,reliability=rel[a:b],
            raw_visible=np.isfinite(tracking.ball[a:b,:2]).all(axis=1),geometry=geometry[a:b],tag=ts[a:b],
            dead=dead[a:b],bridge=np.zeros(b-a),restart_live=rl[a:b],restart_quiet=rq[a:b],restart_team=rt[a:b],gap_brackets=[]))
    return chunks

def summarize(chunks,config):
    rows=[];durations={'H':[],'A':[],'D':[]};no_ball=0;total=0;drop_near=0;weak=0;tagdom=0;rapid=0
    label_code={'H':0,'A':1,'D':2}
    for chunk in chunks:
        labels=chunk['labels'];n=len(labels);first=chunk['first'];total+=n
        no_ball+=int(np.sum(~chunk['raw_visible']))
        edges=np.r_[0,np.flatnonzero(labels[1:]!=labels[:-1])+1,n]
        for a,b in zip(edges[:-1],edges[1:]):
            durations[str(labels[a])].append((b-a)/FPS)
        for j,t in enumerate(edges[1:-1],1):
            old=str(labels[t-1]);new=str(labels[t]);dest=label_code[new]
            scores=chunk['emission'][t];margin=float(scores[dest]-np.max(np.delete(scores,dest)))
            lo=max(0,t-FPS);hi=min(n,t+FPS+1)
            near=bool(np.any(~chunk['raw_visible'][lo:hi]));drop_near+=near
            isweak=margin<.2;weak+=isweak
            istag=abs(chunk['tag'][t])>abs(chunk['geometry'][t]);tagdom+=istag
            elapsed=(t-edges[j-1])/FPS;minimum=config['minimum_s'][label_code[old]]
            rapid+=elapsed<.8
            rows.append(dict(frame=int(first+t),seconds=(first+t)/FPS,previous=old,new=new,
                reliability=float(chunk['reliability'][t]),geometry=float(chunk['geometry'][t]),
                tag=float(chunk['tag'][t]),gap_bridge=float(chunk['bridge'][t]),dead=float(chunk['dead'][t]),
                restart_live=float(chunk['restart_live'][t]),restart_quiet=float(chunk['restart_quiet'][t]),
                restart_team=float(chunk['restart_team'][t]),
                transition_cost=config['team_switch'] if old in 'HA' and new in 'HA' else config['dead_switch'],
                prior_state_duration_s=float(elapsed),source_duration_satisfied=bool(elapsed+1/FPS>=minimum),
                instantaneous_margin=margin,near_ball_dropout=near,tag_dominant_emission=bool(istag)))
    def stats(values):
        return dict(count=len(values),p10_s=float(np.percentile(values,10)) if values else None,
            median_s=float(np.median(values)) if values else None,p90_s=float(np.percentile(values,90)) if values else None)
    summary=dict(graded_frames=total,spell_count=len(durations['H'])+len(durations['A']),
        dead_segments=len(durations['D']),duration_distribution={k:stats(v) for k,v in durations.items()},
        no_visible_ball_fraction=no_ball/max(total,1),transitions=len(rows),rapid_prior_states=int(rapid),
        weak_instantaneous_transition_margins=int(weak),transitions_near_dropouts=int(drop_near),
        tag_dominant_transition_emissions=int(tagdom),
        margin_percentiles=np.percentile([r['instantaneous_margin'] for r in rows],[10,50,90]).tolist() if rows else [],
        caution='Emission dominance is not causal attribution; margins are not calibrated probabilities.')
    return rows,summary

def restart_rejection_summary(events,chunks):
    """Aggregate why strict motion anchors fail. No window timestamps are returned."""
    before=round(.6*FPS);after=round(.4*FPS)
    summary=dict(tagged_windows=0,coverage_supported=0,stationary_to_launch_supported=0,all_conditions_supported=0)
    from .preprocessing import rolling
    from .v2 import clipped_events
    for chunk in chunks:
        a=chunk['first'];n=len(chunk['labels']);scoped=clipped_events(events,a,a+n)
        # Candidate exports speed/quiet arrays locally to support this diagnosis.
        speed=chunk.get('ball_speed');slow=chunk.get('slow')
        if speed is None:continue
        rel=chunk['reliability']
        for event in scoped:
            if (event['code'] or '').strip().casefold()!='set pieces':continue
            summary['tagged_windows']+=1;coverage=launch=accepted=False
            for t in range(max(before,event['start_frame']),min(n-after,event['end_frame'])):
                pre=speed[t-before:t];post=speed[t:t+after]
                ok1=np.isfinite(pre)&(rel[t-before:t]>=.5);ok2=np.isfinite(post)&(rel[t:t+after]>=.5)
                if ok1.mean()<.6 or ok2.mean()<.6:continue
                coverage=True
                if np.median(pre[ok1])<.65 and np.median(post[ok2])>=2.5:
                    launch=True
                    if np.mean(slow[t-before:t])>=.3:accepted=True
            summary['coverage_supported']+=int(coverage)
            summary['stationary_to_launch_supported']+=int(launch)
            summary['all_conditions_supported']+=int(accepted)
    return summary
