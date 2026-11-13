# Implemented improvements and rejected changes

| Change/source | Original limitation and evidence | Candidate method | Verification | Risk / included? |
|---|---|---|---|---|
| v2.infer, clipped_events | .6378 slow-score change from ungraded-only input edits | All repair/features/events/restarts scoped per graded block | Boundary invariance test; full-match contract | Short edge windows have less evidence; included |
| v2.audit_features | Single static tracked player became collective slow=1; .01 reliability became stationary=1 | Coverage-gated collective evidence and continuously weighted stationary mass | Sparse/low-confidence probes and tests | Heuristic coverage cutoffs remain; included |
| v2.kinematic_velocity | 4 cm position noise produces >1 m/s differentiated apparent motion | Approximately .2 s centered displacement with jump/sample checks | Known-static noise and constant-velocity tests | Short offline smoothing window may weaken abrupt motion; included |
| v2.unique_slots | Coincident slots inflate density/counts | Remove same-team positions coincident within .05 m | Exact duplicate-invariance test | Near duplicates and real close overlaps not perfectly resolved; included |
| v2.semantic_tags | All defensive transitions/occupancy implied ownership; unknown defending prefix inverted | Explicit category map; weak defensive thirds; neutral ambiguous codes; max-pool repetition | Polarity, unknown, contradiction and overlap tests; designed stress cases | Incorrect long primary phases still cause errors; included |
| v2.gap_evidence | H-before/A-after gap switches at its first frame by tie | Weak two-sided ownership bridge from sustained reliable endpoints; retain timing bracket | Hidden-turnover/false-reappearance tests and ablation | Symmetric prior, not detected invisible contact; included |
| generator CLI | Relative --config crashed after CSV write | Resolve path before hash; require separate candidate destination | Actual full-run failure fixed; two candidate runs pass | Existing V1 defaults retained; included |
| stronger contact gate | Proposed reception filter reduced rapid-control recovery | Experimental only, disabled in final V2 config | Development prototype and frozen holdout ablation | Erases valid rapid interceptions; excluded |
| quiet-only dead cap | False stationary-live stoppages | Experimental ablation only | Paired ambiguous-geometry probe | Misses indistinguishable genuine stoppages; excluded |

The original seven inference modules, original final.json and protected V1 artifacts
remain unchanged. No calibrated posterior, learned HSMM, new vision model or externally
trained model is claimed. New diagnostics are local-only for per-transition match evidence.

57 tests passed and compileall passed during the audit. The full-match candidate was
generated twice, passed the official and strict validators, matched byte-for-byte and
passed published half/pre-kickoff constraints. Frozen synthetic and independent external
results support specific mechanisms and modest measured gains, not universal accuracy.
