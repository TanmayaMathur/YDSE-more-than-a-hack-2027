# Exact reproduction

Use the commands in README.md with Python 3.14.3. The official organiser helpers
needed for inference/validation are vendored and pinned; cloning GitHub is not
required to regenerate YDSE.csv.

The complete verification command is:

```powershell
.venv\Scripts\python scripts/verify_release.py --team YDSE
```

It generates `submission/YDSE.csv` and `submission/YDSE_reproduced.csv`, using a
fresh parse for each. It invokes the unmodified official validator and a strict
two-column validator on each file. It requires equality of input hashes,
code/config hashes and final SHA-256. Details stay in `private/`.

To recreate the fallback without the larger official checkout:

```powershell
$env:MTAH_DATA_DIR = 'D:\licensed-data'
.venv\Scripts\python upstream/baseline.py --window 50 --out submission/fallback
.venv\Scripts\python upstream/validate_submission.py submission/fallback/baseline_smooth50.csv
```

No model weights or external services are needed. Inference reads only three tactical
assets. Archive/video integrity metadata from preparation remains private; source
publication must exclude that data and the generated frame-level CSVs.
