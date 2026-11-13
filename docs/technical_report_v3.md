# YDSE V3 — separate candidate technical document

V3 adds an externally supervised LIVE/DEAD evidence head to the existing V2
possession detector. Its concrete goal is reducing missed stoppages that join
or misbound genuine H/A possessions. The original V1/V2 files and reports are
preserved; `submission/YDSE.csv` remains the submission of record.

## Inputs, outputs and algorithm

Local official tactical ATD supplies normalized player/ball X/Y and teams;
automatic Smart Tagging supplies weak tactical/restart context. Coordinates are
scaled into metres. Processing is isolated to the official graded halves.
Short ball repairs retain confidence; long gaps get no invented ball coordinates.
V2 deduplicates coincident same-team slots, rejects impossible kinematic jumps,
gates stillness on motion coverage, max-pools semantic team phase evidence and
uses weak two-sided ownership priors across unsupported intervals.

For each frame V2 provides H/A team energy ±s and heuristic D energy d. The new
18-feature head returns clipped D/live log odds z, calculated from reliability,
ball/player motion, control, boundary and interaction features. On supported
frames the new D energy is .5d + .5(|s|+z+restart_delta); otherwise it is d.
The same exact age-state Viterbi decoder integrates emissions per second, using
H/A switch cost 1.1, D cost .7 and minimum durations .32/.32/.64s. No strong
co-motion gate or longer minimum duration is added. Published pre-kickoff D is
enforced by the official frame contract; X is written outside the graded halves.

The composite emissions are scores, not calibrated three-state probabilities.
This model does not solve invisible turnover timing or identify a referee whistle
from static tracking. Automatic tag errors and false D remain material risks.

## Training and attribution

Only J03WOH, Fortuna Düsseldorf–Jahn Regensburg (2022/2023), is used for training.
Its BallStatus labels define D versus live, with no human corrections by YDSE.
Both halves, clean/burst1729/0.05m-noise views and one-in-five frame sampling
produce 82,329 training rows. Standardization uses training data only. L2=.05
logistic IRLS fits 19 coefficients; two fits exactly agree. Training takes about
16s on CPU, and separate retraining reproduced the canonical JSON hash.

Data: Bassek, Rein, Weber and Memmert (2025),
[Sportec/DFL CC BY 4.0 dataset](https://doi.org/10.6084/m9.figshare.28196177.v1).
The small head's public design/IRLS pattern is credited to the MIT-licensed
[stoppage implementation](https://github.com/yassintamer91/more-than-a-hack-2027/blob/906ec8da2e52b1e0c1ade42cd4eca297c0674a2f/solution/stoppage.py);
see `THIRD_PARTY_NOTICES.md`. No competitor weights/predictions or same-game
human labels were used. No provided-match unsupervised training was performed,
although current rules permit it. J03WQQ/J03WN1 are evaluation only, frozen out
before source/config/weight lock. No public-window tuning or hidden labels.

## Evidence and limitations

New clean external spellF1 V2→V3: WQQ .4248→.4799, WN1 .3318→.4235.
All twelve fixed conditions improve spellF1. These are two provider-labelled
matches, one sharing a club with training, not the competition score. Artificial
holdout mean is equal to V2 (.8531, sixty cases). The blend prevents full-head
goalkeeper/loose-ball regressions but does not fix stationary-live ambiguity.
False D/live and direct-handover recall regress externally; short-spell recall
remains weak. Full methods, per-condition results, ablations and uncertainty are
in `reports/final_accuracy_investigation.md` and `reports/external_validation_expanded.md`.

## Reproduction and verification

Use the existing Windows environment or Python with `requirements.txt` (tested
Python 3.14.3, NumPy 2.5.4, pandas 3.1.1). Put official restricted assets in the
existing local data layout; never commit or upload them. Inference is local CPU,
uses the supplied small JSON weights, and requires no external data or network.

```powershell
python scripts/generate_submission.py --model v3 --config configs/audit_v3.json --out submission/candidates/YDSE_v3.csv
python upstream/validate_submission.py submission/candidates/YDSE_v3.csv
python scripts/validate_output.py submission/candidates/YDSE_v3.csv
python scripts/verify_final_candidate.py
python -m pytest -q
```

The generator rejects V3 output paths that would overwrite V1/V2. Full verifier
runs inference twice, both validators, exact 0–199318 indexing, X outside halves,
2,934 pre-kickoff D frames, matching input/code/config/model/output hashes and
all sixteen preservation checks. Private metadata records timings, peak memory,
commit and dirty state. Output hash: `3a27d7d90657d1e4b9485007f0d7ea1d95ac662a64d4a3fbe5c1b50daf4ef534`.
Canonical LF model hash: `0562bf7f6850030346193e88484439b7aa8e0ffb05d273ec035c76e9cd18e4dd`.
Hash locks normalize text line endings for portable Git checkout verification.
71 tests pass. Format validation is not an official accuracy evaluation.

To reproduce optional training without touching the provided weights:

```powershell
python scripts/fetch_external_dfl.py
python scripts/train_final_dead_model.py --out private/final_accuracy/retrained_model.json --report private/final_accuracy/retrained_model_report.json
```

For external validation, fetch the preselected licensed data and write replay
results to a new private path:

```powershell
python scripts/fetch_final_external.py
python scripts/validate_final_external.py --out private/final_accuracy/external_replay.json
python scripts/audit_final_alignment.py
python scripts/analyze_final_external.py
```

The alignment audit needs adapter caches, created by validation.
`run_final_stress.py --split holdout --model models/ydse_live_dead.json` reproduces
the locked synthetic suite. Existing external evaluation reports are protected
against accidental overwrite; use a separate workspace for a full fresh replay.

No publication, submission or promotion is performed by generation. Signed
participation terms and final delivery instructions remain participant checks.
