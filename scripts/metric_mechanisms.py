"""Score independently constructed metric failure cases with the actual scorer."""
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'upstream'))
import possession_metrics as pm

def main():
    base=np.r_[np.zeros(150,int),np.ones(150,int),np.zeros(150,int)]
    cases={'perfect':(base,base.copy())}
    p=base.copy();p[60:70]=1;cases['false_touch']=(base,p)
    p=base.copy();p[150:300]=0;cases['missed_turnovers']=(base,p)
    p=np.r_[base[:1].repeat(25),base[:-25]];cases['late_1_second']=(base,p)
    p=base.copy();p[60:70]=2;cases['false_dead']=(base,p)
    g=base.copy();g[60:90]=2;p=g.copy();p[60:90]=0;cases['missed_dead']=(g,p)
    p=base.copy();p[140:240]=3;cases['abstain_across_turnover']=(base,p)
    g=base.copy();g[200:210]=0;p=np.zeros(len(base),int);cases['oversmoothed_short_spells']=(g,p)
    g=np.array([0]*50+[3]*50+[0]*50);cases['two_halves_same_team']=(g,g.copy())
    result={}
    for name,(gt,pred) in cases.items():
        r=pm.evaluate(gt,pred)
        result[name]={k:r[k] for k in ['spell_f1_mean','macro_f1','n_gt_spells','n_pred_spells']}
    (ROOT/'reports/metric_mechanisms.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
