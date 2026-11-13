# Scientific methods and implementation decisions

| Source and access | Key idea | Compatibility and risk | Effort | Implemented |
|---|---|---|---|---|
| [Yu, Hidden semi-Markov models, 2010](https://www.cs.ubc.ca/~murphyk/Teaching/CS540-Spring10/projects/Yu-hsmm09.pdf), actual paper accessed | State durations can be modeled with expanded states or explicit-duration recurrences | Suitable for offline H/A/D paths; duration assumptions can remove brief true states | Medium | Expanded-state minimum dwell and transition energy; no EM or learned duration distribution |
| [Automatic event detection in football using tracking data](https://link.springer.com/article/10.1007/s12283-022-00381-6), methods inspected | Proximity alone does not establish contact; trajectory changes and continuation matter | Useful control features; its missing-ball/dead trigger assumes provider behavior that does not hold for this ATD | Medium | Confidence from proximity, relative motion and flight; missing=dead explicitly rejected |
| [MS-TCN, Abu Farha and Gall, CVPR 2019](https://arxiv.org/abs/1903.01945), author abstract accessed; CVF page blocked | Temporal context and smoothing loss address over-segmentation | A supervised network needs independent legal labels and transfer testing | High | No TCN trained; segmentation principle informs temporal decoding |
| [Using Temporal Convolutional Networks to estimate ball possession in soccer games](https://www.sciencedirect.com/science/article/pii/S0957417423002816), publisher abstract found; full page returned 403 | Separate alive/dead and ownership predictions; permutation-invariant object embeddings | Closely related; confidential source data and no verified reusable weights | High | Separate physical evidence combined in one three-state decoder; no claimed replication |
| [Semi-automated last-touch detection, Wang et al., 2025](https://dspace.mit.edu/entities/publication/0e674d32-b06a-4ea6-80bc-46f94a2be540), institutional abstract accessed | Touch probability plus context supports out-of-bounds decisions | Skeletal tracking unavailable; last touch differs from controlled possession | High | Not implemented |

VERIFIED sources support the stated high-level ideas. PLAUSIBLE transfer benefits
remain unmeasured. No external annotated match, pretrained model, API or human
annotation was used for training. Kalman extrapolation and learned ball-location
regression were considered but not implemented: long occlusions and discontinuous
ball flights make precise extrapolation hard to justify without independent tests.

Tests use procedural football-like sequences and exact dynamic-programming checks.
They verify expected mechanisms; their simplified geometry is not representative
enough to estimate the hidden competition score.
