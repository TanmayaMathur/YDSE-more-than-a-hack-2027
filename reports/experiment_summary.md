# Executed experiments and tests

Latest unit/contract suite: **21 passed**, 1.64 s. Python compileall also passed.
Tests cover safe ZIP extraction, collision isolation, unsafe Windows paths,
duplicates, symlinks, corrupt ZIPs, expansion limits, parsing/alignment, team mapping,
gap limits and confidence, spike rejection, tactical inversion/N/A, restart
localization, dead/live inference, short possession changes, half separation,
slot-order/team-exchange invariance, strict CSVs and deterministic bytes.
An exhaustive small-sequence check verifies the dynamic program's objective optimum.

The original scorer demo ran on shipped baselines successfully. It was not used
to select our method. No candidate or competitor was ranked on the public labels.

Twenty procedural scenarios, seeds 0–19, each 1,800 frames:

| Method | Synthetic accuracy | Synthetic macroF1 | Synthetic spellF1 |
|---|---:|---:|---:|
| Raw official nearest-player logic | .5905 | .5647 | .3437 |
| Official smooth50 logic | .6345 | .5199 | .5779 |
| YDSE | .8505 | .8401 | .8001 |

These are simulated outcomes, not competition-match scores. The simulator has
simplified geometry, regularized control and stationary stoppages. Real missingness,
referee decisions, aerial play and tagging errors are more difficult. No real-match
quality gain can be inferred quantitatively from this table.

Failures found and corrected: stationary-ball evidence hierarchy and early restart
anchoring on synthetic windows. See execution_log.md. No public ground-truth labels,
manual annotations or competitor predictions were used for either correction.

Advanced vision/external supervised training were not run; no such feature is claimed.
The release candidate was fully generated twice and officially validated, with exact
byte equality. Hardware cost was about 15 seconds and 976 MiB peak working set.
