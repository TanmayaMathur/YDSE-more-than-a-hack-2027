# Synthetic stress tests - accuracy audit

Executed 64 development scenarios and 128 frozen holdout scenarios, each 30 seconds at 25 FPS, across 16 families and 11 configurations (2,112 final-protocol model runs). The initial stronger-contact prototype also ran on development cases and is preserved separately.

Families/holdout seeds were recorded in design_freeze.json before development; v2.py/config were frozen before the holdout run. No model change followed holdout or external outcomes.

| Family | V1 dev | V2 dev | V1 holdout | V2 holdout |
|---|---:|---:|---:|---:|
| stable_gaps | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| hidden_turnover | 0.9000 | 1.0000 | 0.9000 | 1.0000 |
| incidental_touch | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| rapid_turnovers | 0.5496 | 0.5496 | 0.7810 | 0.7810 |
| aerial | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| crowded_box | 0.7500 | 0.7500 | 1.0000 | 1.0000 |
| stationary_live | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| restart_uncertain | 0.7000 | 0.7000 | 0.7000 | 0.7000 |
| ambiguous_tags | 0.2000 | 1.0000 | 0.2000 | 1.0000 |
| slot_switch | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| duplicates_sparse | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| conflicting_evidence | 0.2000 | 0.2000 | 0.2000 | 0.2000 |
| short_control | 0.3000 | 0.3000 | 0.4750 | 0.4750 |
| long_stoppage_blocks | 0.6400 | 0.6400 | 0.6400 | 0.6400 |
| zones_directions | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| trajectory_corruption | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

Unweighted family/case means: development V1 0.7650, V2 0.8212; holdout V1 0.8060, V2 0.8622.

Scores use the actual official library. Each case records predicted transition frames/types, false/missed D rates, missed/spurious spells and failure types in accuracy_stress_*.json. Synthetic transition traces are public artificial data; match transition traces are private.

Most score gain comes from the ambiguous-tag and hidden-turnover constructions. Many other families are unchanged, and short control, crowds and wrong primary phases still fail. The noiseless stationary-live counterexample is separately recorded in audit_probes.json and fails in both versions. Passing its noisy family does not solve the identifiability problem.

The scenario mix is deliberately adversarial, not a football sampling distribution. Its tag-bearing cases disproportionately contain incorrect/ambiguous tags. Therefore the no-tags ablation has an artificial advantage and is not grounds to discard all tagging. Larger holdout coordinate noise is one distribution shift, not a substitute for independent matches. No statistical or competition ranking conclusion is drawn from these averages.
