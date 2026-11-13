# Source-level competitor analysis

401 relevant candidates in the inventory; seven implementations deeply inspected. Others are metadata leads, not assessed solutions. No stars/fork counts or public-window scores are used to rank quality.

## darfattt/mtah-2027-possession
VERIFIED source snapshot: [bc02777ba17f85da2178b575dcbf676f9efd96c6](https://github.com/darfattt/mtah-2027-possession/tree/bc02777ba17f85da2178b575dcbf676f9efd96c6); 1 total reachable commits (includes upstream where applicable).
- Implemented: Nearest-player baseline with optional linear gap repair; majority vote; separate Viterbi utility.
- Missing ball: Optional bounded interpolation; no uncertainty in inferred ball positions.
- Smart Tagging: Soft prior helpers exist, but baseline CLI does not fuse them.
- Dead ball: No separate dead-ball model in baseline path.
- Temporal model: Majority vote used; generic Viterbi implemented but not wired into baseline.
- Confidence: No calibrated confidence.
- Completeness: Runnable starter-level implementation; not an advanced model. Cost: Low, NumPy.
- Actual verification: 12 synthetic tests executed and passed.
- PLAUSIBLE limitations: Normalised-coordinate nearest distance lacks pitch-axis scaling. Smoother votes D and uses a different window convention than upstream despite equivalence claims.
- [Inspected algorithm](https://github.com/darfattt/mtah-2027-possession/blob/bc02777ba17f85da2178b575dcbf676f9efd96c6/src/possession/baseline.py). Licence metadata is in competitor_inventory.csv; NOASSERTION/Unknown is not reuse permission. No source/weights/predictions were reused. Comparable full-match performance: Unknown.

## DivyanshAfk/mtah-2027-possession
VERIFIED source snapshot: [9ec1c218759fdc15e6057240726f0003a56b4ae1](https://github.com/DivyanshAfk/mtah-2027-possession/tree/9ec1c218759fdc15e6057240726f0003a56b4ae1); 8 total reachable commits (includes upstream where applicable).
- Implemented: Control-proximity evidence, separate dead mask, two-state minimum-cost decoding per live run.
- Missing ball: Neutral team evidence in gaps; separate experimental gradient-boosted ball regressor is not used in v1.
- Smart Tagging: Restart windows used by dead mask.
- Dead ball: Fixed restart padding plus player stillness and ball-outside rules.
- Temporal model: Two-state Viterbi with constant switch penalty.
- Confidence: Near/far distance weights; fast-ball evidence suppressed.
- Completeness: Complete v1 source present; full-match execution not independently run. Cost: Low for v1; higher for optional sklearn ballfill.
- Actual verification: No tests directory discovered in reviewed source; not executed.
- PLAUSIBLE limitations: Fixed restart spans can mask live play; long no-evidence live runs can inherit weak endpoints. Ballfill claim is author-reported, not independently reproduced.
- [Inspected algorithm](https://github.com/DivyanshAfk/mtah-2027-possession/blob/9ec1c218759fdc15e6057240726f0003a56b4ae1/src/v1.py). Licence metadata is in competitor_inventory.csv; NOASSERTION/Unknown is not reuse permission. No source/weights/predictions were reused. Comparable full-match performance: Unknown.

## ArmicZeroGTRS/more-than-a-hack-2027
VERIFIED source snapshot: [36c91dd4bebbdf1819f51d558dee3bf17508b2dd](https://github.com/ArmicZeroGTRS/more-than-a-hack-2027/tree/36c91dd4bebbdf1819f51d558dee3bf17508b2dd); 11 total reachable commits (includes upstream where applicable).
- Implemented: Proximity/contact/density scores, collective stillness and three-state decoding.
- Missing ball: Neutral ownership; dead evidence needs static teams.
- Smart Tagging: Weak set-piece mask.
- Dead ball: Ball static/outside plus team motion.
- Temporal model: Three-state Viterbi followed by short-run merging and dead bridging.
- Confidence: Physical scores and temperature; calibration unknown.
- Completeness: Complete source path present; Windows portability limitation observed. Cost: Low, NumPy.
- Actual verification: 15/16 self-checks passed after supplying omitted organiser helpers; one cross-drive failure.
- PLAUSIBLE limitations: Post-hoc minimum spell repair can remove real short possessions. A synthetic end-to-end test fails on Windows when temp and repository are on different drives (os.path.relpath).
- [Inspected algorithm](https://github.com/ArmicZeroGTRS/more-than-a-hack-2027/blob/36c91dd4bebbdf1819f51d558dee3bf17508b2dd/src/model.py). Licence metadata is in competitor_inventory.csv; NOASSERTION/Unknown is not reuse permission. No source/weights/predictions were reused. Comparable full-match performance: Unknown.

## aditwidi/more-than-a-hack-2027-team-nexus
VERIFIED source snapshot: [2cdb4e2b319288cf471aa200a333186529a04568](https://github.com/aditwidi/more-than-a-hack-2027-team-nexus/tree/2cdb4e2b319288cf471aa200a333186529a04568); 12 total reachable commits (includes upstream where applicable).
- Implemented: Top-three team control margin, multi-scale evidence and formation fallback.
- Missing ball: Interpolated ball and formation fallback.
- Smart Tagging: Defensive polarity implemented.
- Dead ball: Ball absence, motion, stationary ball and restart features.
- Temporal model: Asymmetric three-state Viterbi plus iterative minimum-duration cleanup.
- Confidence: Emission weights; real calibration unknown.
- Completeness: Complete feature/emission/decoder source present. Cost: Low, NumPy.
- Actual verification: Tests present; not executed.
- PLAUSIBLE limitations: emissions.py comments explicitly describe changes chosen from public-window outcomes. Those scores/choices are excluded from our model selection; this is a provenance concern, not an organiser ruling.
- [Inspected algorithm](https://github.com/aditwidi/more-than-a-hack-2027-team-nexus/blob/2cdb4e2b319288cf471aa200a333186529a04568/pipeline/emissions.py). Licence metadata is in competitor_inventory.csv; NOASSERTION/Unknown is not reuse permission. No source/weights/predictions were reused. Comparable full-match performance: Unknown.

## hnfadtya/more-than-a-hack-2027
VERIFIED source snapshot: [6f15add056f5b937e5154295fb70e21ebf82ed9f](https://github.com/hnfadtya/more-than-a-hack-2027/tree/6f15add056f5b937e5154295fb70e21ebf82ed9f); 17 total reachable commits (includes upstream where applicable).
- Implemented: Permutation-invariant set Transformer, dilated temporal convolutions and bidirectional GRU.
- Missing ball: Burst dropout, crowd/air-aware corruption and masks for external training.
- Smart Tagging: No tag fusion verified in inspected inference path.
- Dead ball: Learned H/A/D output head.
- Temporal model: Minimum-duration sequence decoding after windowed neural probabilities.
- Confidence: Neural probabilities; independent calibration unknown.
- Completeness: Training and inference code present; trained performance not reproduced. Cost: Higher, PyTorch.
- Actual verification: Decoder tests present; not executed (PyTorch not installed).
- PLAUSIBLE limitations: External training and compatible weights/GPU dependencies must be reproduced; domain transfer to automatic tracking remains uncertain.
- [Inspected algorithm](https://github.com/hnfadtya/more-than-a-hack-2027/blob/6f15add056f5b937e5154295fb70e21ebf82ed9f/mtah/model.py). Licence metadata is in competitor_inventory.csv; NOASSERTION/Unknown is not reuse permission. No source/weights/predictions were reused. Comparable full-match performance: Unknown.

## yassintamer91/more-than-a-hack-2027
VERIFIED source snapshot: [906ec8da2e52b1e0c1ade42cd4eca297c0674a2f](https://github.com/yassintamer91/more-than-a-hack-2027/tree/906ec8da2e52b1e0c1ade42cd4eca297c0674a2f); 7 total reachable commits (includes upstream where applicable).
- Implemented: Control-aware structured evidence, motion-localized restarts, optional externally trained stoppage logistic model.
- Missing ball: Gap confidence and explicit unsupported-evidence handling.
- Smart Tagging: Phase/restart votes clipped; no midpoint anchor when localization fails.
- Dead ball: Collective motion plus stationary/outside ball; optional learned stop head.
- Temporal model: Structured dynamic temporal inference; specialist modules.
- Confidence: Reliability and availability gates; calibration not independently measured.
- Completeness: Substantial source and tests present; inspected core not independently run. Cost: Low core; optional video higher.
- Actual verification: Many synthetic tests present; not executed.
- PLAUSIBLE limitations: Optional video and external-model routes require separate reproduction; real-match superiority unverified.
- [Inspected algorithm](https://github.com/yassintamer91/more-than-a-hack-2027/blob/906ec8da2e52b1e0c1ade42cd4eca297c0674a2f/solution/structured.py). Licence metadata is in competitor_inventory.csv; NOASSERTION/Unknown is not reuse permission. No source/weights/predictions were reused. Comparable full-match performance: Unknown.

## 4139benuzter/mtah2027-mas-bueno
VERIFIED source snapshot: [3928dd3d20ad1d69d0ef17fc0f40e1e73467ca50](https://github.com/4139benuzter/mtah2027-mas-bueno/tree/3928dd3d20ad1d69d0ef17fc0f40e1e73467ca50); 10 total reachable commits (includes upstream where applicable).
- Implemented: Touch/control episodes, restart kick boosts and three-state scores.
- Missing ball: Formation logit and optional broadcast ball fill.
- Smart Tagging: Set-piece restart candidate windows and phase evidence.
- Dead ball: Stillness, outside pitch, restart cues and onset snapping.
- Temporal model: Viterbi plus short-dead merging and onset snapping.
- Confidence: Rule-based probability/score gates.
- Completeness: Complete core and optional broadcast source present. Cost: Low core; optional matching higher.
- Actual verification: No tests directory in reviewed tree; not executed.
- PLAUSIBLE limitations: Broadcast alignment uses match-specific offset hints rather than a fresh global search. Snapping and short-dead rules can erase brief real events.
- [Inspected algorithm](https://github.com/4139benuzter/mtah2027-mas-bueno/blob/3928dd3d20ad1d69d0ef17fc0f40e1e73467ca50/possession/model.py). Licence metadata is in competitor_inventory.csv; NOASSERTION/Unknown is not reuse permission. No source/weights/predictions were reused. Comparable full-match performance: Unknown.

## Opus Operandi
VERIFIED public organisation profile describes a possession engine, external benchmark and visible/missing-ball specialists. The two advertised implementation repositories return 404 and are not in public organisation enumeration. Architecture is therefore an UNVERIFIED implementation claim; code, weights, tests, licence and performance are Unknown. [Profile](https://github.com/Opus-Operandi-FC-Barcelona/.github/blob/main/profile/README.md).

## Search coverage
Twenty repository queries produced 764 deduplicated search/lead records before fork union. Queries cover alternate titles, MTAH, spellF1, BAR-ATH, possession filenames and generic tracking. Code search spellF1 language:Python was paginated, yielding 375 metadata records. Search is index-dependent and mutable; some broad queries were limited to the first 100 results. No claim of finding every participant is made. Private/unindexed implementations remain inaccessible.
