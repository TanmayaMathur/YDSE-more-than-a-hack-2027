# YDSE — More Than a Hack 2027, Phase 1

This document describes preserved Version 1. The separate audited candidate is
documented in [technical_report_v2.md](technical_report_v2.md). The original PDF
and submitted-file candidate have not been overwritten.

## Task and data provenance

YDSE predicts Barcelona possession (`H`), Athletic Club possession (`A`), dead ball
(`D`) or abstention (`X`) for each of 199,319 tactical video frames at 25 FPS.
Possession persists through loose balls and deflections until evidence supports
opposing control. A dead-ball interval splits two possessions even if the same
team restarts. Official constants and utilities define frame alignment and halves.

Inputs are the licensed **automatic tactical ATD metadata/raw tracking and Smart
Tagging**. Nine supplied assets were identified and checked locally; broadcast
tracking/homographies and both videos were preserved but do not enter inference.
Broadcast has a separate timeline, and no unsupported offset is assumed. Homography
is unnecessary when working entirely in pitch coordinates.

No supervised training, external labelled matches, pretrained models or human
annotations were used. Neither the public five-minute labels nor any competitor's
predictions/scores select, train or tune the model. The official evaluation demo
ran once on the shipped baseline files to check scorer execution. All match inputs
are processed locally; no restricted frames, coordinates or tags were disclosed
to hosted AI services. Signed participation terms remain for the team to verify.

## Parsing and trajectory reliability

The parser enforces complete, contiguous ATD records with `video_frame = frame_id - 1`.
It checks slot counts, numeric schema and team membership. Slots are anonymous
tracklets, not stable player identities. Positions are converted from normalized
coordinates to metres using the official 105.3 × 68.0 m pitch dimensions.

Ball repair rejects an isolated implausible spike only if the surrounding samples
are mutually plausible. Linear interpolation requires observed endpoints, a gap
of at most 0.8 s, and implied speed at most 45 m/s. It never extrapolates leading,
trailing or long gaps and never crosses a half boundary. Interpolated reliability
is below observed reliability and decreases with gap duration. Long gaps retain
no invented ball position.

Player and ball velocities are recomputed from coordinates. Player jumps above
12 m/s are discarded as unreliable, reducing sensitivity to slot reassignment.
The collective median speed is smoothed robustly. These are engineering bounds,
not parameters fitted to labels from this match.

## Evidence fusion

Team evidence uses the difference between nearest home/away distances, local
player density and approach motion. Reliability depends on ball observation,
distance to the nearest player, tracked-player coverage, ball flight speed and
relative player–ball velocity. A fast ball near an opponent is weak evidence of
control. Team features are invariant to the order of slots; tests also verify
home/away exchange symmetry.

Smart Tagging timestamps use `round(seconds * 25)` and half-open intervals.
Defensive tags vote for the opponent of the named team. Unknown/N/A team names
produce no ownership vote. Overlapping offensive and defensive descriptions are
saturated, so repeated correlated tags cannot arbitrarily multiply confidence.
Phase evidence is weaker than strong direct geometric evidence.

A separate dead-ball score combines observed outside-pitch ball positions,
stationary ball with low player motion, and missing ball corroborated by low
player motion. Missing ball alone contributes no dead-ball evidence. Restart
tags provide context, never a fixed dead interval.

Within a set-piece window, the optional restart localizer seeks a reliable change
from stationary ball to moving ball with quiet-player context. A supported anchor
provides a short, decaying live/team cue and quiet evidence before it. If motion
does not support an anchor, none is fabricated. Seven restart windows were
localized on the supplied inputs; this is an algorithm diagnostic, not accuracy.

## Duration-constrained sequence inference

One offline dynamic program jointly chooses `H`, `A` and `D`. It maximizes the
sum of frame evidence divided by FPS minus transition costs. The fixed costs are
1.1 for a team change and 0.7 for entry to/exit from dead ball. Expanded age states
enforce minimum durations of 0.32 s for H/A and 0.64 s for D before another switch;
the final segment may be truncated by the end of a half. There is no forced mean
possession duration. This is a constrained energy model, not a calibrated posterior
or a learned general-duration HSMM.

The two halves decode independently. A confidence-weighted evidence gap can retain
possession without inventing contact. Sustained opposing evidence can establish
even a short genuine possession. Boundaries remain at full 25 FPS resolution;
there is no subsequent blanket deletion of short runs or shift to tag midpoints.

`X` is emitted only outside published graded halves. The published second-half
pre-kickoff interval is constrained to `D`, using the organiser's tagging-loader
kickoff constant consistent with FAQ. The scorer forward-fills `X` inside graded
runs for spellF1; uncertainty abstention is therefore not treated as free.

## Verification and cost

The official smooth50 baseline was regenerated and validated as an independent
fallback. YDSE tests cover archive traversal/collisions/corruption, parser alignment,
team mapping, gaps, spikes, confidence decay, tactical polarity, restart localization,
dead states, short turnovers, slot permutation and deterministic CSV generation.
The decoder is checked against exhaustive search on a small sequence.

Twenty independent procedural scenarios (36,000 frames) include ball dropouts,
positional noise, false touches, ownership changes and stationary stoppages. Mean
synthetic spellF1 is 0.8001 for YDSE, 0.5779 for official smooth50 logic and 0.3437
for raw nearest-player logic. These simplified simulations test mechanisms; they
do **not** estimate the competition score or establish superiority over other teams.
No full-match quality score is claimed.

Two full-match runs produced identical bytes and passed both the official validator
and our stricter exact-column check. Measured runtime is approximately 15 s per
run, with approximately 976 MiB peak working set on the available Windows laptop.
The tested runtime is Python 3.14.3, NumPy 2.5.4 and pandas 3.1.1; exact pins and
run-specific measurements accompany the release. No GPU or network is required.

## Related approaches and limits

The duration design follows the general state-duration principle in
[Yu (2010)](https://www.cs.ubc.ca/~murphyk/Teaching/CS540-Spring10/projects/Yu-hsmm09.pdf).
Control versus proximity is motivated by the methods in
[Automatic event detection in football using tracking data](https://link.springer.com/article/10.1007/s12283-022-00381-6).
We did not adopt that paper's provider-specific missing-ball/dead assumption.
Public implementation reviews motivated integrated duration constraints and
motion-supported restart handling; no competitor source or weights were reused.

Principal limitations are heuristic dead-ball calibration, long observation gaps,
unobserved referee decisions, aerial contacts without height, and sparse reliable
restart anchors. Synthetic sequences cannot validate their real-match error rates.
External match-disjoint calibration and improved ball sensing are future work.
Signed data terms, final submission cutoff and public repository URL require team
review. No publication or competition upload has been performed.

## Reproduction

With Python 3.14.3 and the canonical licensed data layout:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
$env:MTAH_DATA_DIR = 'D:\licensed-data'
.venv\Scripts\python scripts/generate_submission.py --out submission/YDSE.csv
.venv\Scripts\python upstream/validate_submission.py submission/YDSE.csv
.venv\Scripts\python scripts/verify_release.py --team YDSE
```

The final command runs two fresh full parses/inference passes, validates both,
and compares input, code/config and output hashes. Detailed metadata remains local
in `private/release_verification.json`; public source contains no restricted assets.
