# Demonstrated failures, limits and fixes

## Demonstrated and repaired mechanisms

- Ungraded observations influence global rolling features even though decoding itself resets.
- A single tracked player is incorrectly treated as collective motion evidence.
- Tiny nonzero repair confidence becomes full-strength stationary-ball evidence.
- Exact duplicate slots count as independent observations.
- Raw differentiated noise creates apparent player motion during a true static configuration.
- Ambiguous transition/occupancy tags can create spurious ownership in long gaps.
- Relative config paths break reproduction metadata after a candidate file is written.

Focused probes and tests establish these mechanisms independently of any match labels.
The candidate fixes are documented by source in implementation_audit.md.

## Demonstrated but not universally solvable

**Invisible turnover:** endpoint evidence establishes different owners but cannot say
when the hidden handover occurred. V1 chooses the gap start by tie behavior. V2's weak
symmetry prior moves an otherwise unconstrained switch near the midpoint. It can be
worse when the real switch was near an edge, when multiple hidden turnovers occur,
or when a hidden stoppage intervenes. No ball coordinates are invented for that interval.

**Stationary live pause versus whistle:** the same complete geometry can describe
waiting with a live ball or a real stoppage. The noiseless paired construction is
incorrectly D throughout its central live-pause interval in both versions. Additional
tags or an independent referee/restart observation are needed; more smoothing cannot
identify permission to play. Conversely, a foul can leave actors moving and produce
no immediate geometric stoppage signal. These remain important risks.

**Wrong primary tactical phase:** a deliberately incorrect long BUILD UP phase can
overrule uncertain geometry during an occlusion. Removing all tags wins on the
adversarial suite's intentionally wrong-tag cases; that is not evidence that all
automatic tactical information is harmful in normal play. The candidate retains
the bounded primary phase prior and discloses this failure.

**Brief real control:** fixed switch costs and dwell constraints still remove some
short, weakly observed legitimate possessions. The experimental stronger co-motion
gate made this worse and is excluded. No multi-second minimum was introduced.

**Aerial challenges/deflections:** high speed weakens proximity evidence, but planar
tracking cannot establish actual contact or control in every duel. The family tests
include both passes past opponents and genuine quick control; good performance on
one does not establish a perfect classifier for the other.

## Why simple dead-cue changes were not promoted

An experimental cap on quiet-only dead evidence protects stationary live play but
can miss a genuinely untagged quiet stoppage with identical observations. The dead
terms share input causes and must not be read as independent likelihood factors.
No learned/calibrated LIVE/DEAD posterior is claimed. Independent annotated validation
is more useful than selecting a new coefficient from synthetic spellF1 alone.
