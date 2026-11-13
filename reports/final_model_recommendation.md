# Final model recommendation

Recommend **the frozen V3 blend for team review as the strongest current
candidate on the ranking metric**. Keep the submission of record unchanged
until the team approves a final choice. Two new other-match evaluations support
V3, but do not establish a hidden competition score or uniform superiority.

| Criterion | V1 | V2 | V3 |
|---|---|---|---|
| Rule/provenance path | Algorithmic geometry, no same-game labels | Same, audited confidence and tags | Same restrictions; public external labelled training with attribution |
| Exact CSV and deterministic full runs | Preserved PASS | Preserved PASS | Two full runs PASS, identical bytes |
| New clean WQQ spellF1 | .4243 | .4248 | .4799 |
| New clean WN1 spellF1 | .3334 | .3318 | .4235 |
| Twelve-view mean spellF1 | 0.3213 | 0.3279 | 0.3786 |
| New synthetic holdout | .8253 | .8531 | .8531 |
| Stationary-live ambiguity | Unsolved | Unsolved | Unsolved; stronger D prior |
| Hidden-turnover timing | Early tie/persistence risk | Weak midpoint prior | Same midpoint risk; no timing fix |
| Short controlled possessions | Often missed | Often missed | Same synthetic recall; higher clean provider short-spell recall, lower direct-handover recall |
| Complexity | Small deterministic pipeline | Additional confidence/semantic logic | 18-feature CPU head and a 2.5KB JSON parameter file added |

Clean WQQ/WN1 gains are +.0551/+.0917 spellF1. The smallest of twelve gains is
+.0108 (WN1 combined dropout/noise). V3 reduces missed genuine D and improves
dead boundaries but increases false D/live, from .17% to .75% and .20% to .82%
on the clean matches. Direct H↔A recall falls from .2947 to .2881 and .2487 to
.2183. Five of six dropout/combined views regress on hidden handover recall.
No candidate can be called best on
every failure type. The higher ranking-metric evidence favors V3 despite those
documented costs; if the team places extra weight on false-D conservatism,
V2 remains the simpler fallback.

New evidence is only two provider-specific matches; one shares a club with the
training match. Repeated corruptions are correlated, real crowd-related missingness
is not recreated, and Smart Tagging is absent externally. Official hidden-match
performance and superiority over competitors remain unknown. Remaining poor
short-spell recall and unidentifiable gap histories limit football conclusions.
Do not retune on these now-exposed evaluation matches; further model selection
requires a new reserved match or properly separated development data.

V3 CSV: `submission/candidates/YDSE_v3.csv`; reproduced copy beside it.
SHA-256: `3a27d7d90657d1e4b9485007f0d7ea1d95ac662a64d4a3fbe5c1b50daf4ef534`.
Canonical learned-parameter SHA-256:
`0562bf7f6850030346193e88484439b7aa8e0ffb05d273ec035c76e9cd18e4dd`.
The exact model/config and method are in `docs/technical_report_v3.md`.
V1/V2 artifacts and original technical documents remain byte-identical.

Readiness: technically validated local candidate with reproducible source and
documented training data. Outstanding participant decisions are signed enrolment
terms verification, final candidate approval, exact deadline/delivery instructions,
and whether/when to publish or submit. The Drive invitation is not consent to
hosted processing or redistribution. No external publication, submission or
automatic promotion was performed.
