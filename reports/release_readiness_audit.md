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

| Match | Model | D precision | D recall | False D seconds | Excess fragments (all lengths) |
| --- | --- | --- | --- | --- | --- |
| J03WQQ | v2 | 0.9948 | 0.4598 | 5.60 | 5 |
| J03WQQ | v3 | 0.9864 | 0.7961 | 25.40 | 6 |
| J03WN1 | v2 | 0.9967 | 0.5635 | 5.52 | 4 |
| J03WN1 | v3 | 0.9917 | 0.9086 | 22.28 | 4 |

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

A source-only export at `3a386275b0692c6898005509b4c7524bd4223ca3` and a fresh venv
installed all existing pins with no system/user-site packages. All 71 tests pass;
two full runs using only licensed local inputs reproduce the exact V3 bytes
(19.45/18.99s). Both official and strict validators pass. This is same-host
Windows/CPython verification, not a cross-platform guarantee. Original CSVs,
weights, configs, source and historical verification artifacts remain unchanged
(40 protected hashes). The final release adds documentation/packaging only.

V3 SHA-256: `3a27d7d90657d1e4b9485007f0d7ea1d95ac662a64d4a3fbe5c1b50daf4ef534`.
Model SHA-256: `0562bf7f6850030346193e88484439b7aa8e0ffb05d273ec035c76e9cd18e4dd`.
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
