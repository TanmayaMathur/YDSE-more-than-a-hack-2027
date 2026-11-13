# Reproduction report

The release verification script completed two independent full-match executions,
each reparsing the original tactical ATD. Both exact output files passed the
unmodified organiser validator and the additional strict schema check.

```powershell
.venv\Scripts\python scripts/verify_release.py --team YDSE
```

Final CSV SHA-256:
`45e91b5246b6a05db7f8b5e034185e0bbd4cf6eab7c9dcc2e4b4d027f369ae35`

Tested environment: Windows, Python 3.14.3, NumPy 2.5.4, pandas 3.1.1.
requirements.txt pins the entire tested dependency set, including the test runner.
The initial two measured verification runs took 14.56 s and 14.79 s; peak working
sets were 975.37 MiB and 975.61 MiB. Subsequent freeze verification records retain
their own timings, code commit, dirty-state flag, exact code/config digest, used
input hashes and output hash locally in `private/release_verification.json`.

Source-only metadata and validation changes were made after the initial verification;
the same verification command is rerun after the final source commit. That local
manifest is the authority for the delivered code revision and actual latest timing.
Source/report files can be published after review; input manifests, match files,
tracking-derived arrays and prediction CSVs are excluded from Git.

No cache, random seed or network affects final inference. Output encoding is UTF-8
with explicit LF newlines. No CSV is edited manually. The baseline fallback remains
in submission/fallback/ and is independently validated.
