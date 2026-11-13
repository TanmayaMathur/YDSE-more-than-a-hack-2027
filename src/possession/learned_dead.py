"""Small externally supervised LIVE/DEAD head; no label access in feature/inference APIs."""
import numpy as np
from .v2 import kinematic_velocity
from .preprocessing import rolling

FEATURE_NAMES=('visible','stationary','slow','active','motion_support','missing','outside',
    'control_quality','control_margin_abs','near_player','near_boundary','ball_speed',
    'stationary_slow','missing_slow','stationary_contact','stationary_without_contact',
    'moving_near_player','player_active_fraction')

def features(tracking,ball,reliability,f,pitch,fps):
    n=len(ball);xy=tracking.players[:,:,:2].astype(float)*np.asarray(pitch)
    distance=np.linalg.norm(xy-ball[:,None,:],axis=2);distance[~np.isfinite(distance)]=np.inf
    nearest=distance.min(axis=1);contact=np.exp(-np.minimum(nearest,50)/2.)*reliability
    boundary=np.minimum.reduce([ball[:,0],pitch[0]-ball[:,0],ball[:,1],pitch[1]-ball[:,1]])
    edge=np.nan_to_num(np.exp(-np.maximum(boundary,0)/2),nan=0.)*reliability
    speed=np.clip(np.nan_to_num(f['ball_speed'],nan=0.),0,30)/30
    pv=kinematic_velocity(xy,fps);ps=np.linalg.norm(pv,axis=2);known=np.isfinite(ps)
    frac=(known&(ps>2)).sum(axis=1)/np.maximum(1,known.sum(axis=1))
    frac=rolling(frac,fps)
    stationary=f['stationary'];slow=f['slow']
    values=np.column_stack((reliability,stationary,slow,f['active'],f.get('motion_support',np.zeros(n)),
        f['missing'],f['outside']*reliability,f['quality'],np.abs(f['control']),contact,edge,speed,
        stationary*slow,f['missing']*slow,stationary*contact,stationary*(1-contact),speed*contact,frac))
    if not np.isfinite(values).all():raise ValueError('Nonfinite learned-head features')
    available=(reliability>0)|(f.get('motion_support',np.zeros(n))>.5)
    return values,available

def fit(values,labels,l2=.05):
    x=np.asarray(values,float);y=np.asarray(labels,float)
    if x.ndim!=2 or x.shape[1]!=len(FEATURE_NAMES) or y.shape!=(len(x),) or not np.isfinite(x).all() or not np.isfinite(y).all() or set(np.unique(y))!={0,1}:
        raise ValueError('Invalid external binary training data')
    mean=x.mean(0);scale=x.std(0);scale[scale<1e-6]=1
    z=np.c_[np.ones(len(x)),(x-mean)/scale];coef=np.zeros(z.shape[1])
    penalty=np.eye(len(coef))*l2;penalty[0,0]=0
    for iteration in range(60):
        p=1/(1+np.exp(-np.clip(z@coef,-30,30)));w=np.maximum(p*(1-p),1e-6)
        gradient=z.T@(p-y)/len(y)+penalty@coef
        hessian=(z.T*w)@z/len(y)+penalty+np.eye(len(coef))*1e-8
        update=np.linalg.solve(hessian,gradient)
        norm=np.linalg.norm(update)
        if norm>5:update*=5/norm
        coef-=update
        if np.max(np.abs(update))<1e-7:break
    return dict(schema='ydse_external_live_dead_v1',feature_names=list(FEATURE_NAMES),
        mean=mean.tolist(),scale=scale.tolist(),coef=coef.tolist(),l2=l2,iterations=iteration+1,
        training_frames=len(y),training_dead_fraction=float(y.mean()))

def predict(model,values):
    if model.get('feature_names')!=list(FEATURE_NAMES):raise ValueError('Learned-head schema mismatch')
    mean=np.array(model['mean']);scale=np.array(model['scale']);coef=np.array(model['coef'])
    if mean.shape!=(len(FEATURE_NAMES),) or scale.shape!=mean.shape or coef.shape!=(len(FEATURE_NAMES)+1,) or np.any(scale<=0) or not all(np.isfinite(a).all() for a in [mean,scale,coef]):
        raise ValueError('Invalid learned-head parameters')
    return np.clip(coef[0]+((values-mean)/scale)@coef[1:],-5,5)
