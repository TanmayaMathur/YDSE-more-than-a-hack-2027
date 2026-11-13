# YDSE - More Than a Hack 2027 possession

**Recommended frozen submission: V3.** The release audit selects the existing
50% learned/heuristic dead-ball blend on the official spellF1 objective. V3
improved spellF1 in all twelve previously evaluated views of two external
matches. Those matches are already exposed evaluation evidence, not future
untouched holdouts. False D and missed-handover risks remain documented.

See [release decision](reports/release_readiness_audit.md),
[final technical document](docs/release_technical_report.md), and
[submission checklist](docs/SUBMISSION_CHECKLIST.md). No candidate is overwritten,
published or uploaded by this repository's release preparation.

## Clean Windows reproduction

Tested with Python 3.14.3, NumPy 2.5.4 and pandas 3.1.1. A new venv installed
all pinned requirements and regenerated the exact frozen V3 twice from an isolated
committed-source export on the same Windows host. This does not establish
cross-platform or older-Python byte reproducibility.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
$env:MTAH_DATA_DIR = 'D:\licensed-data'
.venv\Scripts\python scripts/generate_submission.py --model v3 --config configs/audit_v3.json --out private/reproduced/YDSE_release_reproduction.csv
.venv\Scripts\python upstream/validate_submission.py private/reproduced/YDSE_release_reproduction.csv
.venv\Scripts\python scripts/validate_output.py private/reproduced/YDSE_release_reproduction.csv
Get-FileHash private/reproduced/YDSE_release_reproduction.csv -Algorithm SHA256
.venv\Scripts\python -m pytest -q
```

Expected CSV SHA-256:
`3a27d7d90657d1e4b9485007f0d7ea1d95ac662a64d4a3fbe5c1b50daf4ef534`.

The licensed data directory must contain these official files:

```text
tactical/BAR-ATH_tactical_atd.xml
tactical/BAR-ATH_tactical_atd.txt
tactical/BAR-ATH_tactical_smart_tagging.xml
```

Without `MTAH_DATA_DIR`, the default is local `data/`. The model reads inputs
locally and needs no network, API key, video, GPU or external training/evaluation
dataset at inference. Use an unused output name; legacy verification scripts
rewrite their own historical candidate/run paths and should not be used for a
read-only release audit. Preserve all existing candidates and private metadata.

## Frozen method and provenance

V3 retains V2's confidence-weighted physical team evidence, short-gap repair,
soft semantic phase priors, motion-localized restart context, weak two-sided
gap ownership priors and exact duration-constrained three-state decoding.
Only D evidence adds a fixed externally learned component. Identical static
tracking cannot distinguish live permission from a whistle, and a completely
hidden turnover still has only a midpoint prior.

`models/ydse_live_dead.json` contains 18-feature normalization and 19 logistic
coefficients, trained on 82,329 sampled/augmented rows from J03WOH only.
Provider BallStatus is the external target; no competition-match human labels,
public-window selection, manual corrections or competitor predictions are used.
Training is not part of release preparation. [Model provenance](models/README.md),
[data/design attribution](THIRD_PARTY_NOTICES.md), and
[pinned organiser helpers](upstream/PROVENANCE.md) accompany the weights.

Canonical weight SHA-256:
`0562bf7f6850030346193e88484439b7aa8e0ffb05d273ec035c76e9cd18e4dd`.

## Privacy and release checks

```powershell
python scripts/audit_public_release.py
git diff --cached --name-only
git status --short
```

The audit checks tracked/staged files, reachable Git history, prohibited formats,
large source files, likely credential values, and ignore coverage. Raw/derived
CSV, XML, tracking TXT, videos, audio, archives and model blobs are excluded;
the public competitor-inventory CSV and small attributed parameter JSON are
explicit source exceptions. Detailed release diagnostics and submission files
stay in `private/`. Public reports contain aggregate findings and synthetic
experiments, not frame-level competition predictions or tracking.

The final technical PDF is created locally with the separate release builder;
it does not overwrite the original V1 PDF:

```powershell
.venv\Scripts\python -m pip install -r requirements-pdf.txt
.venv\Scripts\python scripts/build_release_pdf.py
```

Official submission requires the registered team name, team-named CSV, public
code URL and short PDF/Markdown through the emailed Google Form. The public
deadline is **17 November 2026**; **cutoff time and timezone are unverified**.
Signed enrolment terms and the private form URL still need participant review.
Source publication and form upload require explicit approval. No submission
form, message or remote repository is changed by these local commands.

## Preserved history

V1, V2 and V3 CSVs and prior verification artifacts remain byte-identical.
The earlier analysis and technical documents are retained as historical reports;
the release documents above are the current instructions and candidate decision.
Original source is MIT licensed; third-party notices retain the public logistic
design/IRLS attribution and CC BY 4.0 external-data attribution. Competition
assets are separately restricted and are never covered by the source licence.
