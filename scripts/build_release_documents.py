"""Assemble release-only documentation from existing frozen audit evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def write(path,text):(ROOT/path).write_text(text.strip()+'\n',encoding='utf-8',newline='\n')
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])


def main():
    r=json.loads((ROOT/'private/release_audit/readiness_metrics.json').read_text())
    clean=json.loads((ROOT/'private/release_audit/clean_reproduction/verification.json').read_text())
    csvhash=r['candidates']['v3']['sha256'];modelhash='0562bf7f6850030346193e88484439b7aa8e0ffb05d273ec035c76e9cd18e4dd'
    rows=[]
    for x in r['external']:
        rows.append([x['match'],x['condition'],x['model'],f"{x['dead_precision']:.4f}",f"{x['dead_recall']:.4f}",f"{x['false_positive_D_seconds']:.2f}",x['predicted_HA_spells'],x['fragmented_true_spells'],x['excess_same_team_fragments'],x['interior_false_D_segments']])
    external_table=table(['Match','Condition','Model','D precision','D recall','False D seconds','Predicted H/A spells','Fragmented true spells','Excess fragments','Interior false D runs'],rows)
    clean_table=table(['Match','Model','D precision','D recall','False D seconds','Excess fragments (all lengths)'],[[x['match'],x['model'],f"{x['dead_precision']:.4f}",f"{x['dead_recall']:.4f}",f"{x['false_positive_D_seconds']:.2f}",x['excess_same_team_fragments']] for x in r['external'] if x['condition']=='clean'])
    write('reports/release_external_dead_ball.md',f'''
# Release audit: existing external prediction error accounting

No new model, fitting, calibration, parameters or match selection. These are
**already examined** J03WQQ/J03WN1 evaluation outputs; they are not untouched
future holdouts. J03WOH is training/development and is excluded from independent
evidence. Raw arrays and detailed diagnostics stay private.

{external_table}

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
''')
    write('reports/release_readiness_audit.md',f'''
# Final release-readiness audit - YDSE, 14 November 2026

**Decision: submit the existing frozen V3 candidate after explicit approval.**
The spellF1 evidence consistently favors V3 across the two already exposed
external matches and all twelve fixed conditions. This audit does not retrain,
tune, make V4 or use competition-match human labels/video inspection. The
official public five-minute labels were not scored or used for selection.

## Independent CSV recount

| Measure | V2 | V3 |
|---|---:|---:|
| D frames | 28,762 | 40,211 |
| D segments | 101 | 113 |
| H/A spells | 365 | 365 |
| Required pre-kickoff D | 2,934 | 2,934 |

Confirmed with a stdlib CSV parser and two independent run-counting routines.
11,806 labels differ: H->D 6,283; A->D 5,227; D->H 6; D->A 55;
H->A 159; A->H 76. Thus 11,510 D additions minus 61 removals = **11,449
net D frames, 457.96 seconds (7m37.96s)**. X and graded boundaries are unchanged.
Twenty V3 D segments have no V2 D overlap; six V3 D segments combine multiple
V2 D intervals. Equal H/A spell totals do not establish equal boundaries or
accuracy. No available permitted competition truth can adjudicate the extra time.

## Origin of the D increase

Frozen V2 team energy s, heuristic D energy d and learned external D/live log
odds z give V3 D energy `.5*d + .5*(abs(s)+z+restart_delta)` on supported
frames. Otherwise it retains d. No new transition cost, duration, gap repair,
tactical interpretation or hard missing-ball-is-dead rule was introduced.

An automatic read-only replay exactly matches both frozen CSVs. Of 11,510
newly D-labelled frames, 9,038 (78.5%) lack a raw ball observation and all have
learned-head support. D energy rises locally on 11,487; the remaining 23 follow
the globally duration-constrained decoded path. Mean local increase is 1.099;
mean absolute team energy is only .372 and mean learned log odds is 1.792.
None of these added frames saturates the +/-5 log-odds clip. Additions are
5,814/5,696 in halves one/two, removals 18/43. The common pre-kickoff D contract
does not explain any difference.

The largest positive mean centered-logit contributions on added D are low
player activity fraction (+.627), low activity (+.529), missing/slow interaction
(+.486), low ball speed (+.415) and slow-team score (+.379). Activity/speed
coefficients are negative, so below-training-mean values contribute positively.
Features are correlated; these contributions are descriptive, not causal proof
or ground-truth verification. Only 1,372 additions have stationary score >.5:
the change is broader than stationary-ball thresholding. The `abs(s)` anchor,
learned low-activity evidence and unchanged temporal costs can jointly lengthen
or insert D, truncate possession or alter neighboring H/A choices.

## Existing external evidence and risks

{clean_table}

False D duration rises by 19.80s and 16.76s. The larger benefit is fewer missed
true D frames: clean spellF1 improves .4248->.4799 and .3318->.4235. All twelve
views improve; this outweighs conservative D counts for the ranking objective.
Direct H/A handover recall falls .2947->.2881 and .2487->.2183. WQQ fragmentation
increases; dropout can worsen it further. Stationary-live ambiguity, uncertain
hidden turnover timing and weak short-spell recall remain. More D is not
automatically more accurate. Full precision/recall, false-positive seconds and
all-length fragmentation for every condition are in
`release_external_dead_ball.md`. These two matches are historical evaluation
evidence, not new/future untouched holdouts or the hidden competition score.

## Reproduction and release checks

The 2,500-byte JSON contains normalization, coefficients, feature schema,
J03WOH-only provenance, label source, licence and attribution. MIT source-design
notices, CC BY 4.0 data attribution, pinned runtime dependencies and explicit
V3 commands are present. Underlying BallStatus flags come from Sportec/DFL;
YDSE did not hand-label them or reconstruct their annotation personnel.
No retraining was performed in this release audit.

A source-only export at `{clean['source_export_commit']}` and a fresh venv
installed all existing pins with no system/user-site packages. All 71 tests pass;
two full runs using only licensed local inputs reproduce the exact V3 bytes
(19.45/18.99s). Both official and strict validators pass. This is same-host
Windows/CPython verification, not a cross-platform guarantee. Original CSVs,
weights, configs, source and historical verification artifacts remain unchanged
(40 protected hashes). The final release adds documentation/packaging only.

V3 SHA-256: `{csvhash}`.
Model SHA-256: `{modelhash}`.
Exactly 199,319 rows, frame IDs 0-199318, H/A/D/X, X outside published halves,
and D on 110808-113741 are verified. Existing CSVs were read, never rewritten.
Two new audit outputs stay private. Detailed logs and input diagnostics are
excluded from the public source. See `scripts/verify_clean_v3_release.py`.

`audit_public_release.py` checks actual staged blobs, current files and reachable
historical blob contents/paths, credential patterns, binary/large files, and
ignore probes. No restricted assets or prediction files were found. Ignore
coverage now also blocks CSV/XML/tracking TXT/media anywhere; only the public
competitor inventory and requirements TXT are exceptions. The approved source
package is made from a committed Git archive, never a workspace ZIP. Re-run the
audit immediately before any approved publication; forced adds can bypass ignores.

## Submission status

[Official SUBMISSION.md](https://github.com/metrica-sports/more-than-a-hack-2027/blob/main/SUBMISSION.md)
requires registered team name YDSE, `YDSE.csv`, public source URL and short
`YDSE.pdf`/Markdown, through an emailed Google Form. One team response; the
last pre-deadline response is scored. The [organiser landing page](https://landing.mobileworldcapital.com/more-than-a-hack-2027)
and repository confirm **17 November 2026**, with no accessible cutoff time or
timezone. The participant also has no exact time. **Exact cutoff is unverified;
do not assume midnight or convert an invented timezone.** Form URL and accepted
signed terms remain participant checks. No email/message is sent by this audit.

The public-ready source, separate final technical PDF, team-named local CSV
copy and exact checklist are prepared without replacing any existing candidate.
Publication and form upload remain pending explicit approval. No remote push,
upload, submission or promotion was performed. The recommendation is exactly V3.
''')
    write('docs/SUBMISSION_CHECKLIST.md',f'''
# YDSE final submission checklist - frozen V3

**Selected file: the existing V3, not a regenerated/tuned variant.** Source
preparation is local only. The original `submission/YDSE.csv` is preserved V1;
do not accidentally upload it. Use the separate new submission bundle.

## Verified locally

- [x] V3 exact SHA-256 `{csvhash}`.
- [x] 199,319 data rows; exact `frame,label`; IDs 0-199318; H/A/D/X only.
- [x] X outside official halves; D on frames 110808-113741 inclusive (2,934).
- [x] Official validator and strict validator pass on the exact V3 bytes.
- [x] Two isolated-source/fresh-venv full runs reproduce the same hash; 71 tests pass.
- [x] Frozen source/config/model weights unchanged; all three candidates preserved.
- [x] CC BY training-data attribution and MIT design notices included; no training required for inference.
- [x] Current source/index/history and ignore audit passes; restricted inputs,
  competition predictions and detailed private diagnostics excluded.
- [x] Separate final technical document and visually checked PDF prepared locally.

## Before approved publication/upload

- [ ] Review and explicitly approve source publication and submission. Nothing is published yet.
- [ ] Verify accepted enrolment/data-use terms; the Drive invitation is not permission to share data.
- [ ] Confirm the Google Form URL from the organiser's email; it is not publicly posted in the repository.
- [ ] Obtain the exact **November 17, 2026 cutoff time and timezone** from the organiser.
  Public sources and participant do not provide a time; no midnight assumption is valid.
- [ ] Confirm the registered name is exactly **YDSE**, team details are correct,
  and the submitting Google account can upload. Only one response per team.
- [ ] Re-run `python scripts/audit_public_release.py` and review the approved commit/diff.
- [ ] Publish only approved committed source to the chosen public URL after approval;
  verify LICENSE, THIRD_PARTY_NOTICES, README, requirements, config and model JSON are accessible.
- [ ] Confirm a fresh user with licensed inputs can follow the README and get the expected hash.
- [ ] Use `private/release_audit/submission_bundle/YDSE.csv` and `YDSE.pdf`.
  This is a new copy of V3; never replace V1/V2/V3 originals or upload a workspace archive.
- [ ] Revalidate that exact bundle CSV immediately before the form upload:

```powershell
python upstream/validate_submission.py private/release_audit/submission_bundle/YDSE.csv
python scripts/validate_output.py private/release_audit/submission_bundle/YDSE.csv
Get-FileHash private/release_audit/submission_bundle/YDSE.csv -Algorithm SHA256
```

- [ ] Verify the PDF hash against the local bundle manifest and read the final PDF.
- [ ] Enter Team Name **YDSE**, upload team-named CSV and PDF, and supply the approved
  public code URL. Do not upload tracking, videos, private diagnostics or source ZIP to the CSV field.
- [ ] Submit only after approval; save the response receipt locally and verify uploaded filenames.
- [ ] If editing the response, the last response before the deadline is scored.
  No live leaderboard or accuracy feedback is promised.

Authority: [official submission instructions](https://github.com/metrica-sports/more-than-a-hack-2027/blob/main/SUBMISSION.md),
[organiser schedule](https://landing.mobileworldcapital.com/more-than-a-hack-2027).
Final audit: `reports/release_readiness_audit.md`. Exact PDF/source archive hashes
and the approved-source commit are recorded in the local bundle manifest.
''')
    write('docs/release_technical_report.md',f'''
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
.venv\\Scripts\\python -m pip install -r requirements.txt
$env:MTAH_DATA_DIR = 'D:\\licensed-data'
.venv\\Scripts\\python scripts/generate_submission.py `
  --model v3 --config configs/audit_v3.json `
  --out private/reproduced/YDSE_release_reproduction.csv
.venv\\Scripts\\python upstream/validate_submission.py `
  private/reproduced/YDSE_release_reproduction.csv
.venv\\Scripts\\python scripts/validate_output.py `
  private/reproduced/YDSE_release_reproduction.csv
.venv\\Scripts\\python -m pytest -q
```

Use an unused output name to preserve historical candidates/metadata. The supplied
model JSON and config are sufficient; no external dataset, network, API key or
training is required at inference. Optional full training provenance and its
historical commands remain documented in models/README.md, not part of release.

Expected V3 CSV SHA-256:

```text
{csvhash}
```

Canonical learned-model SHA-256:

```text
{modelhash}
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
''')
    print('Built release decision, external accounting, exact checklist and final technical Markdown.')


if __name__=='__main__':main()
