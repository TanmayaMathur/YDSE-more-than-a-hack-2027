# Controlled ablations

The original V1 path is unchanged. V2 always scopes operations to graded blocks. The reliability-only ablation adds deduplication, motion coverage, short-window player kinematics and stationary reliability. Other rows disable one named candidate component.

| Configuration | Dev spellF1 | Holdout spellF1 |
|---|---:|---:|
| v1 | 0.7650 | 0.8060 |
| v2 | 0.8212 | 0.8622 |
| reliability_only | 0.7650 | 0.8060 |
| no_tags | 0.8712 | 0.9122 |
| no_restarts | 0.8212 | 0.8622 |
| no_gap_bridge | 0.8150 | 0.8560 |
| experimental_contact_gate | 0.8062 | 0.8225 |
| old_semantics | 0.7712 | 0.8122 |
| conservative_dead | 0.8212 | 0.8622 |
| cost_minus25 | 0.8672 | 0.8854 |
| cost_plus25 | 0.8100 | 0.8398 |

Interpretation:
- Reliability-only produces no mean score gain on this suite, despite repairing demonstrated invariants. This distinction is intentional: correctness evidence is not an accuracy estimate.
- Explicit tag semantics prevent the designed ambiguous-phase failure; incorrect strong primary phases remain a risk.
- Weak two-sided ownership bridges improve the constructed midpoint turnover cases, but impose an uncertain timing prior and can be wrong for edge-of-gap turnovers.
- The stronger co-motion gate is excluded: its development prototype reduced rapid-turnover family spellF1 from .550 to .281 without helping the incidental-touch family. It remains an experimental ablation only.
- Restart removal changes no mean on these sparse synthetic cases; this is lack of discriminating test evidence, not proof restart cues are useless.
- The quiet-only dead cap remains experimental; identical static observations can encode opposite referee states. It was not adopted.
- +/-25% cost sensitivity changes the outputs materially. Costs 1.1/.7 and dwell times .32/.32/.64 remain fixed; lower-cost synthetic scores did not select parameters.

No factorial claim is made: components can interact. No provided five-minute labels or competitor scores were loaded or used. No post-holdout parameter search was performed.
