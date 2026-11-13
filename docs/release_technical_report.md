# YDSE | Football possession from automatic tracking

More Than a Hack 2027 - Phase 1 final technical document
14 November 2026 | Existing frozen V3 | Team YDSE

## 1. Approach and football rules

We infer complete H/A possession spells and dead-ball intervals from local
automatic tactical tracking and automatic Smart Tagging. V3 retains V2's physical
team evidence and duration decoder, adding a small independently trained
dead/live evidence blend to reduce missed stoppages. Classical geometry handles
team identity; a small CPU model addresses a specific weakness without needing
a neural training pipeline, cloud service or GPU.

Coordinates are converted to metres. Coincident same-team slots are deduplicated;
impossible motion invalidates speed evidence. Ball gaps up to 0.8s may be repaired
with reduced reliability; longer gaps get no invented trajectory. Motion/stillness
requires adequate coverage. Sustained control evidence is stronger than incidental
nearest-player contact. Loose balls and brief deflections do not automatically
change ownership. Short genuine possessions are permitted, but can still be missed.

BUILD UP, PROGRESSION and CREATING CHANCES provide soft named-team votes;
defending-third phases weakly favor the opponent. Ambiguous transitions, goals
and player counts do not establish ownership. Correlated votes are max-pooled.
SET PIECES provides context; a reliable stationary-to-moving ball change may
localize a restart. A whole set-piece phase is not declared dead or owned by
its named team. D means the ball is not in play; dead-ball ownership is not inferred.

V2 supplies team energy +/-s and heuristic D energy d. A fixed 18-feature logistic
head supplies clipped external D/live log odds z. On supported frames, V3 uses
D energy .5d + .5(abs(s)+z+restart_delta); unsupported frames retain d. Physical
features include reliability, activity, stillness, control, proximity, boundary
and interactions. Composite scores are not calibrated H/A/D probabilities.

Exact age-state Viterbi decoding divides emissions by FPS, with H/A switch cost
1.1, transitions to/from D .7, and minimum dwell .32/.32/.64s. The two official
halves decode separately; X is written elsewhere. The official 2,934-frame
second-half pre-kickoff D interval is enforced. Weak two-sided ownership priors
use recovery evidence through long gaps but cannot observe hidden turnover timing.

Inputs used: tactical ATD metadata, ATD positions and automatic tactical tags.
Neither video, homography nor broadcast assets are required at inference.
No competition-match human annotations or hand-corrected outputs are used.

<!-- pagebreak -->

## 2. External training, evidence and limitations

Training uses only J03WOH, Fortuna Duesseldorf versus Jahn Regensburg, 2022/2023.
Labels are provider-supplied Sportec/DFL BallStatus flags, as distributed by
Bassek, Rein, Weber and Memmert (2025). YDSE did not hand-label them; underlying
annotation personnel/process for these flags was not independently reconstructed.
Both halves, one-in-five sampling and clean/burst/noise views yield 82,329 rows.
Train-only normalization and fixed L2=.05 fit 19 logistic coefficients. The
provided 2.5KB JSON contains all parameters and provenance. No retraining is
needed to regenerate the CSV. No retraining or parameter change occurred during
the final release audit.

Data: Bassek et al., An integrated dataset of spatiotemporal and event data in
elite soccer, CC BY 4.0, DOI 10.6084/m9.figshare.28196177.v1. The public logistic
design/IRLS pattern adapts yassintamer91/solution/stoppage.py at revision 906ec8d,
under its MIT licence; full credit/notices accompany the source. No competitor
weights, prediction CSVs or competition labels are used. J03WOH is development,
not untouched evaluation. No competition public-window training or selection.

The following fixed-model evaluations were already examined. J03WQQ and J03WN1
were reserved before fitting/selection in the earlier investigation; now they
are historical evidence and will not be used for further tuning or claimed as
future untouched holdouts. Provider definitions differ from Metrica's controlled
possession, clean ball coordinates are complete, and one match shares a club
with training. Twelve corruptions are repeated views, not twelve matches.

