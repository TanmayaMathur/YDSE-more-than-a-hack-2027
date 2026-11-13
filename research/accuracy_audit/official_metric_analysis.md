# What the actual metric rewards

Specification: [official possession_metrics.py, f8f2629](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/evaluation/possession_metrics.py).
Local pinned source: upstream/possession_metrics.py. `metric_mechanisms.py` executes
the real library on independent constructed sequences; results are in reports/metric_mechanisms.json.

1. `valid_runs` derives contiguous graded spans from GT != X. Temporal operations never
   span their gaps. These spans may be shorter than a half for an external dataset with unknown labels.
2. `fill_abstentions` forward-fills predicted X inside each span and back-fills its leading
   X values from the first known answer. An entirely abstained span remains X. MacroF1 still
   charges the raw X as a frame-level miss.
3. `segments` encodes maximal constant runs; `possession_spells` keeps H/A runs only.
   D is not a possession but breaks two same-team possessions apart.
4. `spell_overlaps` enumerates same-label overlaps with IoU = intersection / union.
   Pairs sort by descending IoU, then GT and prediction indices for deterministic ties.
5. Matching is **greedy one-to-one**, not Hungarian or a maximum-cardinality assignment.
   Threshold equality is accepted. Each GT and prediction is consumed at most once.
6. At each threshold .3/.4/.5/.6/.7, F1 = 2TP/(2TP+FP+FN). The ranking score averages these
   five hard-label F1 values; there is no confidence-ranked precision/recall curve.

Constructed examples use three six-second team spells unless otherwise indicated:

| Failure | Executed synthetic spellF1 | Mechanism |
|---|---:|---|
| Perfect | 1.0000 | Every spell matched |
| Ten-frame opposing touch | .6500 | One spell becomes three; false predictions cost precision |
| Erased middle turnover | .1000 | Separate true spells merge; recall and IoU collapse |
| Ten-frame false D | .7429 | A genuine possession splits into two |
| Missed thirty-frame D | .6857 | Two same-team possessions merge |
| X spanning a turnover | .7333 | Previous ownership propagates through the new team's play |
| Smoothed-out short spells | .0667 | Genuine brief control becomes missing spells |
| Two same-team halves separated by X | 1.0000 | Halftime separation preserved |

A one-second shift scores 1.0 **in this particular six-second-spell construction**:
IoU remains above .7. This does not mean a one-second offset is universally free.
Shorter spells suffer much more. The official documentation's numerical examples
are measurements on its reference sequences, not algebraic guarantees.

Likewise, perfect H/A-only synthetic predictions have macroF1 2/3 because the library
assigns F1 zero to absent D and averages over all three classes. An always-H prediction
can score 1 on an all-H synthetic sequence; a constant guess scoring zero is a property
of the full-match setting described in the documentation, not every possible input.

Implication: do not optimize frame agreement or duration counts in isolation. Both
false and missed stoppages damage the objects being matched. A longer smoothing
window can suppress false touches while deleting legitimate short possessions.
No provided public labels were used to choose thresholds or methods in this audit.
