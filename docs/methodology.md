# Methodology and decision provenance

The implemented method is fully described in technical_report.md. Parameters
were fixed from physical plausibility and synthetic mechanisms, not competition
labels. The first complete candidate was already runnable before advanced source
research was finished. The official smooth50 output was kept as the fallback.

Implementation progression:

1. V0: original official baseline, executed and validated.
2. V1/V2: metre-based team geometry and bounded confidence-aware ball repair.
3. V3: saturated automatic phase priors with defensive inversion and N/A handling.
4. V4: exact expanded-state duration-constrained inference.
5. V5: motion-supported restart localization and full-resolution decoded boundaries.

These are implemented components, not separately ranked competition entries.
No V1–V5 scores against the provided labels were calculated or used for selection.
Heavy vision, a trained TCN, Kalman long-gap extrapolation and external supervised
calibration were not implemented. Source reviews of such methods are research,
not claims they exist in YDSE.

Synthetic testing found two issues: stationary-ball dead evidence could be outweighed
by possession proximity, and a moving-window restart contrast could anchor before
the actual launch. The former was fixed by strengthening corroborated stationary
evidence; the latter by including before/after state purity. Both fixes were based
on artificial sequences with known construction, not manual labels of the match.

The official scorer demo's baseline rankings were not used to pick a smoothing
window. The fallback is the organiser's published smooth50 variant. Competitor
comments that describe public-window tuning were recorded as provenance concerns
and excluded from parameter selection. No organiser disqualification is inferred.
