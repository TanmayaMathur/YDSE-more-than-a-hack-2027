"""Verify external ball indices/timestamps independently of model outputs."""
import json
from datetime import datetime
from final_external_data import folder_for,frames,ROOT


def main():
    rows=[]
    for match in ['J03WQQ','J03WN1']:
        folder=folder_for(match);raw=next(folder.glob('*positions_raw_observed*.xml'))
        sections={}
        for series,frame in frames(raw):
            if series.get('TeamId')!='BALL' or series.get('GameSection') not in ('firstHalf','secondHalf'):continue
            period=series['GameSection'];num=int(frame['N']);clock=datetime.fromisoformat(frame['T'])
            if period not in sections:sections[period]=dict(first=num,last=num,count=0,previous_time=clock)
            s=sections[period]
            if s['count']:
                assert num==s['last']+1,(match,period,'duplicate or missing ball row')
                assert abs((clock-s['previous_time']).total_seconds()-.04)<1e-6,(match,period,'clock mismatch')
            s.update(last=num,count=s['count']+1,previous_time=clock)
        summary={k:{x:v[x] for x in ['first','last','count']} for k,v in sections.items()}
        assert sum(x['count'] for x in summary.values())==json.loads((folder/'evaluation_inputs.json').read_text())['rows']
        rows.append(dict(match=match,periods=summary,continuous_ball_indices=True,all_ball_timestamps_40ms=True))
        print('All external ball indices and timestamps verified:',match,flush=True)
    (ROOT/'reports/final_external_alignment.json').write_text(json.dumps(rows,indent=2),newline='\n')


if __name__=='__main__':main()
