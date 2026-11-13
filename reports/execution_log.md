# Execution log

2026-11-14 (Asia/Kolkata): Read user brief, inspected initial workspace: eight archives and two MP4 files. Python 3.14.3 is the only installed Python; Git and GitHub CLI are available. No project code or local AGENTS.md found.

- `git clone https://github.com/metrica-sports/more-than-a-hack-2027.git official`: sandbox network failed; retried with approved network access, successful. Upstream HEAD f8f2629.
- Read official challenge, data, scoring, submission and rules documents before restricted-data processing. Hosted LLM disclosure prohibited; all restricted processing will use local Python. Signed terms not located yet; requested path from user. No raw match content will be returned to model context.
- `python -m venv .venv`: started. Only Python 3.14 available; use tested available runtime rather than silently claiming Python 3.11.

Public-window labels will not select, tune, train or rank our models. Final CSVs and reconstructable derivatives remain excluded from public source.

## Data and baseline

- `python scripts/prepare_data.py`: eight archives hashed, member inventories inspected, extracted to separate checksum-qualified staging directories. Success; originals unchanged.
- `python scripts/identify_assets.py`: first failed on Windows hard-link permissions; retried with approved elevated execution, succeeded. Nine expected assets identified; both tracking/homography frame counts verified. Both MP4 signatures checked; no complete video decode performed. All asset checksums recorded locally.
- `.venv\Scripts\python -m pip install numpy pandas pytest`: approved package installation into isolated environment, success. Exact tested versions frozen in requirements.txt.
- From `official/`: `..\.venv\Scripts\python evaluation/run_evaluation.py`: successful official demonstration on shipped baseline CSVs only. Its rankings were not model-selection evidence.
- `$env:MTAH_DATA_DIR = (Join-Path (Get-Location) 'data')`; `.venv\Scripts\python official/starter/baseline.py --out submission/fallback`: success, 3.52 s.
- `.venv\Scripts\python official/evaluation/validate_submission.py submission/fallback/baseline_smooth50.csv`: PASS, 199319 rows; 669 reported possessions. The organiser's published full-match score is not a score measured here.
- Workspace agreement/PDF/DOCX filename search found no applicable signed terms. User confirmed Drive access but explicitly did not authorize disclosure. Continued local-only processing, as requested.

## Public research

- `.venv\Scripts\python scripts/update_github_intelligence.py`: paginated official metadata/history/comments/forks and 20 alternative repository queries; successful scan with endpoint-specific errors preserved.
- PR listing: HTTP 404 through gh and connected GitHub tool. Issue listing and repository-scoped searches: no accessible records; issue comments 404. Discussions disabled. Wiki fetch failed. No invented PR/issue findings.
- Six official commits and diffs inspected using `git -C official log --all --stat`, `git -C official diff e47adea HEAD -- ...`, public API detail and source reads. Scoring/alignment implementations unchanged since initial commit; annotation rules changed.
- Sparse public source checkouts of darfattt, DivyanshAfk, ArmicZeroGTRS, aditwidi/team-nexus, hnfadtya, yassintamer91 and 4139benuzter inspected. No competitor predictions or weights used.
- `.venv\Scripts\python -m pytest vendor_research/darfattt/tests -q` with its src on PYTHONPATH: 12 passed.
- `.venv\Scripts\python vendor_research/Armic/tests/test_pipeline.py`: sparse checkout initially lacked organiser helpers. Supplied unmodified pinned helpers; 15/16 checks passed, one end-to-end test failed because Windows relpath spans C: temporary directory and D: repository. No full-match comparative quality test performed.
- Opus public profile inspected; linked engine/benchmark repositories returned 404. Claims remain unverified.
- Public code search `spellF1 language:Python` paginated across four pages; only repository/path metadata retained. Index results changed during scanning.
- Notebook read initially failed with default Windows cp1252; rerun with UTF-8 succeeded. No restricted notebook outputs were displayed.
- Update check `scripts/update_github_intelligence.py --quick` initially failed reading a UTF-8 cache with Windows default cp1252. Fixed explicit UTF-8; rerun succeeded. No new official commit detected. Future November 16/submission-day checks remain manual.
- `.venv\Scripts\python scripts/build_research_reports.py`: generated source-linked research files, full metadata inventory and scope/access counts. Removed unnecessary fork patch bodies from local cache.

## Model and verification

- Initial YDSE full pipeline executed and validated before refinements. Implemented bounded repair, team/flight evidence, soft phases, explicit dead evidence and exact duration constraints.
- Synthetic stationary/slow test failed: geometric team evidence outweighed corroborated stoppage evidence. Increased the stationary-plus-slow term based on this artificial case; rerun passed.
- Motion-localized restart test failed: window contrast peaked four frames before constructed launch. Added before/after state purity to select the actual constructed boundary; rerun passed.
- `.venv\Scripts\python -m pytest tests -q`: latest run 21 passed, 1.64 s. Includes brute-force decoder check, slot permutation and team-swap symmetry.
- `.venv\Scripts\python -m compileall -q src scripts tests`: passed.
- `.venv\Scripts\python scripts/benchmark_synthetic.py`: 20 procedural scenarios, 36000 frames. Actual results saved to reports/synthetic_benchmark.json; no competition-quality claim.
- `.venv\Scripts\python scripts/verify_release.py --team YDSE`: two fresh full parses/inference runs; both officially validated and exact-byte SHA-256 matched. Baseline remains private fallback.
- Further source-only metadata/validation changes require the final post-commit release run recorded in reproduction_report.md. No data, repository or submission uploaded externally.
- Initial root `git add` was blocked by the sandbox's read-only .git/index policy; no files were staged. The hygiene checker incorrectly reported an empty index as PASS; changed it to reject an empty tracked-file list before retrying staging with approved local Git writes.
