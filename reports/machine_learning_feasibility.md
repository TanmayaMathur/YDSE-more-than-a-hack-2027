# Machine-learning feasibility and executed prototype

A small externally trained LIVE/DEAD head helped the confirmed dead-ball weakness.
No evidence here justifies a large neural training pipeline or claims to solve
unobserved possession histories. The executed model is CPU-only, deterministic
regularized logistic regression, using existing NumPy rather than PyTorch because
the chosen model is a small convex tabular fit.

## Rules and data split

[Current official rules](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/RULES.md)
permit other-game supervised learning and label-free adaptation/pseudo-labels on
the provided match. Human labels on the provided game and public-window tuning
are prohibited. These are different cases. No competition supervision, public
window selection, pseudo-label adaptation or manual corrections enter this work.
The FAQ additionally prohibits restricted-data disclosure to hosted LLMs; all
restricted inference stays local. Signed enrolment terms were not located and
cannot be declared fully verified; see the official guidance report.

J03WOH is explicitly development/training now. Initial prototype trains first
half only and evaluates its correlated second half; that comparison guided the
choice and is not independent validation. Final model uses both development
halves and then locks weights before J03WQQ/J03WN1 evaluation. Neither new match
is used for normalization, fitting, regularization selection or blend tuning.

## Experiments actually run

First-half prototype second-half spellF1 (V2 / full learned / 50% blend): clean
.4163/.5070/.4744, burst1729 .3307/.4549/.3813, 0.05m noise
.3803/.4860/.4166. Full replacement harms goalkeeper and loose-ball artificial
cases, so the conservative blend was selected before new evaluation outcomes.

Final fit: 82,329 rows, one in five frames from both
halves and three label-independent views (clean, burst1729, noise); **18 features,
19 coefficients**, L2=.05, training normalization only, bounded log odds ±5.
Two deterministic fits were exactly equal. Initial training took
16.35s. A later independently invoked retraining to a separate
private path reproduced the canonical weight-file SHA-256 byte for byte.
The model is 2,500 bytes, not a
GPU checkpoint. The externally trained JSON is shipped with licence/attribution
and source-design credit in `THIRD_PARTY_NOTICES.md`; no competitor weights or
predictions were used. The IRLS design is explicitly credited, not presented as
an invented new learning algorithm.

Features use reliability, stillness, player speed/coverage, outside/boundary
position, control quality/margin, player proximity and interactions. Training
targets are external BallStatus. Inference feature functions accept no labels.
The model falls back to heuristic D energy when neither ball nor player motion
has sufficient support. H/A evidence, costs, minimums, tags and restarts are
unchanged. The .5 blend is a composite energy, not calibrated class probabilities.

Independent clean spellF1 V2→V3 is .4248→.4799 and .3318→.4235; all twelve
corruption views favor V3. Artificial holdout mean remains .8531, equal to V2.
False D and direct-handover regressions remain; see expanded validation.

## Other options assessed, not claimed executed

| Option | Feasibility and missing evidence | Decision |
|---|---|---|
| Self-supervised trajectory encoder | Permitted locally, but anonymous slot discontinuities and no direct D/ownership objective; representation gain alone does not establish spell gain | No neural training attempted |
| Unsupervised HMM/state discovery | Can cluster geometry/motion but state identity need not mean referee-live or controlled ownership; identical static worlds remain ambiguous | Existing duration decoder retained |
| Algorithmic pseudo-labels | Permitted without human correction; can distill and amplify current D/midpoint errors | No pseudo-label model fitted |
| External sequence model/PathCRF | Relevant ball-free interactions, but identity continuity, D mapping, train/evaluation overlap and reproducible weights need audit | Public method inspected; not executed or imported |
| Tracking-confidence learner | Automatic physical signals could supply targets, but no independent correctness labels/calibration demonstrated | Existing coverage gates retained |
| Confidence-adaptive change points | Small CPU prototype was run on development simulations, .8420 mean equals fixed costs | Not adopted |
| Local whistle/referee/video evidence | Potential independent sensor for identical tracking states; suitable annotated training, licensed weights and alignment not verified | Not implemented; no sensor accuracy claimed |

One development match is still a small training population; its corruptions are
not independent samples, and DFL source/semantics are shared across evaluation.
No full posterior calibration, crowded-occlusion model or neural benchmark was
established. The strongest feasible intervention before the deadline is the
small reproducible blend, with its measured tradeoffs documented.

Commands and exact hashes are in `models/README.md` and `docs/technical_report_v3.md`.
Inference never requires network or access to the external evaluation targets.
