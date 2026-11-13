"""Localize optional restart boundaries using a stationary-to-moving ball change."""
import numpy as np

def localize(events, speed, reliability, slow, fps):
    n=len(speed)
    before=max(2,round(.6*fps)); after=max(2,round(.4*fps))
    live=np.zeros(n); quiet=np.zeros(n); vote=np.zeros(n)
    located=0
    from .tagging import side
    for event in events:
        if (event['code'] or '').strip().casefold()!='set pieces':
            continue
        a=max(before,event['start_frame']); b=min(n-after,event['end_frame'])
        best=None
        for t in range(a,b):
            pre=speed[t-before:t]; post=speed[t:t+after]
            pre_ok=np.isfinite(pre)&(reliability[t-before:t]>=.5)
            post_ok=np.isfinite(post)&(reliability[t:t+after]>=.5)
            if pre_ok.mean()<.6 or post_ok.mean()<.6:
                continue
            # Both the change and its context must support a real restart.
            low=np.median(pre[pre_ok]); high=np.median(post[post_ok])
            if low>=.65 or high<2.5 or np.mean(slow[t-before:t])<.3:
                continue
            purity=np.mean(pre[pre_ok]<.65)+np.mean(post[post_ok]>=2.5)
            contrast=min(high,12.)-low+.2*purity
            if best is None or contrast>best[0]:
                best=(contrast,t)
        if best is None:
            continue
        located+=1; t=best[1]
        stop=min(n,t+round(.8*fps)); start=max(0,t-round(3*fps))
        decay=np.linspace(1.,0.,stop-t)
        live[t:stop]=np.maximum(live[t:stop],decay)
        quiet[start:t]=np.maximum(quiet[start:t],slow[start:t])
        tags={k.casefold():v for k,v in event['tags'].items() if k}
        team=side(tags.get('team'))
        if team is not None:
            vote[t:stop]+=(1 if team==0 else -1)*decay
    return live,quiet,np.clip(vote,-1,1),located
