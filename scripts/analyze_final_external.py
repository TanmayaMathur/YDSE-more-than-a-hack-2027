"""Fixed prediction error accounting; reads only external evaluation artifacts."""
import json
import sys
from pathlib import Path
import numpy as np
from freeze_final_candidate import verify_freeze
from validate_external_dfl import paired_spell_interval
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'upstream'))
import possession_metrics as pm


def main():
    verify_freeze();rows=[]
    for match in ['J03WQQ','J03WN1']:
        for condition in ['clean','burst1729','burst3253','coordinate_noise','slot_switches','combined']:
            path=ROOT/'private/final_accuracy/external'/match/f'predictions_{condition}.npz'
            with np.load(path) as z:
                gt=z['truth'];pred={v:pm.label_codes(z[v]) for v in ['v2','v3']}
            runs=pm.valid_runs(gt);spells=pm.possession_spells(gt,runs)
            flags={v:pm.matched_gt_flags(pm.spell_overlaps(spells,pm.possession_spells(p,runs)),len(spells),.5) for v,p in pred.items()}
            handovers=[t for t in pm.transitions(gt,runs) if t[1]<pm.D and t[2]<pm.D]
            matched={}
            for v,p in pred.items():
                pt=[t for t in pm.transitions(p,runs) if t[1]<pm.D and t[2]<pm.D]
                matched[v]={tuple(a) for a,b in pm.transition_scores(handovers,pt,25)['pairs']}
            lost=matched['v2']-matched['v3'];gained=matched['v3']-matched['v2']
            shorts={}
            for seconds in (1,2,3):
                mask=np.array([(b-a)/25<seconds for a,b,k in spells])
                shorts[str(seconds)]=dict(n=int(mask.sum()),lost=int((mask&flags['v2']&~flags['v3']).sum()),
                    gained=int((mask&~flags['v2']&flags['v3']).sum()))
            source_interval=paired_spell_interval(gt,{'v1':pred['v2'],'v2':pred['v3']})
            interval=dict(low95=source_interval['delta_v2_minus_v1_low95'],
                high95=source_interval['delta_v2_minus_v1_high95'],draws=source_interval['draws'],
                seed=source_interval['seed'],method=source_interval['method'])
            rows.append(dict(match=match,condition=condition,paired_v3_minus_v2=interval,
                short_spell_changes=shorts,direct_handovers_lost=len(lost),direct_handovers_gained=len(gained),
                lost_handovers_with_D_within_1s=sum(np.any(pred['v3'][max(0,t-25):t+26]==pm.D) for t,a,b in lost)))
    # Convert NumPy integers before public JSON serialization.
    result=dict(rows=rows,uncertainty='Exploratory same-match paired spell resampling, fixed prediction counts; not match-level or competition confidence intervals')
    (ROOT/'reports/final_external_error_analysis.json').write_text(json.dumps(result,indent=2,default=int),newline='\n')
    for r in rows:
        if r['condition']=='clean':print(r)


if __name__=='__main__':main()
