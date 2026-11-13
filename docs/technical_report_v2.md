# YDSE V2 - accuracy-audit candidate technical addendum

This addendum describes a separate candidate. The original YDSE.csv, PDF, Markdown,
release metadata and baseline are preserved. V1 remains the submission of record until
the team chooses to promote V2. V2 full-match accuracy is unknown.

## Implemented changes

V2 keeps the original ATD parser, pitch/frame alignment, bounded .8-second trajectory
repair and exact duration-constrained H/A/D decoder. Costs stay 1.1 for team changes
and .7 for dead transitions; minimum dwell remains .32/.32/.64 seconds. No model is trained.

All feature windows, events and restart operations are now scoped to each graded block.
Numerically coincident same-team slots are removed at 5 cm tolerance. Collective motion
uses approximately .2-second centered displacements, rejects impossible/interrupted tracks
and requires sufficient independent position and motion coverage. Stationary-ball evidence
retains continuous endpoint reliability instead of promoting any nonzero repair confidence
to a full observation. These are evidence/invariance fixes, not calibrated probability estimates.

The tag mapper explicitly whitelists codes. Build Up, Progression and Creating Chances
are primary soft evidence; ball zones/long balls and defensive thirds are weaker. Defensive
thirds invert actor polarity. Transitions, Players in the Box, Goals, unknown codes and N/A
teams provide no settled-control vote. Repeated/correlated phases use maximum pooling.
Set-piece windows remain uncertain context, with motion-supported optional restart anchors.

For entirely invisible ball intervals with sustained reliable control at both endpoints,
a weak ownership-only bridge retains same-team evidence or varies symmetrically between
opposing teams. It never creates a long invisible trajectory. Its midpoint preference is
an explicit uncertainty prior; it can be wrong for edge-of-gap or multiple hidden turnovers.

The stronger experimental co-motion gate and quiet-only dead cap are not included. The
former erased rapid legitimate control in development. The latter cannot distinguish
identical live/dead geometry. Dead-ball weights remain heuristic and correlated.

## Verification and independent evidence

57 automated tests passed. The decoder matches exhaustive small-sequence objectives and
preserves expected timing at 20/25/50 FPS. Tests cover noise, sparse/duplicate slots, clipping,
phase semantics, sequence isolation, unknown gaps, exact schema and external target separation.
Sixteen stress families use 64 development and 128 frozen holdout cases. Holdout mean
synthetic spellF1 is 0.8060 for V1 and 0.8622
for V2; this is not a real-match accuracy estimate or sufficient selection evidence.

One preselected independent CC BY 4.0 Sportec/DFL match (J03WOH, 2022/2023) was evaluated
after model freeze. Frame-level BallStatus/BallPossession are separate evaluation references,
never input features or phase priors. No training, pseudo-label fitting or parameter search
used them. Clean and two independent burst-dropout views favor V2 slightly; two exploratory
paired intervals include zero. See reports/external_validation.md for the actual table,
attribution and domain/annotation limits. These are not competition-match scores.

Both complete candidate runs pass official and strict validation, have identical bytes,
use X only outside graded blocks and produce D on all 2,934 published pre-kickoff frames.
Candidate SHA-256: `79d4552782eebc37995ccb8603a091518dd45dbcb33cdb7ac93daca714d01f00`. Exact timing, memory, source revision, input and
code/config hashes are retained locally in private/accuracy_audit/candidate_verification.json.

## Limits and reproduction

Stationary live play versus a whistle can be unidentifiable from tracking alone; both
versions fail the constructed exact-geometry live pause. Wrong long primary phases,
uncertain restart timing, aerial duels and genuine short weak controls remain failure modes.
External provider semantics/stable tracking and artificial missingness differ from ATD.
No supervised model or new video inference is claimed. No provided five-minute labels,
same-game human annotations, manual prediction edits or competitor outputs were used.

```powershell
.venv\Scripts\python scripts/verify_accuracy_candidate.py
.venv\Scripts\python -m pytest tests -q
```

Optional independent evaluation uses scripts/fetch_external_dfl.py and
scripts/validate_external_dfl.py, with CC BY 4.0 attribution to Bassek, Rein, Weber and Memmert
(2025), [dataset DOI](https://doi.org/10.6084/m9.figshare.28196177.v1). No network is required to
regenerate the competition candidate. Restricted assets and per-transition diagnostics remain local.
