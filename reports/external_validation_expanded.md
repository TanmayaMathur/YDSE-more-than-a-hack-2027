# Expanded external validation — 14 November 2026

Frozen V3 improves official spellF1 over V2 in all twelve tested views of two
new matches. This is evidence for the dead-ball change, not an estimate of the
competition score. Repeated corruptions are correlated views, not twelve matches.

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

Unweighted mean across these views: V1 0.3213, V2 0.3279,
V3 0.3786. This descriptive mean does not estimate deployment frequencies.
Evaluation took 341.4 seconds including XML parsing and local
prediction caching; it is not per-model inference timing.

## Data separation, alignment and licensing

Training/development is **J03WOH**, previously evaluated in the V2 investigation.
It is explicitly no longer untouched holdout. New matches were declared in
`research/final_accuracy/experiment_plan.json` before reading their tracking
outcomes. Candidate source, weights, config and stress generator were frozen
before evaluating either new match; no refit followed these results.

- J03WQQ: Fortuna Düsseldorf–FC St. Pauli, 142,345 frames, 401 reference spells.
  It shares one club with the development match; it is match-disjoint, not fully
  team-disjoint.
- J03WN1: VfL Bochum–Bayer Leverkusen, 141,561 frames, 500 reference spells;
  different teams/stadium from development. Both are 2022/2023, not Barcelona–Athletic.

