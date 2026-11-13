# Targeted public-method recheck, 14 November 2026

The prior 401-candidate inventory and seven source reviews are preserved.
This pass revisits methods that address confirmed failures; it does not claim
a fresh exhaustive GitHub census or comparable competitor performance.

| Primary source | Verified mechanism | Decision |
|---|---|---|
| [yassintamer91 stoppage.py](https://github.com/yassintamer91/more-than-a-hack-2027/blob/906ec8da2e52b1e0c1ade42cd4eca297c0674a2f/solution/stoppage.py) | Small external LIVE/DEAD logistic head; stationary/contact interaction features, coverage gates, regularized IRLS | Concrete precedent for V3. Credit the adapted public design and fitting pattern in THIRD_PARTY_NOTICES.md, retain MIT notice, train our own weights/features. |
| [hnfadtya augment.py](https://github.com/hnfadtya/more-than-a-hack-2027/blob/6f15add056f5b937e5154295fb70e21ebf82ed9f/mtah/augment.py) | Bursty missingness, coordinate corruption, team swap and crowd/air dropout for external training | Supports robustness testing, not a claim that independent random missingness matches tackle/aerial occlusion. No code, weights or predictions imported. |
| [PathCRF official repository](https://github.com/hyunsungkim-ds/pathcrf/tree/1b7c6f85a6b78c92e4543fde72ca2b86a933f997), [paper](https://arxiv.org/abs/2602.12080) | Set-attention trajectory interactions and CRF edge paths for ball-free events; seven-match Sportec workflow and supplied checkpoints | Relevant missing-ball specialist, but player identity continuity, edge-to-team/D semantics and training-split overlap must be audited before reuse. Not run, no weights copied, no performance claim. |

Current competitor HEADs remain `906ec8d` and `6f15add`; PathCRF HEAD is
`1b7c6f8`. Source was fetched again. Viterbi/HSMM alternatives and restart
detectors in the preserved `research/competitor_comparison.md` remain useful
comparators: explicit durations prevent flicker but do not create missing
transition observations. An additional confidence-adaptive decoder was actually
tested on development simulations, with no mean improvement (see final report).

No competitor submission CSV, private weights or same-game human labels were
downloaded or used. No claim of superiority over competitors is supported by
these inspections. Generic source inspiration is distinguished from a reproduced
model. The new fitting design attribution is explicit; the historical V1/V2
no-reuse statements do not describe the new V3 head.
