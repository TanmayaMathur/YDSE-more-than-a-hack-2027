# Validation report — YDSE

Executed on 14 November 2026 (Asia/Kolkata). Final output:
`submission/YDSE.csv`.

| Check | Actual result |
|---|---|
| Data rows | 199,319 |
| Frame IDs | 0 through 199318, complete and ordered |
| Header/columns | Exactly frame,label |
| Labels/blanks | H/A/D/X only; no blanks |
| Official validation function | PASS |
| Unmodified official validator CLI | PASS |
| Stricter exact-column check | PASS |
| Independent regeneration | Identical bytes, PASS |
| SHA-256 | 45e91b5246b6a05db7f8b5e034185e0bbd4cf6eab7c9dcc2e4b4d027f369ae35 |

Prediction diagnostics: H 79,788; A 53,531; D 25,538; X 40,462.
The X count exactly matches ungraded frames. The official validator reports 362
predicted possessions of mean 14.7 s. These are prediction descriptions, not
ground-truth quantities, accuracy measurements or targets used to tune the model.

The fallback `submission/fallback/baseline_smooth50.csv` was generated independently
using the original official baseline and passed the official validator. Its
checksums and the exact final runs are recorded locally in the reproduction record.

Validation is format correctness only. No full-match spellF1 or hidden score is
available. The generated CSV was not manually edited.
