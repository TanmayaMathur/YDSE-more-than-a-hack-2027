"""Small independent counterexamples to Version 1 assumptions; no match data."""
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from possession.data import Tracking
from possession.features import extract
from possession.temporal import decode
from possession.pipeline import infer as infer_v1
from possession.v2 import infer as infer_v2

def main():
    n=200; fps=25; pitch=(105.3,68.)
    p=np.full((n,16,3),np.nan)
    p[:,:,:2]=np.array([.3,.4]);p[:,:,2]=0
    ball=np.tile([32.,27.],(n,1));reliability=np.ones(n)
    tr=Tracking(p,np.c_[ball/np.array(pitch),np.zeros(n)],np.r_[np.zeros(8,int),np.ones(8,int)])
    # A single tracked stationary player is not evidence that all players stopped.
    p[:]=np.nan;p[:,0,:2]=[.3,.4]
    f=extract(tr,np.full((n,2),np.nan),np.zeros(n),pitch,fps,[(0,n)])
    sparse_slow=float(f['slow'][100])
    # A tiny interpolation confidence still becomes full stationary evidence.
    p[:,:,:2]=[.3,.4]
    f_low=extract(tr,ball,np.full(n,.01),pitch,fps,[(0,n)])
    f_high=extract(tr,ball,np.ones(n),pitch,fps,[(0,n)])
    # Alter only ungraded frames; keep the second graded block identical.
    p=np.zeros((n,16,3));p[:,:,:2]=np.arange(n)[:,None,None]*np.array([.0006,0.])
    p[:,:,0]+=np.arange(16)[None,:]*.03
    tr=Tracking(p,np.zeros((n,3)),tr.teams)
    f1=extract(tr,ball,np.ones(n),pitch,fps,[(80,170)])
    altered=p.copy();altered[:80]=altered[79]
    f2=extract(Tracking(altered,tr.ball,tr.teams),ball,np.ones(n),pitch,fps,[(80,170)])
    leakage=float(np.max(np.abs(f1['slow'][80:90]-f2['slow'][80:90])))
    e=np.zeros((400,3));e[:,2]=-2;e[:100,:2]=[2.4,-2.4];e[300:,:2]=[-2.4,2.4]
    decoded=decode(e)
    switches=(np.flatnonzero(decoded[1:]!=decoded[:-1])+1).tolist()
    # Two different referee states can generate exactly the same observed geometry.
    n2=400;t=np.arange(n2)/25;p2=np.zeros((n2,16,3));teams=np.r_[np.zeros(8,int),np.ones(8,int)]
    for j in range(16):p2[:,j,:2]=np.c_[25+t,np.full(n2,20.)]+[3*j,5*(j%3)]
    ball2=p2[:,0,:2]+[.3,0]
    p2[100:300]=p2[100];ball2[100:300]=ball2[100]
    p2[:,:,:2]/=np.array(pitch)
    tr2=Tracking(p2,np.c_[ball2/np.array(pitch),np.zeros(n2)],teams)
    c1=json.loads((ROOT/'configs/final.json').read_text())|{'official_prekickoff':False}
    c2=json.loads((ROOT/'configs/audit_v2.json').read_text())|{'official_prekickoff':False}
    live1=infer_v1(tr2,[],c1,[(0,n2)])[0];live2=infer_v2(tr2,[],c2,[(0,n2)])[0]
    result={'single_stationary_player_slow_score':sparse_slow,
            'stationary_score_at_reliability_0.01':float(f_low['stationary'][100]),
            'stationary_score_at_reliability_1.0':float(f_high['stationary'][100]),
            'graded_feature_change_when_only_ungraded_input_changes':leakage,
            'unobserved_turnover_gap':[100,300],'v1_turnover_frames':switches,
            'identical_static_geometry_live_or_whistle':{
                'v1_dead_fraction_in_constructed_live_pause':float(np.mean(live1[140:260]=='D')),
                'v2_dead_fraction_in_constructed_live_pause':float(np.mean(live2[140:260]=='D')),
                'warning':'Same observations also support a real stoppage. No geometric-only classifier can distinguish referee permission in this pair.'},
            'meaning':'Constructed mechanisms only, not competition quality estimates'}
    (ROOT/'reports/audit_probes.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
