# YDSE — More Than a Hack 2027 possession

The `accuracy-improvement` branch adds a separate audited V2 candidate. Original
V1 inference and `submission/YDSE.csv` remain unchanged. See
[accuracy audit](reports/accuracy_audit.md), [candidate comparison](reports/final_candidate_comparison.md)
and [independent other-match validation](reports/external_validation.md).

Safe V2 reproduction (does not overwrite V1 or its release metadata):

```powershell
.venv\Scripts\python scripts/verify_accuracy_candidate.py
```

V2 is an engineering recommendation for review, with demonstrated fixes and modest
frozen external-match gains. Competition accuracy remains unknown. No automatic
promotion, repository publication or submission occurs.

A deterministic, local Python pipeline that generates a full-match `frame,label`
submission from the licensed tactical tracking and automatic Smart Tagging.
It combines confidence-weighted geometry, short-gap ball repair, collective motion,
defensive-phase inversion, motion-localized restarts and duration-constrained
three-state Viterbi decoding. It performs no supervised training.

The generated candidate and official baseline fallback pass the organiser's format
validator. No full-match score or ranking is available. Synthetic test results are
correctness and robustness evidence, not estimates of competition performance.

## Windows setup and reproduction

Tested on Windows with Python 3.14.3, NumPy 2.5.4 and pandas 3.1.1.
Python 3.11 was not installed on the development machine; these pins require the
tested newer runtime. Run these commands from this repository's root:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
$env:MTAH_DATA_DIR = 'D:\licensed-data'
.venv\Scripts\python scripts/generate_submission.py --out submission/YDSE.csv
.venv\Scripts\python upstream/validate_submission.py submission/YDSE.csv
.venv\Scripts\python scripts/validate_output.py submission/YDSE.csv
```

`MTAH_DATA_DIR` must contain `tactical/BAR-ATH_tactical_atd.xml`,
`tactical/BAR-ATH_tactical_atd.txt` and
`tactical/BAR-ATH_tactical_smart_tagging.xml`, preserving official names.
Without the environment variable, `data/` in this repository is used.
No network connection, API key, video model or GPU is required for inference.

If the assets arrive as ZIPs alongside the source, the optional preparation commands
are below. Each archive is extracted separately, with no overwrites. The second
command identifies all nine official assets and creates same-volume hard links
to avoid duplicating videos. It requires Windows permission to create hard links.
Organisers who already have the canonical layout can skip both commands.

```powershell
.venv\Scripts\python scripts/prepare_data.py
.venv\Scripts\python scripts/identify_assets.py
```

An optional official checkout is useful for the original scorer demo and notebooks:

```powershell
git clone https://github.com/metrica-sports/more-than-a-hack-2027.git official
git -C official checkout f8f2629ff1e0985f81d7e59d8413678514ee1530
```

Inference uses the small pinned public source snapshot in `upstream/`; the checkout
is optional for inference and tests. To regenerate the fallback with pinned source:

```powershell
$env:MTAH_DATA_DIR = (Join-Path (Get-Location) 'data')
.venv\Scripts\python upstream/baseline.py --window 50 --out submission/fallback
```

## Checks

```powershell
.venv\Scripts\python -m pytest tests -q
.venv\Scripts\python scripts/benchmark_synthetic.py
.venv\Scripts\python scripts/generate_submission.py --out submission/YDSE_reproduced.csv
Get-FileHash submission/YDSE.csv,submission/YDSE_reproduced.csv -Algorithm SHA256
```

Synthetic scenarios test noise, deflections, missing observations, stationary
stoppages and ownership changes. The scorer demo was run once on the shipped
baselines to check execution. The public five-minute ground truth is never used
to tune, train or select YDSE or any competitor.

## Files and privacy

- `src/possession/`: implemented inference.
- `configs/final.json`: frozen parameters.
- `docs/technical_report.md`: submission technical document.
- `submission/YDSE.pdf`: locally generated three-page version, excluded from Git.
- `reports/`: actual checks, experiment results and outstanding manual actions.
- `research/`: official history, public competitor analysis and source links.
- `scripts/update_github_intelligence.py`: public-only repeatable scan using `gh`.
- `upstream/`: attributed, pinned organiser helpers.

Keep `data/`, `data_staging/`, `private/`, videos, archives, prediction CSVs,
research clones and raw API caches private. They are gitignored. Signed data-use
terms were not supplied, so their review remains a participant responsibility.
The software reads restricted data locally and never sends it to hosted AI.

The public-ready source is prepared locally. Publication and competition upload
require the team's explicit approval. Deadline: **17 November 2026**; the precise
cutoff time and submission URL must be checked in the organiser's email.

## Attribution

Official challenge and scorer: [Metrica Sports](https://github.com/metrica-sports/more-than-a-hack-2027).
Original V1/V2 model code is MIT licensed. V3's small external dead/live head
adapts the public logistic design and IRLS pattern credited, with its MIT notice,
in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). No competitor weights or
predictions were used.
See `upstream/PROVENANCE.md` and the research reports for sources and limitations.

Optional PDF export (not required to reproduce predictions):

```powershell
.venv\Scripts\python -m pip install -r requirements-pdf.txt
.venv\Scripts\python scripts/build_technical_pdf.py
```

## Final investigation and separate V3 candidate

V1/V2 remain preserved. V3 blends a small other-match-trained dead/live head
with V2's D evidence. It improved spellF1 on both newly reserved DFL matches
across all twelve fixed evaluation views; it also increased false D and lowered
direct handover recall. This is external evidence, not a competition score.
The submission of record has not been replaced or published.

Read [final recommendation](reports/final_model_recommendation.md),
[expanded validation](reports/external_validation_expanded.md), and
[V3 technical document](docs/technical_report_v3.md) before selecting a candidate.

```powershell
python -m pytest -q
python scripts/verify_final_candidate.py
```

This verifier creates only `submission/candidates/YDSE_v3.csv` and its reproduced
copy, validates both and checks all sixteen protected V1/V2 artifacts. It needs
the existing local preservation manifest and official data. For a fresh source
checkout without those private historical files, use the single-run V3 commands
in the technical document. The small supplied JSON weights permit inference
without external training-data downloads; see [model provenance](models/README.md).
