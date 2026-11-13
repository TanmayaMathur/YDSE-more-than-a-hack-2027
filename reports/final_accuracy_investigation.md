# Final accuracy investigation — YDSE, 14 November 2026

V3 is justified as a separate candidate: an externally trained dead/live evidence
blend improves spellF1 on both newly selected other matches, under every fixed
evaluation condition, without changing V2's team inference or decoder. It is
not automatically promoted. Hidden-turnover timing and stationary-live ambiguity
remain unsolved; direct handover recall and false-D rate regress.

## Preservation and compliance

Started from clean `accuracy-improvement` at
`e329912c9f6db186fb946a1e87d98f173f1c81dc`; work is isolated on
`final-accuracy-investigation`. Sixteen V1/V2 CSVs, reports, configs and private
verification artifacts were hashed and copied before edits. All sixteen remain
unchanged after full V3 generation. V1 hash
`45e91b5246b6a05db7f8b5e034185e0bbd4cf6eab7c9dcc2e4b4d027f369ae35`;
V2 hash `79d4552782eebc37995ccb8603a091518dd45dbcb33cdb7ac93daca714d01f00`.
Original V1/V2 inference modules/configs remain unchanged.

Current RULES/FAQ/CHALLENGE/DATA/EVALUATION/SUBMISSION/scorer were read from
official HEAD `f8f2629`. Label-free provided-match adaptation is permitted,
same-game human supervision is not. V3 trains only on CC BY other-game data.
No supplied-match human annotations, public-window candidate scoring, manual
label corrections or competitor predictions enter these experiments. Restricted
assets and predictions remain local and excluded from Git. Signed terms remain
unverified; the Drive invitation is not sharing permission. See
`research/final_accuracy/rules_and_guidance.md` and `official_recheck.json`.
Official issue/PR/comment queries distinguish successful empty results from
404/unsupported/network failures. No new accessible maintainer conversation
was found. Source-level competitor recheck and MIT attribution are recorded.

## Controlled implementation

Only the D evidence is changed. The small 18-feature logistic head uses external
J03WOH BallStatus, with train-only normalization and L2=.05. A 50% blend with V2
retains coverage fallback and the same H/A emissions, weak bridge, tags, restarts,
costs and minimum durations. First-half prototype validation and development
stress checks preceded source/config/weight lock. J03WOH is no longer holdout.
The full learned replacement was rejected for slow-control regressions.

Source/config/weight hashes and scenario design were frozen before reading
J03WQQ/J03WN1 or synthetic holdout outcomes. A formatting-only pre-evaluation
revision canonicalized LF model bytes and hash normalization for Git portability;
the initial byte lock and unchanged numeric parameters are preserved. No
inference source, parameters or weights changed after new evaluation results.

## Executed evidence

| Match | Condition | V1 spellF1 | V2 spellF1 | V3 spellF1 | V3 − V2 |
| --- | --- | --- | --- | --- | --- |
| J03WQQ | clean | 0.4243 | 0.4248 | 0.4799 | 0.0551 |
| J03WQQ | burst1729 | 0.3471 | 0.3538 | 0.3994 | 0.0456 |
| J03WQQ | burst3253 | 0.3440 | 0.3617 | 0.4017 | 0.0401 |
| J03WQQ | coordinate_noise | 0.3793 | 0.3815 | 0.4087 | 0.0272 |
| J03WQQ | slot_switches | 0.4243 | 0.4237 | 0.4805 | 0.0569 |
| J03WQQ | combined | 0.2950 | 0.2986 | 0.3319 | 0.0332 |
| J03WN1 | clean | 0.3334 | 0.3318 | 0.4235 | 0.0917 |
| J03WN1 | burst1729 | 0.2362 | 0.2397 | 0.3116 | 0.0719 |
| J03WN1 | burst3253 | 0.2287 | 0.2361 | 0.3087 | 0.0726 |
| J03WN1 | coordinate_noise | 0.3077 | 0.3248 | 0.3371 | 0.0124 |
| J03WN1 | slot_switches | 0.3334 | 0.3322 | 0.4235 | 0.0913 |
| J03WN1 | combined | 0.2020 | 0.2257 | 0.2365 | 0.0108 |

Two matches, twelve correlated views; not a hidden score or competitor ranking.
Definitions, error counts, macroF1, paired ranges and data limitations are in
`external_validation_expanded.md` and its machine-readable JSON.

