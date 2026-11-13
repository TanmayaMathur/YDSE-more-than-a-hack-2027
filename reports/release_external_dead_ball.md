# Release audit: existing external prediction error accounting

No new model, fitting, calibration, parameters or match selection. These are
**already examined** J03WQQ/J03WN1 evaluation outputs; they are not untouched
future holdouts. J03WOH is training/development and is excluded from independent
evidence. Raw arrays and detailed diagnostics stay private.

| Match | Condition | Model | D precision | D recall | False D seconds | Predicted H/A spells | Fragmented true spells | Excess fragments | Interior false D runs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J03WQQ | clean | v2 | 0.9948 | 0.4598 | 5.60 | 341 | 5 | 5 | 0 |
| J03WQQ | clean | v3 | 0.9864 | 0.7961 | 25.40 | 335 | 5 | 6 | 1 |
| J03WQQ | burst1729 | v2 | 0.9903 | 0.4353 | 9.84 | 275 | 3 | 3 | 0 |
| J03WQQ | burst1729 | v3 | 0.9627 | 0.7136 | 64.08 | 276 | 7 | 8 | 5 |
| J03WQQ | burst3253 | v2 | 0.9933 | 0.4378 | 6.88 | 288 | 4 | 4 | 0 |
| J03WQQ | burst3253 | v3 | 0.9746 | 0.7027 | 42.44 | 288 | 4 | 5 | 2 |
| J03WQQ | coordinate_noise | v2 | 0.9760 | 0.0814 | 4.64 | 314 | 5 | 5 | 0 |
| J03WQQ | coordinate_noise | v3 | 0.9927 | 0.2710 | 4.60 | 331 | 5 | 5 | 0 |
| J03WQQ | slot_switches | v2 | 0.9947 | 0.4538 | 5.60 | 342 | 5 | 5 | 0 |
| J03WQQ | slot_switches | v3 | 0.9865 | 0.7985 | 25.44 | 334 | 5 | 6 | 1 |
| J03WQQ | combined | v2 | 0.9929 | 0.0697 | 1.16 | 262 | 4 | 4 | 0 |
| J03WQQ | combined | v3 | 0.9866 | 0.3864 | 12.20 | 292 | 3 | 3 | 0 |
| J03WN1 | clean | v2 | 0.9967 | 0.5635 | 5.52 | 345 | 4 | 4 | 0 |
| J03WN1 | clean | v3 | 0.9917 | 0.9086 | 22.28 | 300 | 4 | 4 | 0 |
| J03WN1 | burst1729 | v2 | 0.9943 | 0.4990 | 8.40 | 316 | 2 | 2 | 0 |
| J03WN1 | burst1729 | v3 | 0.9784 | 0.8224 | 53.20 | 278 | 3 | 3 | 1 |
| J03WN1 | burst3253 | v2 | 0.9926 | 0.5231 | 11.48 | 303 | 2 | 2 | 0 |
| J03WN1 | burst3253 | v3 | 0.9755 | 0.8187 | 60.08 | 271 | 3 | 3 | 1 |
| J03WN1 | coordinate_noise | v2 | 0.9950 | 0.2503 | 3.68 | 324 | 4 | 4 | 0 |
| J03WN1 | coordinate_noise | v3 | 0.9953 | 0.4174 | 5.80 | 321 | 4 | 4 | 0 |
| J03WN1 | slot_switches | v2 | 0.9966 | 0.5567 | 5.52 | 344 | 4 | 4 | 0 |
| J03WN1 | slot_switches | v3 | 0.9916 | 0.9110 | 22.52 | 300 | 4 | 4 | 0 |
| J03WN1 | combined | v2 | 0.9976 | 0.2017 | 1.40 | 303 | 2 | 2 | 0 |
| J03WN1 | combined | v3 | 0.9923 | 0.4726 | 10.80 | 312 | 2 | 2 | 0 |

D precision = TP_D/(TP_D+FP_D); D recall = TP_D/(TP_D+FN_D). False-positive
duration = FP_D/25, counting provider H/A frames predicted D. Unknown reference
frames are excluded (both matches have zero). Predicted spells and fragmentation
use maximal same-team H/A intervals. A true spell is fragmented when two or more
same-team predicted spells overlap it; excess fragments sum overlap_count-1.
All true spell lengths are included here, unlike the earlier report's >=10s
fragmentation statistic. Interior false-D runs lie strictly inside a true H/A
spell; D at a spell boundary is truncation, not an interior split. These simple
overlap diagnostics are not a replacement for official IoU spellF1 matching.
No true H/A spell crosses either concatenated half join.

On clean WQQ, fragmented true spells remain 5, but excess fragments grow 5->6
and one interior false-D run appears; true spells touched by any false D rise
15->66. On clean WN1, fragmented spells remain 4 and excess fragments remain 4,
but touched spells rise 37->91. Thus unchanged fragmentation counts can hide
boundary truncation. Dropout WQQ seed 1729 shows the largest fragmentation cost:
excess fragments 3->8, five interior false-D runs. Some earlier long-spell-only
counts are smaller by definition.

Existing official spellF1 V2->V3: clean WQQ .4248->.4799, WN1 .3318->.4235;
all twelve views improve. Existing direct-handover recall nevertheless falls
.2947->.2881 and .2487->.2183 on clean inputs, and hidden-handover recall falls
in five of six dropout/combined views. Short-spell recall remains weak. No
adjustment was made in response. Provider ownership/status semantics, complete
clean ball observations, one shared club with training and correlated artificial
corruptions limit transfer to Metrica automatic tracking. These are external
references, not competition human truth or a hidden-score estimate.

Sources: prior `external_validation_expanded.json`, fixed local prediction caches,
`scripts/release_readiness_audit.py`, `final_external_error_analysis.json`.
Data attribution: Bassek, Rein, Weber and Memmert (2025),
[Sportec/DFL dataset, CC BY 4.0](https://doi.org/10.6084/m9.figshare.28196177.v1).
