# Missing-ball and controlled-turnover analysis

V3 leaves V2's hidden-team timing model unchanged. It improves gap frame accuracy
through the D head, but there is no demonstrated improvement in hidden H↔A
transition localization. This distinction is essential for complete possession spells.

## Confirmed midpoint failure

`v2.py:gap_evidence` uses .6s sustained confident observations on either side
of an entirely unsupported interval. Same owners get a weak .2 persistence prior;
opposite owners get a weak symmetric ramp. No ball coordinates are filled across
the long interval. In the probe the unsupported bracket is [9,21] seconds:

| Hidden truth | V2/V3 predicted handover | Error |
|---|---|---|
| H→A at 10s | H→A at 15s | +5s |
| H→A at 20s | H→A at 15s | −5s |
| H→A at 11s, A→H at 15s, H→A at 19s | One H→A at 15s | Two turnovers unrecovered; direction of middle event differs |

The three examples share observed input histories. The midpoint is a symmetric
timing prior and can minimize worst-case location error with an unknown single
transition; it is not a detected event. It cannot reconstruct multiple turnovers.
Backward use of the recovery endpoint improves the previous arbitrary early
tie in some cases, but does not add an interior observation. The bracket must
be interpreted as uncertainty. Long same-owner gaps can hide whole opposing
spells too. No evidence supports a more precise universally correct boundary.

Frozen holdout: V1/V2/V3 early-gap spellF1 is 1.000/.900/.900; late-gap is
.400/.900/.900; multiple-gap is .5333/.6667/.6667. No-bridge V2 reverts to the
V1 means here and its overall mean falls from .8531 to .8253. The prior helps
this balanced diagnostic but is not universally accurate. Long no-turnover gaps
remain 1.0. Artificial labels are not a hidden-match accuracy estimate.

## Evidence-aware timing and tactical context

The current decoder already integrates weak two-sided bridge scores with real
visible control, localized restarts and automatic phase votes over the whole
half. Strong supported observations or useful phase evidence can override the
weak bridge; no fabricated long trajectory or fixed frame-specific correction
was added. A new event-localizer without an independent interior cue would only
replace one timing assumption with another. It was not promoted as an improvement.
Possible next work is a separately evaluated ball-free player-interaction model
or permitted local video sensor, with explicit uncertainty rather than false precision.

Tag semantics remain unchanged in V3: BUILD UP/PROGRESSION/CREATING CHANCES vote
for the named team; final-third/box/long-ball phases are weaker. Defending-third
phases weakly vote for the other team. ATTACKING TRANSITION, DEFENSIVE TRANSITION,
PLAYERS IN THE BOX and GOALS do not establish control. SET PIECES supplies restart
context, not ownership of the entire phase. Unknown/missing teams contribute no
ownership vote. Duplicated/correlated phase votes use max pooling rather than
unlimited accumulation. Incorrect primary phases can still dominate a hidden gap.

The revised tag diagnostic includes both a useful hidden away phase and an
incorrect away phase on every seed, plus an ambiguous defensive-transition tag.
A test caught an initial seed-modulo imbalance; it was fixed before holdout.
Holdout tag-family spellF1 is .4889 with tags vs .5000 without all tags/restarts;
the means over all families are .8531 and .8537. This tiny artificial difference
does not justify removing all automatic tagging. External DFL inputs have no
equivalent automatic phases, so they cannot validate competition tag calibration.

## Actual external gap results

| Match | Condition | Missing fraction | V2 gap accuracy | V3 gap accuracy | Hidden handovers | V2 hidden recall ±1s | V3 hidden recall ±1s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J03WQQ | burst1729 | 0.4029 | 0.6494 | 0.7300 | 125 | 0.1040 | 0.0880 |
| J03WQQ | burst3253 | 0.4004 | 0.6422 | 0.7219 | 131 | 0.1221 | 0.1145 |
| J03WQQ | combined | 0.4105 | 0.5008 | 0.6479 | 114 | 0.1491 | 0.1404 |
| J03WN1 | burst1729 | 0.4026 | 0.5789 | 0.7349 | 143 | 0.0699 | 0.0490 |
| J03WN1 | burst3253 | 0.4007 | 0.5996 | 0.7297 | 155 | 0.0581 | 0.0516 |
| J03WN1 | combined | 0.4088 | 0.4374 | 0.6090 | 171 | 0.0936 | 0.0994 |

These are artificial missing intervals in otherwise complete provider tracking.
They are not observed real occlusion histories. Hidden handover recall worsens
in five of six views even though gap accuracy improves. V3 is not a solution to
hidden possession recovery, and learned D evidence sometimes obscures a handover.

## Controlled reception, contacts and duration

V3 preserves V2 team evidence and minimum dwell times; it does not equate nearest
player identity with control, and does not reintroduce the rejected strong
co-motion gate. Held-out deflection and aerial families retain 1.0, but the short
control family is only .5333. A development 0.68s away control is missed by both
V2/V3. Team-switch evidence must pay two 1.1 costs to introduce a short opposing
spell; sustained possession evidence may be insufficient even when the .32s
minimum itself permits that spell. A hard minimum is not the sole source of loss.

The additional frozen-model diagnostic gives identical V1/V2/V3 rapid-turnover
spellF1 .6568, and conflicting-primary-phase spellF1 .2000. Strong 2m noise,
slot permutations and outlier tests on simple stable-control examples score
1.0; those easy families do not prove robustness during noisy real turnovers.

| Match | Model | Recall <1s | Recall <2s | Recall <3s | Direct H↔A recall ±1s |
| --- | --- | --- | --- | --- | --- |
| J03WQQ | v2 | 0.0000 | 0.0099 | 0.0452 | 0.2947 |
| J03WQQ | v3 | 0.0000 | 0.0297 | 0.0710 | 0.2881 |
| J03WN1 | v2 | 0.0132 | 0.0234 | 0.0420 | 0.2487 |
| J03WN1 | v3 | 0.0263 | 0.0526 | 0.0882 | 0.2183 |

Real provider short-spell recall remains very low. On clean data V3 gains 4/11
matched <3s spells with no losses of V2-matched short spells at IoU=.5, but loses
other direct handover matches. Therefore preservation on artificial cases is a
limited safeguard, not proof that every genuine fast turnover survives.

## Transition-cost investigation

The duration decoder uses time-normalized emissions (division by FPS), costs
1.1 H↔A and .7 to/from D, and minimums .32/.32/.64 seconds. Age states enforce
internal minimums; half edges can truncate a dwell and blocks decode independently.
`probe_final_failures.py` executes development-only fixed ±25% cost, shorter-dwell
and confidence-adaptive prototypes. Mean spellF1: fixed .8420, lower cost .8595,
higher cost .8420, shorter minimum .8420, adaptive .8420. Adaptive costs range
from .75× to 1.25× based on current team margin; this particular prototype adds
complexity without a mean gain. Lower-cost synthetic gain is not sufficient
external evidence to retune the frozen candidate. No post-evaluation search or
match-specific switching constants were adopted. Next development must reserve
new independent matches if these hypotheses are used for selection.
