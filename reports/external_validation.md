# Independent other-match validation

Frozen candidate evaluated on J03WOH: Fortuna Duesseldorf versus SSV Jahn Regensburg, 2022/2023, not the competition game. Selected as the smallest tracking XML before examining outcomes. Primary Figshare licence is CC BY 4.0; download size and MD5 verified.

Attribution: Manuel Bassek, Robert Rein, Hendrik Weber and Daniel Memmert (2025), [An integrated dataset of spatiotemporal and event data in elite soccer](https://doi.org/10.6084/m9.figshare.28196177.v1).

Parsed 137,214 frames at 25 FPS, 39 player slots, 105 x 68 m pitch, two independently decoded periods. BallStatus/BallPossession are evaluation targets only. Coordinates are converted from centered metres to normalized pitch coordinates. Source coding is checked against the public PySport Sportec implementation and the observed schema.

No phase/event labels are given to either model. No weights are trained. A test changes the target ownership attributes and verifies Tracking inputs stay identical. Dropout is an independent two-state Markov process, target .41 missing probability and mean 40-frame burst; seeds fixed in external_validation_plan.json before reading outcomes.

| Condition | V1 spellF1 | V2 spellF1 | V1 macroF1 | V2 macroF1 | Delta spellF1, exploratory paired 95% interval |
|---|---:|---:|---:|---:|---|
| clean | 0.3949 | 0.3972 | 0.6762 | 0.6782 | +0.0023, [-0.0011, +0.0069] |
| bursty_ball_missing_seed1729 | 0.2883 | 0.2985 | 0.6164 | 0.6340 | +0.0102, [+0.0005, +0.0198] |
| bursty_ball_missing_seed3253 | 0.3035 | 0.3124 | 0.6269 | 0.6373 | +0.0089, [-0.0032, +0.0204] |

All three point estimates favor V2, but two paired intervals include zero. The intervals resample shared GT spells with prediction counts fixed, using 1,000 draws; they are exploratory within-match uncertainty measures, not multi-match generalization bounds. The two corruption seeds are repeated views of the same match, not independent matches.

Important limits: provider ownership semantics may differ from Metrica controlled possession; these are provider-defined reference attributes, not independently re-annotated gold truth. Stable player identities, clean coordinates, absence of automatic tactical tags and artificial missingness differ from the competition. No competition score, rank or superiority over its official baseline is inferred. No parameters changed after external results.
