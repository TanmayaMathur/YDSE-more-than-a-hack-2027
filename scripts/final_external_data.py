"""Other-match loader with labels isolated from Tracking; no competition reads."""
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from possession.data import Tracking

def folder_for(match):
    if match=='J03WOH':return ROOT/'private/accuracy_audit/external_dfl'
    if match in ('J03WQQ','J03WN1'):return ROOT/'private/final_accuracy/external'/match
    raise ValueError('Only predeclared external matches allowed')

def frames(path):
    series={}
    for event,node in ET.iterparse(path,events=('start','end')):
        if event=='start' and node.tag=='FrameSet':series=dict(node.attrib)
        elif event=='end' and node.tag=='Frame':
            yield series,dict(node.attrib);node.clear()
        elif event=='end' and node.tag=='FrameSet':node.clear()

def load(match):
    folder=folder_for(match);cache=folder/'evaluation_inputs.npz';info=folder/'evaluation_inputs.json'
    if cache.exists() and info.exists():
        with np.load(cache,allow_pickle=False) as z:
            p=z['players'];b=z['ball'];teams=z['teams'];labels=z['labels'];blocks=z['blocks'].tolist();pitch=z['pitch'].tolist()
        return Tracking(p,b,teams),labels,[tuple(x) for x in blocks],tuple(pitch),json.loads(info.read_text())
    meta=next(folder.glob('*matchinformation*.xml'));raw=next(folder.glob('*positions_raw_observed*.xml'))
    root=ET.parse(meta).getroot();general=next(root.iter('General'))
    assert general.get('MatchId')=='DFL-MAT-'+match
    assert general.get('Season')=='2022/2023'
    team_ids=[general.get('HomeTeamId'),general.get('GuestTeamId')]
    slots=[];teams=[]
    for team in root.iter('Team'):
        if team.get('TeamId') in team_ids:
            for player in team.iter('Player'):
                slots.append(player.get('PersonId'));teams.append(team_ids.index(team.get('TeamId')))
    spans={};pitch=None
    for event,node in ET.iterparse(raw,events=('start','end')):
        if event=='start' and node.tag=='PitchSize':pitch=(float(node.get('X')),float(node.get('Y')))
        if event=='start' and node.tag=='FrameSet':series=dict(node.attrib)
        elif event=='end' and node.tag=='Frame':
            period=series['GameSection'];num=int(node.get('N'))
            if period in ('firstHalf','secondHalf'):
                lo,hi=spans.get(period,[num,num]);spans[period]=[min(lo,num),max(hi,num)]
            node.clear()
        elif event=='end' and node.tag=='FrameSet':node.clear()
    offsets={};blocks=[];n=0
    for period in ('firstHalf','secondHalf'):
        a,b=spans[period];offsets[period]=n-a;blocks.append((n,n+b-a+1));n+=b-a+1
    p=np.full((n,len(slots),3),np.nan,np.float32);ball=np.full((n,3),np.nan,np.float32);labels=np.full(n,3,np.int8)
    index={s:i for i,s in enumerate(slots)};codes=set();times=[]
    for series,frame in frames(raw):
        period=series['GameSection']
        if period not in offsets:continue
        row=int(frame['N'])+offsets[period];x=float(frame.get('X','nan'));y=float(frame.get('Y','nan'))
        if len(times)<2:times.append(frame['T'])
        if series.get('TeamId') in team_ids and series.get('PersonId') in index:
            p[row,index[series['PersonId']],:2]=[x/pitch[0]+.5,y/pitch[1]+.5]
        elif series.get('TeamId')=='BALL':
            ball[row,:2]=[x/pitch[0]+.5,y/pitch[1]+.5]
            status=frame.get('BallStatus');owner=frame.get('BallPossession');codes.add((status,owner))
            if status=='0':labels[row]=2
            elif status=='1' and owner in ('1','2'):labels[row]=int(owner)-1
    from datetime import datetime
    assert abs((datetime.fromisoformat(times[1])-datetime.fromisoformat(times[0])).total_seconds()-.04)<1e-6
    assert pitch and all(s in ('0','1') and o in ('0','1','2') for s,o in codes)
    provenance=dict(match_id=match,title=general.get('MatchTitle'),rows=n,fps=25,pitch=pitch,players=len(slots),
        source='https://doi.org/10.6084/m9.figshare.28196177.v1',licence='CC BY 4.0',
        target_fields='BallStatus and BallPossession, isolated from Tracking',unknown_reference_frames=int(np.sum(labels==3)))
    np.savez_compressed(cache,players=p,ball=ball,teams=np.array(teams),labels=labels,blocks=blocks,pitch=pitch)
    info.write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    return Tracking(p,ball,np.array(teams)),labels,blocks,pitch,provenance

def condition(tracking,name,pitch,fps=25):
    """Label-independent perturbations; no reference labels accepted by this function."""
    seeds={'burst1729':1729,'burst3253':3253,'coordinate_noise':7117,'slot_switches':9011,'combined':14027}
    if name=='clean':return tracking
    rng=np.random.default_rng(seeds[name]);p=tracking.players.copy();ball=tracking.ball.copy();n=len(ball)
    if name.startswith('burst') or name=='combined':
        state=False;mask=np.zeros(n,bool)
        for i in range(n):
            state=(rng.random()>=1/40) if state else (rng.random()<(.41/.59/40));mask[i]=state
        ball[mask,:2]=np.nan
    if name in ('coordinate_noise','combined'):
        p[:,:,:2]+=rng.normal(0,.05,p[:,:,:2].shape)/np.asarray(pitch)
        ball[:,:2]+=rng.normal(0,.05,ball[:,:2].shape)/np.asarray(pitch)
    if name in ('slot_switches','combined'):
        for a in range(20*fps,n,20*fps):
            for team in (0,1):
                ids=np.flatnonzero(tracking.teams==team)
                p[a:,ids]=p[a:,rng.permutation(ids)]
    return Tracking(p,ball,tracking.teams)