| Variant | Development spellF1 | Frozen holdout spellF1 |
| --- | --- | --- |
| v1 | 0.8137 | 0.8253 |
| v2 | 0.8420 | 0.8531 |
| no_tags | 0.8420 | 0.8537 |
| no_restarts | 0.8420 | 0.8531 |
| no_bridge | 0.8137 | 0.8253 |
| dead_cap | 0.8420 | 0.8531 |
| learned_dead | 0.7740 | 0.7631 |
| blend_dead | 0.8420 | 0.8531 |

Forty development and sixty frozen holdout scenarios cover twenty families:
static-live/dead pairs, moving-after-whistle, throw-in, corner, fast restart,
goalkeeper, aerial, loose ball, deflection, short control, long gap, early/late/
multiple hidden turnovers, useful and incorrect tags, duplicate slots, ambiguous
geometry, observation/tempo variation and noisy half boundaries. The no_tags
row disables all phase and restart channels; no_restarts disables restart
channels only. Dead cap is the experimental quiet-only cap. Full learned and
blend share all team evidence. No-bridge tests transition-localization dependence.

Initial restart fixtures lacked consistent receivers and the tag selector
accidentally chose only wrong-tag seeds. Failing tests exposed both fixture
errors; they were corrected **before** new holdout outcomes. Initial reports,
hashes and revision reasons are preserved, so corrected scores are not silently
substituted for the initial runs. Artificial means are diagnostic averages,
not estimates of how often these events occur in matches.

Fifteen additional post-freeze adversarial cases cover identity switches, rapid
controlled turnovers, conflicting tags, outliers and 2m jitter. All three models
score .6568 on rapid turnovers and .2000 on conflicting tags; simple stable
noise/slot/outlier families score 1.0. These are additional diagnostics, not
the preregistered holdout. No model was altered in response.

## Failure mechanisms and decisions

- Stationary tracking cannot determine referee permission in an identical-input
  pair. V3 strengthens D here and cannot be claimed to fix live pauses.
- Hidden opposite-endpoint gaps still use a midpoint prior, with ±5s error in
  early/late examples and unrecovered extra turnovers. No long ball trajectory
  was fabricated. Gap accuracy improvement is mostly D recognition, not timing.
- Fast controls remain vulnerable to integrated switch costs. The strong
  co-motion filter stays excluded; V3 does not lower synthetic short-control
  recall but external direct handover recall declines.
- Useful/incorrect tactical phase priors remain soft, max-pooled and explicitly
  mapped. The tiny balanced-suite no-tag advantage does not justify global removal.
- Development confidence-adaptive costs and shorter dwell minima gave no mean
  gain (.8420 each). A lower fixed cost gave .8595, but was not selected from
  artificial scores or tested/tuned on exposed new matches.

Focused evidence is in `dead_ball_failure_analysis.md`,
`missing_ball_turnover_analysis.md`, `machine_learning_feasibility.md` and
`final_failure_probes.json`. No unsupported claim that every real rapid possession
is preserved follows from these tests.

## Engineering verification and reproduction

71 tests pass, including all prior tests, deterministic learner/schema checks,
target-feature separation, V2-equivalent prepared inference, stationary-input
indistinguishability and V3 block isolation. The optional retraining CLI initially
exposed a missing Path import; it was corrected and rerun successfully to a
separate private file, with the original weight hash reproduced exactly.
All external ball indices and 40ms timestamps passed the independent alignment audit.

Two independent full-match V3 parses/inference runs passed the official CLI
validator and stricter exact-column/index validator. Both have exactly 199,319
rows indexed 0–199318, H/A/D/X only, X outside the published halves and D on all
2,934 required pre-kickoff frames. Output SHA-256:
`3a27d7d90657d1e4b9485007f0d7ea1d95ac662a64d4a3fbe5c1b50daf4ef534`. Run timing/memory and exact commit/input/model hashes
remain in `private/final_accuracy/candidate_verification.json`. Final post-commit
verification records the clean source revision. No original verification file
is replaced. Source hygiene excludes restricted assets and frame predictions.

```powershell
python -m pytest -q
python scripts/verify_final_candidate.py
```

See `docs/technical_report_v3.md` for single-run commands and external evaluation
reproduction. All six requested reports are supplied; original reports/PDFs stay
intact. Recommended candidate and residual risks are stated in
`final_model_recommendation.md`. No publication, submission or promotion occurred.
