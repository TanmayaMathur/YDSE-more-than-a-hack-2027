# Techniques reviewed for the accuracy audit

No competitor predictions, weights or copied solution code enter this candidate.
Source inspections are hypotheses, not evidence of a higher competition score.

| Source | Inspected mechanism | Audit decision |
|---|---|---|
| [yassintamer91/solution/stoppage.py](https://github.com/yassintamer91/more-than-a-hack-2027/blob/906ec8d/solution/stoppage.py) | External-data regularized logistic dead/live head; unavailable evidence is neutral | Useful design precedent for future external calibration. No weights reused and no same-game calibration performed. |
| [hnfadtya/mtah/augment.py](https://github.com/hnfadtya/more-than-a-hack-2027/blob/6f15add/mtah/augment.py) | Bursty ball/player dropout and corruption of other-match tracking | Independent external validation uses its own simple label-independent Markov dropout, not competitor predictions or tuned values. |
| [PathCRF official source](https://github.com/hyunsungkim-ds/pathcrf), [paper](https://arxiv.org/abs/2602.12080) | Set-attention player interactions plus CRF paths; checkpoints and other-match training workflow advertised | Potential missing-ball specialist, but player-level edge paths require identity/continuity adaptation for anonymous slots. Not inserted or claimed reproduced. |
| [Automatic event detection methods](https://arxiv.org/abs/2202.00804) | Proximity plus changes in speed/direction to distinguish control from passing contact | Supports testing control persistence. Stronger co-motion filtering was tested and rejected after erasing true rapid controls. |
| [SkillCorner official data](https://github.com/SkillCorner/opendata) | Ten other matches, automatic ownership and phases, MIT repository licence | Accessible independent proxy, but automatic/provider-specific labels are not equivalent to manually corrected H/A/D truth. Not claimed as gold evaluation. |
| [Metrica sample data](https://github.com/metrica-sports/sample-data) | Synchronized other-match tracking and events | Public examples are useful, but README gives attribution guidance without a clearly verified continuous possession-label contract. No synthetic truth reconstructed from gaps/events for validation. |
| [Bassek et al. Sportec/DFL dataset](https://springernature.figshare.com/articles/dataset/28196177) | CC BY 4.0 data from seven other matches; BallStatus and BallPossession frame attributes | One preselected independent match is evaluated separately, with raw and label-independent corrupted ball observations. See frozen external plan and actual validation report. |

Targeted video inference was investigated as a possible independent sensor. A small
football ball detector would need verified weights/licence, pixel/pitch association,
occlusion rejection and local-only inference. A frame cannot be treated as out of play
just because a detector misses the ball. No suitable tested detector was inserted;
full-video processing and unvalidated visual labels would sacrifice a working candidate.

The selected P2 experiment is independent external tracking validation. No competition
video, XML, tracking or derivative is uploaded to any service. External datasets are
other matches only, with provenance checked before evaluation. Neither external nor
synthetic outcomes may trigger tuning after the recorded candidate freeze.
