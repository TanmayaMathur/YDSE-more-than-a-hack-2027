# Frozen external LIVE/DEAD parameters

`ydse_live_dead.json` contains 18 feature means/scales and 19 logistic
coefficients. Inference needs NumPy and this file; it does not download models,
contact services or require PyTorch/GPU. Training and inference are separate.

Training source: Bassek, Rein, Weber and Memmert (2025), Sportec/DFL,
[CC BY 4.0 dataset](https://doi.org/10.6084/m9.figshare.28196177.v1), match J03WOH
only. Features and labels are documented in `docs/technical_report_v3.md`.
See `THIRD_PARTY_NOTICES.md` for source-design and data attribution.

Canonical LF SHA-256:
`0562bf7f6850030346193e88484439b7aa8e0ffb05d273ec035c76e9cd18e4dd`.
No competition labels or newly selected evaluation matches enter training.

Reproduce training without replacing this file:

```powershell
python scripts/fetch_external_dfl.py
python scripts/train_final_dead_model.py --out private/final_accuracy/retrained_model.json --report private/final_accuracy/retrained_model_report.json
Get-FileHash models/ydse_live_dead.json,private/final_accuracy/retrained_model.json -Algorithm SHA256
```

Two fits are checked for exact equality during training. The provided parameters
are authoritative for CSV reproduction; other numerical-library/platform
versions can change the final bits of floating-point training.