Attribution: Manuel Bassek, Robert Rein, Hendrik Weber and Daniel Memmert (2025),
[Sportec/DFL dataset](https://doi.org/10.6084/m9.figshare.28196177.v1),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Primary Figshare
metadata verified the licence; all four downloads matched supplied size and MD5.
The external raw files stay outside Git. `final_external_alignment.json` verifies
every ball-frame index and every 40 ms timestamp step independently in each half;
both matches have zero unknown reference frames. Metadata determines home/away.
Centered metre coordinates become normalized coordinates using the 105×68 m pitch.
The [PySport Sportec deserializer](https://github.com/PySport/kloppy/blob/master/kloppy/infra/serializers/tracking/sportec/deserializer.py)
confirms BallStatus=1 means live and BallPossession=1/2 means home/away.

Only X/Y geometry and team IDs enter Tracking. BallStatus and BallPossession
are isolated scoring targets, never inference features. The model receives no
external event annotations or Smart Tagging. Disabling tactical priors on these
matches would be an identical-input check, not an informative tag ablation.

## Perturbations and additional metrics

Clean data has complete ball coordinates, so natural ball-dropout validation is
unavailable here. Burst seeds 1729/3253 use independent two-state missingness,
target fraction .41 and mean missing burst 40 frames. Actual fractions are in
the gap table. Coordinate noise is Gaussian 0.05 m standard deviation, added to
ball and players; it is a small jitter test, not realistic broadcast error.
Slot switches permute IDs within each team every 20 seconds. Combined uses
the separately preregistered seed 14027 for all three perturbations. No reference
labels guide corruption. Crowd-correlated occlusion, false detections and team
ID errors are not reproduced by this experiment.

| Match | Condition | V1 macroF1 | V2 macroF1 | V3 macroF1 | V3 alive/dead F1 |
| --- | --- | --- | --- | --- | --- |
| J03WQQ | clean | 0.6842 | 0.6866 | 0.8211 | 0.9307 |
| J03WQQ | burst1729 | 0.6550 | 0.6679 | 0.7753 | 0.9009 |
| J03WQQ | burst3253 | 0.6523 | 0.6676 | 0.7730 | 0.9010 |
| J03WQQ | coordinate_noise | 0.4747 | 0.4803 | 0.5949 | 0.7990 |
| J03WQQ | slot_switches | 0.6843 | 0.6839 | 0.8220 | 0.9314 |
| J03WQQ | combined | 0.4356 | 0.4591 | 0.6373 | 0.8241 |
| J03WN1 | clean | 0.6716 | 0.6764 | 0.8281 | 0.9493 |
| J03WN1 | burst1729 | 0.6133 | 0.6283 | 0.7705 | 0.9035 |
| J03WN1 | burst3253 | 0.6192 | 0.6391 | 0.7641 | 0.9005 |
| J03WN1 | coordinate_noise | 0.4924 | 0.5187 | 0.6074 | 0.7613 |
| J03WN1 | slot_switches | 0.6716 | 0.6733 | 0.8291 | 0.9504 |
| J03WN1 | combined | 0.4111 | 0.4741 | 0.6162 | 0.7780 |

## Actual possession and boundary errors

| Match | Model | False D / live | Missed D / D | D onset F1 ±1s | D exit F1 ±1s | Spurious spells @.5 | Missed spells @.5 | Excess long-spell fragments |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J03WQQ | v2 | 0.0017 | 0.5402 | 0.1455 | 0.4049 | 182 | 242 | 5 |
| J03WQQ | v3 | 0.0075 | 0.2039 | 0.4623 | 0.6091 | 157 | 223 | 6 |
| J03WN1 | v2 | 0.0020 | 0.4365 | 0.2359 | 0.4021 | 208 | 363 | 2 |
| J03WN1 | v3 | 0.0081 | 0.0914 | 0.6066 | 0.5837 | 124 | 324 | 2 |

False/missed D are conditional frame error rates. Spurious/missed possessions
use the official one-to-one same-team IoU=.5 matching. Long spells are ≥10s;
the fragmentation count measures additional overlapping same-team predicted
spells, not all possible false splits. Boundary F1 uses a ±1s tolerance.

| Match | Model | Recall <1s | Recall <2s | Recall <3s | Direct H↔A recall ±1s |
| --- | --- | --- | --- | --- | --- |
| J03WQQ | v2 | 0.0000 | 0.0099 | 0.0452 | 0.2947 |
| J03WQQ | v3 | 0.0000 | 0.0297 | 0.0710 | 0.2881 |
| J03WN1 | v2 | 0.0132 | 0.0234 | 0.0420 | 0.2487 |
| J03WN1 | v3 | 0.0263 | 0.0526 | 0.0882 | 0.2183 |

Short recall uses same-team IoU=.5, so imprecise short boundaries are penalized.
Reference counts for <1/<2/<3s are 37/101/155 (WQQ), 76/171/238 (WN1).
V3 improves aggregate short-spell recall, but it remains poor. Clean short spells
previously matched by V2 were not lost at this threshold; V3 gains 4 and 11
additional <3s matches. Direct H↔A recall nevertheless falls: WQQ loses 3 and
gains 1 matched handover; WN1 loses 13 and gains 1. In 3/3 and 5/13 lost cases,
V3 predicts D within one second. Other losses can reflect boundary displacement
or changed one-to-one matching. These are real regressions, not erased by the
higher spellF1. No correction was tuned on these matches.

| Match | Condition | Missing fraction | V2 gap accuracy | V3 gap accuracy | Hidden handovers | V2 hidden recall ±1s | V3 hidden recall ±1s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J03WQQ | burst1729 | 0.4029 | 0.6494 | 0.7300 | 125 | 0.1040 | 0.0880 |
| J03WQQ | burst3253 | 0.4004 | 0.6422 | 0.7219 | 131 | 0.1221 | 0.1145 |
| J03WQQ | combined | 0.4105 | 0.5008 | 0.6479 | 114 | 0.1491 | 0.1404 |
| J03WN1 | burst1729 | 0.4026 | 0.5789 | 0.7349 | 143 | 0.0699 | 0.0490 |
| J03WN1 | burst3253 | 0.4007 | 0.5996 | 0.7297 | 155 | 0.0581 | 0.0516 |
| J03WN1 | combined | 0.4088 | 0.4374 | 0.6090 | 171 | 0.0936 | 0.0994 |

Gap frame accuracy improves, mainly through D recognition. Hidden handover
recall falls in five of these six views; improvement in gap accuracy is not
evidence of better hidden-turnover timing. The combined WN1 view is the exception.

## Uncertainty and definition mismatch

| Match | Condition | Exploratory paired V3−V2 95% range |
| --- | --- | --- |
| J03WQQ | clean | [0.0350, 0.0762] |
| J03WQQ | burst1729 | [0.0236, 0.0680] |
| J03WQQ | burst3253 | [0.0209, 0.0604] |
| J03WQQ | coordinate_noise | [0.0109, 0.0457] |
| J03WQQ | slot_switches | [0.0367, 0.0776] |
| J03WQQ | combined | [0.0150, 0.0524] |
| J03WN1 | clean | [0.0687, 0.1170] |
| J03WN1 | burst1729 | [0.0518, 0.0941] |
| J03WN1 | burst3253 | [0.0534, 0.0940] |
| J03WN1 | coordinate_noise | [0.0013, 0.0242] |
| J03WN1 | slot_switches | [0.0683, 0.1166] |
| J03WN1 | combined | [0.0017, 0.0205] |

These are 1,000 paired resamples of shared reference spells using fixed prediction
counts, seed 20261114, following the existing scorer-style helper. Within-match
spell dependence, common teams, shared provider, clean tracking and label
conventions remain unaccounted for. They are exploratory ranges, not match-level
or competition confidence intervals. No broad significance claim follows.
DFL provider ownership may retain or change possession differently through
deflections, aerials and contested periods than Metrica's controlled-possession
definition. Its status flags also supply a different stoppage-reference process.
All results are against those provider references, without hand reannotation.

Recommendation: retain the frozen blend as the strongest current candidate for
review, while explicitly tracking increased false D and lost direct handovers.
Do not calibrate on these now-exposed evaluation targets. Raw predictions remain
local; aggregate results are in `external_validation_expanded.json` and
`final_external_error_analysis.json`. Reproduce in a fresh evaluation output
location/check-out; the evaluator refuses to overwrite its recorded outcomes.
