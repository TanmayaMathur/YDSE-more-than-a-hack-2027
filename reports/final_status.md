# Final handoff — YDSE

## Built and working

The workspace contains collision-safe data preparation, a regenerated official
baseline fallback, implemented hybrid possession inference, automated synthetic
tests, a public GitHub intelligence scanner, source-linked research and technical
documentation. `submission/YDSE.csv` is complete, officially format-validated and
byte-for-byte reproducible. Source is prepared locally; nothing has been published
or uploaded to the competition.

Algorithm: confidence-weighted metric geometry and player/ball motion, bounded ball
repair, saturated automatic phase priors with defensive inversion, motion-supported
restarts, explicit dead-ball evidence and per-half duration-constrained Viterbi.
No supervised training or same-game human annotations were used.

## Research scope and findings

Six official commits reviewed; zero accessible issue or PR bodies. Issues are disabled
in metadata; PR and issue-comment listing returned 404, while searches returned no
accessible results. Counts of inaccessible history remain Unknown. Discussions are
disabled; wiki content was inaccessible. No findings were fabricated for those surfaces.

Paginated listing covered 288 accessible forks: 66 with upstream changes, including
51 changing Python filenames. The inventory contains 401 challenge-related candidate
repositories (many are starter-only), with seven implementations deeply inspected.
The source inventory distinguishes code inspection from metadata screening. It is
not a ranking and is not an assertion that all 401 contain working competing models.

Important verified findings and engineering consequences:

1. Official October rule revisions prohibit any same-match hand labels and public-window
   tuning. No such training/selection was performed; tests are independently procedural.
2. Metric code counts same-team whole spells, splits at D and fills abstentions within
   graded runs. We decode complete halves and emit X only outside them.
3. Tactical ATD alignment is frame_id minus one, not the private IdFrame offsets. The
   parser verifies exact IDs and refuses silently dropped records.
4. Tag windows are imprecise and defensive tags name the defending team. Our priors
   invert defensive polarity, saturate correlated phases and require motion to locate restarts.
5. Several implementations apply post-hoc short-run merging or fixed restart windows.
   YDSE integrates duration constraints into the optimizer and retains supported short turns.

Opus profile claims could not be checked against its advertised engine/benchmark
repositories (404). Competitor public-window score claims were not selection signals.
No competitor code, model or final predictions were copied. Detailed URLs, SHAs,
licence metadata and caveats appear in research/.

## Actual verification and limits

21 tests passed, compileall passed, 20 procedural scenarios executed. Final full-match
verification parses/infers twice, runs official and strict validation and checks hashes.
Runtime is about 15 s per generation, peak working set about 976 MiB. Synthetic
spellF1 .8001 is a simulator result only. No private-match score or ranking exists here.

Dead-ball thresholds are heuristic, long ball occlusions remain uncertain, and no
external labelled calibration or heavy vision model was trained. Seven public source
reviews do not exhaust all candidate implementations. More sophisticated methods in
the research reports are explicitly distinguished from implemented code.

## Deliverables

- Final possession file: `submission/YDSE.csv`.
- Identical independent regeneration: `submission/YDSE_reproduced.csv`.
- Fallback: `submission/fallback/baseline_smooth50.csv`.
- Technical report: `docs/technical_report.md`, also `submission/YDSE.md` and visually checked `submission/YDSE.pdf`.
- Public-ready code: this repository's tracked files; inspect `git ls-files`.
- Exact run/commit/input/output hashes: local `private/release_verification.json`.
- Final output SHA-256: `45e91b5246b6a05db7f8b5e034185e0bbd4cf6eab7c9dcc2e4b4d027f369ae35`.

Reproduction:

```powershell
$env:MTAH_DATA_DIR = 'D:\licensed-data'
.venv\Scripts\python scripts/verify_release.py --team YDSE
```

## Remaining team actions

1. Confirm signed terms and eligibility, registered name YDSE, form URL and exact
   deadline cutoff/timezone in official communications. The public date is November 17,
   2026. Drive access is not disclosure permission.
2. Review the report, limitations and staged/tracked source list. Approve publication,
   then create/push a public GitHub repository containing only tracked public files.
3. On November 16 and just before submission, manually run the public update scanner:
   `.venv\Scripts\python scripts/update_github_intelligence.py --quick`.
   Inspect changed official rules/scorer files before adopting any change.
4. Rerun `scripts/verify_release.py --team YDSE`; verify the exact final CSV hash.
5. Upload YDSE.csv, YDSE.pdf (or YDSE.md) and the public repository URL through the organiser's
   emailed form under YDSE. Submit one editable team response before the confirmed cutoff.

No future scan is represented as already executed. No public push or form upload is
authorized by the preparation request; these await the team's review and approval.
