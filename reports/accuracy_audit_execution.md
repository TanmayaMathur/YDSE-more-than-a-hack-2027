# Accuracy audit execution record - 14 November 2026

Starting revision: 8b184b0c626e108679b97a344ef06a661f860d5b, clean worktree.
Created accuracy-improvement branch. Copied and hashed V1 CSV, PDF, Markdown,
release JSON, run JSON and smooth50 fallback into private/accuracy_audit/v1_preserved/.
The expected V1 CSV hash matched before any edits.

Executed work:

1. Re-fetched official priority files and repository/issue/PR/comment surfaces through
   the connected GitHub tool. Zero accessible open/closed issues and PR search results;
   PR and issue-comment listings returned 404. gh commit-comment fallback returned zero.
2. Read every targeted inference module, generation/release scripts, configuration,
   tests, benchmark and actual metric functions. Constructed focused counterexamples.
3. `.venv\Scripts\python scripts/audit_probes.py`: reproduced reliability promotion,
   sparse motion, graded-boundary leakage, arbitrary hidden-turnover timing and ambiguous
   stationary-live failure. Probe inputs are artificial, not match annotations.
4. `.venv\Scripts\python scripts/metric_mechanisms.py`: executed official scorer on
   constructed false-touch/dead, missed-turnover/dead, X and half-boundary cases.
5. Added V2 without editing the original seven inference modules. Added independent
   16-family design, four development seeds and eight held-out seeds before development.
6. `.venv\Scripts\python scripts/run_accuracy_stress.py --split development`: initial
   prototype exposed a stronger-contact filter erasing rapid legitimate turnovers.
   Disabled that filter in the candidate; kept it as an explicit experimental ablation.
   Added independently demonstrated noise-bias correction. Preserved initial results.
7. Re-ran development, then froze v2.py/config and ran
   `.venv\Scripts\python scripts/run_accuracy_stress.py --split holdout` once. No model
   parameters or V2 inference source changed after holdout exposure. Final protocol:
   64 development + 128 holdout cases, 11 variants, 2,112 model runs.
8. First candidate generation exposed the old generator's relative --config path hash
   error after CSV writing. Fixed path resolution and added a V2 overwrite guard.
9. `.venv\Scripts\python scripts/verify_accuracy_candidate.py`: two complete candidate
   executions, both officially validated, exact hash equality, ungraded X and all
   2,934 pre-kickoff D frames checked, all six protected V1 artifact hashes unchanged.
10. `.venv\Scripts\python scripts/run_match_audit.py`: initially hit NumPy int64 JSON
    serialization in aggregate diagnostics; converted the counter to Python int and
    reran successfully. Both reconstructed diagnostic label sequences match exact CSVs.
    Restricted per-transition data stays private; only aggregates are public.
11. Primary API verified CC BY 4.0 for Sportec/DFL other-match data. Preselected J03WOH
    by smallest file size before inspecting outcomes. Wrote external validation plan.
    `.venv\Scripts\python scripts/fetch_external_dfl.py`: downloaded metadata and 348.9 MB
    tracking XML, verified size and MD5; no competition data sent anywhere.
12. `.venv\Scripts\python scripts/validate_external_dfl.py`: frozen V1/V2 evaluation on
    137,214 frames of a different 2022/2023 German match, clean and two fixed dropout
    realizations. Repeated without model changes only to add paired uncertainty and
    preserve prediction arrays. Results unchanged. No fitting/training was performed.
13. `.venv\Scripts\python -m pytest tests -q`: 57 passed, 2.30 seconds. Includes external
    target-field separation. `.venv\Scripts\python -m compileall -q src scripts tests`: passed.
14. `.venv\Scripts\python scripts/build_accuracy_reports.py`: compiled required reports
    from actual results, including regressions, uncertainty, limitations and safe reproduction.

The original overwrite-oriented verify_release.py was not used during experiments.
Original submission/PDF/metadata/fallback are untouched. Final post-commit candidate
verification records its exact source revision, runtime, memory, input/config/output
hashes separately in private/accuracy_audit/candidate_verification.json.

No competition labels were manually annotated, scored for model selection, corrected,
trained on or uploaded. Neither code nor candidate has been published/submitted.
