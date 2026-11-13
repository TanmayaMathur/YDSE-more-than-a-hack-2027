"""New development/frozen stress split, including observationally ambiguous pairs."""
import numpy as np
from .audit_scenarios import make as old_make,Scenario,phase
from .data import Tracking
from .official import PITCH

FAMILIES=('stationary_live','stationary_dead','whistle_moving','throw_in','corner','fast_restart',
    'goalkeeper','aerial','loose_ball','deflection','short_control','long_gap','hidden_early',
    'hidden_late','hidden_multiple','tag_errors','duplicate_slots','ambiguous_geometry',
    'observations_tempo','boundary_noise')
DEV_SEEDS=(31,67)
HOLDOUT_SEEDS=(4093,16381,65521)

def make(family,seed):
    if family not in FAMILIES:raise ValueError('Unknown final stress family')
    mapping={'aerial':'aerial','deflection':'incidental_touch','short_control':'short_control',
        'long_gap':'stable_gaps','ambiguous_geometry':'crowded_box','duplicate_slots':'duplicates_sparse',
        'boundary_noise':'long_stoppage_blocks'}
    base='hidden_turnover' if family.startswith('hidden_') else mapping.get(family,'stable_gaps')
    s=old_make(base,seed);tr=s.tracking;n=len(s.truth);fps=s.fps;rng=np.random.default_rng(seed+211)
    p=tr.players.copy();ball=tr.ball.copy();truth=s.truth.copy();events=s.events.copy();a,b=8*fps,20*fps
    if family in ('stationary_live','stationary_dead'):
        # Identical, fully observed inputs with opposite permission to play.
        anchor=np.array([40.,34.])/np.asarray(PITCH)
        for j in range(16):p[a:b,j,:2]=anchor+np.array([j*2.,4*(j%3)])/np.asarray(PITCH)
        ball[a:b,:2]=anchor+[.3/PITCH[0],0]
        truth[a:b]=0 if family=='stationary_live' else 2;events=[]
    elif family in ('whistle_moving','throw_in','corner','fast_restart'):
        start=8*fps;stop=14*fps
        if family=='fast_restart':stop=start+round(float(rng.uniform(.4,1.2))*fps)
        truth[start:stop]=2;truth[stop:]=1
        tt=np.arange(n)/fps
        xy=np.c_[35+.8*tt,np.full(n,34.)]
        marker=np.array([-1.5,-1.5]) if family=='corner' else np.array([42.,-1.5]) if family=='throw_in' else xy[start].copy()
        lead=start-2*fps
        xy[lead:start]=np.linspace(xy[lead],marker,start-lead,endpoint=False)
        xy[start:stop]=marker
        if family=='whistle_moving':
            quiet=min(stop,start+2*fps)
            xy[start:quiet]=marker+np.c_[np.arange(quiet-start)/fps,np.zeros(quiet-start)]
            xy[quiet:stop]=xy[quiet-1]
        restart=xy[stop-1].copy()
        if family in ('throw_in','corner'):
            restart=np.array([0.,0.]) if family=='corner' else np.array([42.,0.])
            placement=min(stop-start,max(2,round(.5*fps)))
            xy[stop-placement:stop]=np.linspace(marker,restart,placement,endpoint=False)
        velocity=np.array([2.,1.]) if family=='corner' else np.array([.6,1.5]) if family=='throw_in' else np.array([1.,0.])
        xy[stop:]=restart+(tt[stop:]-tt[stop])[:,None]*velocity
        ball[:,:2]=xy/np.asarray(PITCH)
        # Home controls before the outgoing pass; away waits for and controls
        # the actual restart. Neither carrier teleports with a flighted ball.
        p[:lead,0,:2]=ball[:lead,:2]+[.6/PITCH[0],0]
        p[lead:,0,:2]=p[lead-1,0,:2]+np.c_[(tt[lead:]-tt[lead])*.4/PITCH[0],np.zeros(n-lead)]
        approach_start=2*fps
        destination=restart/np.asarray(PITCH)-[.6/PITCH[0],0]
        p[approach_start:stop,8,:2]=np.linspace(p[approach_start,8,:2],destination,stop-approach_start,endpoint=False)
        p[stop:,8,:2]=ball[stop:,:2]-[.6/PITCH[0],0]
        if family!='whistle_moving':
            events=[phase('SET PIECES','Atletic Club' if family=='corner' else 'N/A',start-fps,stop+3*fps)]
    elif family=='goalkeeper':
        ball[:,:2]=np.c_[np.full(n,5./PITCH[0]),.5+.01*np.sin(np.arange(n)/fps)]
        p[:,0,:2]=ball[:,:2]+[.5/PITCH[0],0];truth[:]=0;events=[]
    elif family=='loose_ball':
        ball[:,:2]=np.c_[.4+.01*np.sin(np.arange(n)/fps),np.full(n,.5)]
        p[:,0,:2]=ball[:,:2]+[2./PITCH[0],0];p[:,8,:2]=ball[:,:2]-[2./PITCH[0],0]
        truth[:]=0;events=[]
    elif family.startswith('hidden_'):
        # Same observed inputs permit different unobserved control histories.
        truth[:]=0
        if family=='hidden_early':truth[10*fps:]=1
        elif family=='hidden_late':truth[20*fps:]=1
        else:
            truth[11*fps:15*fps]=1;truth[19*fps:]=1
        events=[]
    elif family=='tag_errors':
        # Every seed includes both a useful and an incorrect primary phase.
        # Seed modulo selection accidentally produced only wrong tags in the
        # initial seed list; retain that initial result, but fix the test design.
        truth[:]=0;truth[7*fps:9*fps]=1
        ball[6*fps:10*fps,:2]=np.nan;ball[18*fps:22*fps,:2]=np.nan
        events=[phase('BUILD UP','Atletic Club',7*fps,9*fps),
                phase('BUILD UP','Atletic Club',19*fps,21*fps),
                phase('DEFENSIVE TRANSITION','Barcelona',24*fps,26*fps)]
    elif family=='observations_tempo':
        # Observation probability varies independently of targets.
        probability=(.2,.5,.8)[seed%3];state=False
        for i in range(n):
            state=(rng.random()>.05) if state else rng.random()<(probability/(1-probability)*.05)
            if state:ball[i,:2]=np.nan
        # Slow/fast motion is not assigned from live/dead labels.
        p[:,:,:2]+=np.sin(np.arange(n)[:,None,None]/fps)*(.003 if seed%2 else .02)
    elif family=='boundary_noise':
        p[:,:,:2]+=rng.normal(0,.1,p[:,:,:2].shape)/np.asarray(PITCH)
        ball[:,:2]+=rng.normal(0,.1,ball[:,:2].shape)/np.asarray(PITCH)
    return Scenario(Tracking(p,ball,tr.teams),truth,events,s.blocks,fps,
        {'family':family,'seed':seed,'warning':'Artificial mechanism, not representative match-frequency sampling'})
