# Accuracy audit - YDSE, 14 November 2026

Starting commit `8b184b0c626e108679b97a344ef06a661f860d5b` had a clean working tree. The audit runs on
`accuracy-improvement`; V1 source remains on the original branch. Its CSV hash
matches `45e91b5246b6a05db7f8b5e034185e0bbd4cf6eab7c9dcc2e4b4d027f369ae35`. CSV, PDF, Markdown, release metadata/run metadata and official
smooth50 fallback were copied to a private preservation directory and hash-checked.

## Outcome

The audit found real implementation weaknesses, not an alignment or team-label reversal.
The separate V2 candidate fixes boundary leakage, weak-data confidence promotion,
duplicate observation counting, noisy player-speed bias and ambiguous tactical semantics.
It adds a deliberately weak, two-sided ownership timing prior for invisible turnovers.
The original durations/costs remain fixed; the original V1 inference modules are unchanged.

V2 passed two complete 199,319-frame executions, official/strict schema checks,
byte equality, graded-boundary checks and the published second-half D block. Its SHA-256
is `79d4552782eebc37995ccb8603a091518dd45dbcb33cdb7ac93daca714d01f00`. V1 and all protected metadata/PDF/fallback artifacts remain unchanged.

57 tests passed (including exact decoder objective, noise/coverage, duplicate, semantic,
boundary and external target-separation tests); compileall passed. There were 64 development
and 128 frozen holdout scenarios across 16 families and 11 configurations. A stronger
co-motion filter was rejected before holdout because it erased genuine rapid control.

One independent CC BY 4.0 other match was evaluated without fitting any parameters.
V2 point estimates improved slightly on clean tracking and two independent dropout
realizations; two exploratory intervals include zero. See external_validation.md for
actual numbers and limitations. Synthetic gains alone did not determine the recommendation.

## Highest-priority findings

1. V1 rolling features cross ungraded boundaries even though its DP resets. A constructed
   ungraded-only edit changed the graded slow feature by .6378. V2 scopes all operations.
2. One stationary player received full collective-stillness evidence; a .01-confidence
   repaired ball received the same stationary score as a real observation. V2 gates
   coverage and preserves reliability continuously.
3. First-difference norm magnifies coordinate noise. V2 uses a short supported displacement
   estimate for collective motion, with tests on known stationary and moving trajectories.
4. V1 broadly interprets defensive transitions and box occupation as ownership. V2 uses
   an explicit weaker/neutral semantic map and bounded pooling. Wrong primary tags remain risky.
5. A hidden turnover has an uncertainty interval, not a known frame. V1 can choose the
   first invisible frame by tie; V2's midpoint tendency is an explicit prior, not reconstruction.
6. Exact DP checks found no optimization bug for the stated energy/minimum-duration model.
   This does not validate its manually chosen costs or feature scales as football-optimal.

## Remaining failure analysis

Both versions misclassify an exact noiseless stationary live pause as dead. Identical
tracking can describe a real whistle, so this cannot be solved universally by geometry.
Moving-after-foul stoppages can also be missed. The dead terms are correlated scores,
not independent calibrated likelihoods. No learned LIVE/DEAD posterior is claimed.

Short weak controls, unseen multiple turnovers, aerial interactions and incorrect long
primary phases remain hard. A no-tags model wins the deliberately adversarial synthetic
mix, but that mix disproportionately supplies wrong/ambiguous tags; this is not evidence
to remove all tags on real football. Timing priors can place hidden turnovers wrongly.

Local match diagnostics reproduce both exact CSVs. Per-transition reliability, component
scores, costs, prior-state ages and dropout/tag indicators are kept in private JSON files.
Only aggregate statistics are public: V1/V2 have 362/365
predicted possessions and 90/101 D segments.
Those numbers are not used as targets. Seven of 59 restart windows meet all strict
conditions; most rejected anchors lack the motion pattern or quiet corroboration.

## Official guidance, evidence and decision

Recheck found zero accessible open or closed issues and no accessible PR conversations.
PR listing and issue comments returned 404; commit-comment fallback returned zero;
Discussions are disabled. Official HEAD remains f8f2629. No discussion was invented.
Metric semantics, threshold matching, X propagation and the 2,934-frame D block were
verified against actual official source and independently constructed scorer examples.

Recommend V2 for engineering review because the fixes are demonstrated and frozen external
point estimates are favorable. **Do not claim higher competition accuracy or automatically
replace V1.** Broad superiority is unestablished; preserve both and explicitly review risk
before choosing the upload. No prohibited annotations, public-window tuning, manual prediction
edits, hosted restricted-data disclosure, publication or competition upload occurred.

Detailed source-by-source audit: research/accuracy_audit/implementation_audit.md.
Reproduce safely with `.venv\Scripts\python scripts/verify_accuracy_candidate.py`.