| Clean external match | V2 spellF1 | V3 spellF1 |
|---|---|---|
| Duesseldorf - St. Pauli (J03WQQ) | 0.4248 | 0.4799 |
| Bochum - Leverkusen (J03WN1) | 0.3318 | 0.4235 |

All twelve fixed clean/dropout/noise/slot-switch views favor V3 on spellF1.
Clean D recall rises .4598 to .7961 and .5635 to .9086; D precision falls
.9948 to .9864 and .9967 to .9917. False-D duration rises 5.60 to 25.40s and
5.52 to 22.28s. Clean direct-handover recall falls .2947 to .2881 and .2487 to
.2183. WQQ all-length excess same-team fragments increase 5 to 6; WN1 stays 4.

V3 is recommended on the ranking objective, with those explicit risks.
Identical static tracking can represent either live play or a whistle. Fully
hidden turnovers still have an uncertain midpoint prior; extra unseen turnovers
are unrecoverable without new evidence. Short-spell recall is weak. The frozen
60-case artificial holdout mean equals V2 (.8531); it is diagnostic, not match
accuracy. V3 adds net 11,449 D frames on the competition inputs, without human
truth to determine whether that extra time is correct. No hidden score or
competitor superiority is claimed.

<!-- pagebreak -->

## 3. Reproduction, exact file and responsible release

Tested on Windows with CPython 3.14.3 and pinned NumPy 2.5.4/pandas 3.1.1.
A fresh venv, with user/system site packages excluded, installed requirements
and reproduced the exact frozen V3 twice from an isolated source export. All
71 tests pass. Cross-platform byte reproducibility has not been demonstrated.

Place licensed official assets under MTAH_DATA_DIR:

```text
tactical/BAR-ATH_tactical_atd.xml
tactical/BAR-ATH_tactical_atd.txt
tactical/BAR-ATH_tactical_smart_tagging.xml
```

Run from the repository root (PowerShell; continuation uses backticks):

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
$env:MTAH_DATA_DIR = 'D:\licensed-data'
.venv\Scripts\python scripts/generate_submission.py `
  --model v3 --config configs/audit_v3.json `
  --out private/reproduced/YDSE_release_reproduction.csv
.venv\Scripts\python upstream/validate_submission.py `
  private/reproduced/YDSE_release_reproduction.csv
.venv\Scripts\python scripts/validate_output.py `
  private/reproduced/YDSE_release_reproduction.csv
.venv\Scripts\python -m pytest -q
```

Use an unused output name to preserve historical candidates/metadata. The supplied
model JSON and config are sufficient; no external dataset, network, API key or
training is required at inference. Optional full training provenance and its
historical commands remain documented in models/README.md, not part of release.

Expected V3 CSV SHA-256:

```text
3a27d7d90657d1e4b9485007f0d7ea1d95ac662a64d4a3fbe5c1b50daf4ef534
```

Canonical learned-model SHA-256:

```text
0562bf7f6850030346193e88484439b7aa8e0ffb05d273ec035c76e9cd18e4dd
```

Official and strict validators verify exactly 199,319 data rows, header
frame,label, IDs 0-199318 and H/A/D/X only. X is outside the published graded
halves; all frames 110808-113741 are D. Format validation is not an accuracy
score. The original V1/V2/V3 candidates and 40 protected artifact/source hashes
remain unchanged. Submission uses an exact team-named copy of frozen V3.

Restricted inputs, frame-level outputs and detailed diagnostics stay local and
outside Git. Public code includes required weights, licence/attribution and
reproduction commands. Publication and form upload require explicit approval.
Signed enrolment terms remain participant verification. Official public sources
state November 17, 2026 but give no cutoff time/timezone; neither is inferred.

References: github.com/metrica-sports/more-than-a-hack-2027 (rules/scorer);
doi.org/10.6084/m9.figshare.28196177.v1 (training/evaluation data);
THIRD_PARTY_NOTICES.md and upstream/PROVENANCE.md (source/data licences).
