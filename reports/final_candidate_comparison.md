# Final candidate comparison and recommendation

**Recommended engineering candidate for team review: V2.** It repairs reproducible evidence/sequence-invariance defects and its frozen external point estimates do not regress in the three predeclared conditions. This is not proof that it is the more accurate competition submission. Keep V1 as the unchanged submission of record until the team explicitly chooses to promote a candidate; there is no automatic promotion.

| Item | Preserved V1 | Audit V2 |
|---|---|---|
| CSV | submission/YDSE.csv | submission/candidates/YDSE_v2.csv |
| SHA-256 | 45e91b5246b6a05db7f8b5e034185e0bbd4cf6eab7c9dcc2e4b4d027f369ae35 | 79d4552782eebc37995ccb8603a091518dd45dbcb33cdb7ac93daca714d01f00 |
| Official schema | PASS | PASS, two independent runs |
| Half and pre-kickoff contract | Original published layout | Explicitly verified, including 2,934 D frames |
| Protected artifacts | Original CSV/PDF/Markdown/release metadata/fallback | All six hashes unchanged |
| Predicted H/A spells | 362 | 365 |
| Predicted D segments | 90 | 101 |
| Candidate changes | - | 14,781 labels differ |
| Synthetic holdout mean spellF1 | 0.8060 | 0.8622 |
| Private competition spellF1 | Unknown | Unknown |

Prediction counts, duration percentiles, tag-dominant emissions and weak transition margins are diagnostics only, not accuracy measures or fitting targets. More dead segments can be correct extra stoppages or harmful false splits; the unavailable competition truth does not let us decide. No model was tuned to predicted match counts/durations.

See external_validation.md for actual other-match scores and paired uncertainty, synthetic_stress_tests.md for family failures and accuracy_audit.md for the unresolved dead-ball, wrong-tag, unseen-turnover and short-control limitations.

Exact safe candidate reproduction:
```powershell
.venv\Scripts\python scripts/verify_accuracy_candidate.py
```
This writes only candidate outputs and separate audit metadata. It asserts all protected V1 artifact hashes after both runs. It does not invoke the original overwrite-oriented release command. No repository or submission has been published.
