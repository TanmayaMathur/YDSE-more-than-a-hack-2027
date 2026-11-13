"""Official spell metrics plus interpretable external-match error summaries."""
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'upstream'))
import possession_metrics as pm

def evaluate(truth,pred,visible=None,fps=25):
    pred=pm.label_codes(pred) if np.asarray(pred).dtype.kind in 'USO' else np.asarray(pred)
    r=pm.evaluate(truth,pred);runs=pm.valid_runs(truth);filled=pm.fill_abstentions(pred,runs)
    gt=pm.possession_spells(truth,runs);spells=pm.possession_spells(filled,runs)
    flags=pm.matched_gt_flags(pm.spell_overlaps(gt,spells),len(gt),.5)
    lengths=np.array([b-a for a,b,k in gt])/fps
    transitions=pm.transitions(truth,runs);pred_trans=pm.transitions(filled,runs)
    handovers=[t for t in transitions if t[1]<pm.D and t[2]<pm.D]
    phandovers=[t for t in pred_trans if t[1]<pm.D and t[2]<pm.D]
    turnover=pm.transition_scores(handovers,phandovers,fps)
    dstart=pm.transition_scores([t for t in transitions if t[2]==pm.D],[t for t in pred_trans if t[2]==pm.D],fps)
    dend=pm.transition_scores([t for t in transitions if t[1]==pm.D],[t for t in pred_trans if t[1]==pm.D],fps)
    alive=truth<pm.D;dead=truth==pm.D
    long_fragments=[]
    for a,b,k in gt:
        if (b-a)/fps>=10:
            overlapping=sum(s==k and y>a and x<b for x,y,s in spells)
            long_fragments.append(max(0,overlapping-1))
    short={}
    for seconds in (1,2,3):
        mask=lengths<seconds;short[str(seconds)]=dict(n=int(mask.sum()),recall=float(flags[mask].mean()) if mask.any() else None)
    hidden=[]
    if visible is not None:
        hidden=[t for t in handovers if not visible[t[0]]]
    hidden_score=pm.transition_scores(hidden,phandovers,fps) if hidden else None
    return {k:r[k] for k in ['spell_f1_mean','macro_f1','alive_dead_f1','n_gt_spells','n_pred_spells']}|dict(
        spurious_spells_at50=r['spell_f1'][.5]['n_spurious'],missed_spells_at50=r['spell_f1'][.5]['n_missed'],
        short_recall=short,false_dead_on_live=float(np.mean(pred[alive]==pm.D)) if alive.any() else None,
        missed_dead=float(np.mean(pred[dead]!=pm.D)) if dead.any() else None,
        turnover_recall_1s=turnover['recall'],dead_onset_f1_1s=dstart['f1'],dead_exit_f1_1s=dend['f1'],
        excess_fragments_of_long_spells=int(sum(long_fragments)),hidden_turnovers=len(hidden),
        hidden_turnover_recall_1s=hidden_score['recall'] if hidden_score else None,
        no_ball_accuracy=float(np.mean(pred[~visible & (truth!=pm.X)]==truth[~visible & (truth!=pm.X)])) if visible is not None and np.any(~visible & (truth!=pm.X)) else None)
