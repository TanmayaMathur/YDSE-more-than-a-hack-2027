"""Independent procedural tests. These scores do NOT estimate competition performance."""
import json
from pathlib import Path
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from possession.data import Tracking
from possession.pipeline import infer
from possession.official import FPS, PITCH
from baseline import smooth
import possession_metrics as pm

def simulate(seed, n=1800):
    rng=np.random.default_rng(seed)
    truth=np.empty(n,np.int8)
    pos=0; state=0
    while pos<n:
        length=int(rng.integers(35,230))
        truth[pos:min(n,pos+length)]=state
        pos+=length
        state=int(rng.choice([s for s in (0,1,2) if s!=state]))
    # Team motion is coherent; stoppages freeze the pitch configuration.
    motion=np.cumsum(np.where(truth==2,0.,.045))
    ball=np.column_stack((35+4*np.sin(motion/4),32+3*np.cos(motion/5)))
    p=np.empty((n,16,3),np.float32)
    for slot in range(16):
        p[:,slot,:2]=ball+np.array([((slot%8)-3.5)*5,(-1 if slot<8 else 1)*(8+(slot%4)*4)])
        p[:,slot,2]=0
    # One carrier and one presser per team; same geometry in every scenario.
    p[:,0,:2]=ball+[1.,0.]
    p[:,8,:2]=ball+[6.,0.]
    p[truth==1,0,:2]=ball[truth==1]+[6.,0.]
    p[truth==1,8,:2]=ball[truth==1]+[1.,0.]
    b=np.zeros((n,3),np.float32); b[:,:2]=ball
    # Small observation noise, short occlusion blocks, and isolated false ball positions.
    p[:,:,:2]+=rng.normal(0,.08,(n,16,2))
    b[:,:2]+=rng.normal(0,.03,(n,2))
    # Preserve genuinely stationary stoppages despite detector jitter.
    for a,bound in zip(np.r_[0,np.flatnonzero(truth[1:]!=truth[:-1])+1],
                       np.r_[np.flatnonzero(truth[1:]!=truth[:-1])+1,n]):
        if truth[a]==2:
            p[a:bound,:,:2]=p[a,:,:2]
            b[a:bound,:2]=b[a,:2]
    for start in rng.integers(0,n-60,12):
        b[start:start+int(rng.integers(5,55)),:2]=np.nan
    for start in rng.integers(0,n-10,4):
        if truth[start]<2:
            opponent=8 if truth[start]==0 else 0
            b[start:start+5,:2]=p[start:start+5,opponent,:2]
    p[:,:,:2]/=np.array(PITCH)
    b[:,:2]/=np.array(PITCH)
    return Tracking(p,b,np.r_[np.zeros(8,int),np.ones(8,int)]),truth

def main():
    config=json.loads((ROOT/'configs/final.json').read_text())|{'official_prekickoff':False}
    results=[]; begin=time.perf_counter()
    for seed in range(20):
        tracking,truth=simulate(seed)
        labels,_=infer(tracking,[],config,blocks=[(0,len(truth))])
        pred=pm.label_codes(labels)
        xy=tracking.players[:,:,:2]*np.array(PITCH)
        ball=tracking.ball[:,:2]*np.array(PITCH)
        dist=np.linalg.norm(xy-ball[:,None,:],axis=2)
        dist[~np.isfinite(dist)]=np.inf
        nearest=tracking.teams[dist.argmin(axis=1)]
        nearest[np.isinf(dist).all(axis=1)]=-1
        methods={'raw':pm.label_codes(smooth(nearest,0)),
                 'smooth50':pm.label_codes(smooth(nearest,50)), 'YDSE':pred}
        for name,codes in methods.items():
            metric=pm.evaluate(truth,codes)
            results.append(dict(seed=seed,method=name,accuracy=metric['accuracy'],
                                synthetic_spell_f1=metric['spell_f1_mean'],
                                synthetic_macro_f1=metric['macro_f1']))
    summary={name:{key:float(np.mean([r[key] for r in results if r['method']==name]))
                   for key in ['accuracy','synthetic_spell_f1','synthetic_macro_f1']}
             for name in ['raw','smooth50','YDSE']}
    report={'description':'Procedural scenarios only; not match or leaderboard estimates',
            'seeds':list(range(20)),'seconds':time.perf_counter()-begin,'summary':summary,'results':results}
    (ROOT/'reports/synthetic_benchmark.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))

if __name__=='__main__':
    main()
