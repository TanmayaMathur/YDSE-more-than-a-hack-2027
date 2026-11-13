# Dead-ball failure analysis

V3 improves external dead-ball reliability but does not solve stationary-live
ambiguity. Evidence comes from the locked two-match evaluation, the 60-case
frozen artificial holdout and explicit emission/transition probes; no competition
reference labels are involved.

## Responsible features and decoder behavior

`src/possession/v2.py:audit_features` already gates stillness on observed motion
coverage and reliable ball samples. Its dead energy nevertheless includes
`5 × stationary × slow` and `2.6 × missing × slow`, plus outside/restart evidence,
minus activity/live-tag/control quality. The static-pair probe gives mean centre
energies H=2.400, A=−2.400, D=2.800. Accumulating this small D advantage over
seconds beats two .7 transition costs. V2 predicts D from 9.00 to 19.04 seconds
in a true all-live example. This is a feature ambiguity, not just a minimum-dwell bug.

The paired stationary-dead example has exactly the same player/ball arrays and
events but a referee stop from 8–20 seconds. No function of these inputs can
distinguish the two worlds. V3 raises centre D energy to 4.112 and predicts D
from 8.16–19.88: better dead timing, worse live timing. Both models score .1333
on stationary-live and 1.0000 on stationary-dead in the frozen holdout.
A quiet-only dead cap flips those outcomes and leaves their mean unchanged.

## What was implemented and rejected

`learned_dead.py` computes 18 physical features, including player proximity,
stationary/contact interactions, boundary distance, motion coverage and activity.
A small logistic model trained only on another match supplies binary D-vs-live
log odds. `live_dead_experiment.py` blends 50% of this evidence with the existing
D energy, while preserving team geometry, tags, restart timing and decoder costs.
The binary learned energy is relative to the stronger team energy; the resulting
composite is not a calibrated H/A/D probability.

Full learned replacement was rejected before evaluating new matches: it labels
slow goalkeeper and contested loose-ball simulations D, scoring 0 in both.
The blend retains 1.0 on those families and equals V2's mean holdout .8531.
It still misses moving-after-whistle evidence (family spellF1 .8000), whereas
full replacement reaches 1.0 at the cost of those other failures. No approach is
uniformly better on the mechanism tests.

Restart localization in `restarts.py` requires reliable stationary-to-moving
ball support within an automatic SET PIECES interval. It cannot identify the
whistle itself. No-restart ablation changes the suite mean by zero, demonstrating
limited discrimination in these fixtures, not that real restart context is
useless. The new throw-in/corner fixtures had an initial physically inconsistent
receiver; failing tests exposed it and the fixture was corrected before any
holdout outcome. Initial results and revision hashes are preserved.

## External evidence and remaining risks

| Match | Model | False D / live | Missed D / D | D onset F1 ±1s | D exit F1 ±1s | Spurious spells @.5 | Missed spells @.5 | Excess long-spell fragments |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J03WQQ | v2 | 0.0017 | 0.5402 | 0.1455 | 0.4049 | 182 | 242 | 5 |
| J03WQQ | v3 | 0.0075 | 0.2039 | 0.4623 | 0.6091 | 157 | 223 | 6 |
| J03WN1 | v2 | 0.0020 | 0.4365 | 0.2359 | 0.4021 | 208 | 363 | 2 |
| J03WN1 | v3 | 0.0081 | 0.0914 | 0.6066 | 0.5837 | 124 | 324 | 2 |

Missed-D fractions fall from 54.0%→20.4% and 43.6%→9.1% on clean matches;
false-D/live increases from about .17%→.75% and .20%→.82%. D onset/exit F1
improves, but direct handovers can disappear into D. Increased long-spell
fragmentation on WQQ (5→6) is another measured cost. With combined dropout/noise,
V3 still misses 61.4% and 52.7% of D frames: robustness is incomplete.

An independent referee gesture, local whistle/audio classifier or permitted
automatic event sensor could resolve some ambiguous states. None was trained
or validated here; do not claim those sensors work. Additional team activity
alone cannot distinguish the identical-input pair. Keep this limitation visible,
retain the blend's conservative fallback for unavailable evidence and avoid
stronger D rules without new independent data. See `final_failure_probes.json`,
`final_stress_holdout.json` and the expanded external report for all measurements.
