# Five engineering opportunities

These opportunities are based on source inspection, not leaderboard claims. See
competitor_comparison.md for commit-pinned evidence. No competitor code was copied.

| Opportunity | Failure mode | Improvement and effort | Independent verification | Decision |
|---|---|---|---|---|
| Preserve short real control without flicker | Majority votes and neighbour merging erase rapid turnovers | Integrate minimum dwell times directly into sequence optimization; medium | Compare decoder to brute-force optimum; synthetic deflection and short-control tests | Implemented |
| Respect missing-position uncertainty | Long interpolation invents contact; missing=dead fragments possessions | Bounded physical repair with confidence decay and neutral long gaps; low | Occlusion lengths, spike/noise tests and same-team retention | Implemented |
| Interpret tactical evidence correctly | Defensive tags invert ownership; correlated tags amplify errors | Defensive polarity and saturated, weak evidence; low | Synthetic defensive/NA/overlap cases | Implemented |
| Localize restart boundaries from motion | Fixed tag windows shift both D and possession boundaries | Stationary-to-moving change inside candidate window, optional anchor only; medium | Known synthetic launch frame; reject all-missing evidence | Implemented |
| Calibrate stoppages on independent matches | Static-ball and player-speed heuristics remain domain-sensitive | External match-disjoint training with realistic dropout; high | Provenance/licence review; held-out match segmentation scoring | Deferred from this freeze; no externally trained weights claimed |

Broadcast global alignment and heavy video inference remain optional future work.
They were not inserted without an independent reliability test. We inspected a
broadcast method with match-specific offset hints, but adopted none of those hints.

The first four opportunities improved implemented behavior in synthetic tests.
Their full-match score benefit is UNVERIFIED. Final parameters were not chosen
against the competition public window or competitors' public-window results.
