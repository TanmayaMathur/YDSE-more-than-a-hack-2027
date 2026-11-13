# YDSE final submission checklist - frozen V3

**Selected file: the existing V3, not a regenerated/tuned variant.** Source
preparation is local only. The original `submission/YDSE.csv` is preserved V1;
do not accidentally upload it. Use the separate new submission bundle.

## Verified locally

- [x] V3 exact SHA-256 `3a27d7d90657d1e4b9485007f0d7ea1d95ac662a64d4a3fbe5c1b50daf4ef534`.
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
