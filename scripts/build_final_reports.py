"""Build only the new final-investigation reports from executed experiments."""
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def read(name):return json.loads((ROOT/name).read_text())
def write(name,text):(ROOT/name).write_text(text.strip()+'\n',encoding='utf-8',newline='\n')
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])
def f(value):return f'{value:.4f}'


def main():
    ext=read('reports/external_validation_expanded.json');errors=read('reports/final_external_error_analysis.json')
    dev=read('reports/final_stress_development.json');hold=read('reports/final_stress_holdout.json')
    training=read('reports/final_model_training.json');probe=read('reports/final_failure_probes.json')
    verified=read('private/final_accuracy/candidate_verification.json')
    alignment=read('reports/final_external_alignment.json')
    rows=ext['rows'];lookup={(r['match'],r['condition'],r['variant']):r for r in rows}
    def get(match,condition,variant):return lookup[match,condition,variant]
    scores=[];dead=[];short=[];gap=[];details=[]
    for match in ['J03WQQ','J03WN1']:
        for condition in ['clean','burst1729','burst3253','coordinate_noise','slot_switches','combined']:
            a,b,c=[get(match,condition,v) for v in ['v1','v2','v3']]
            scores.append([match,condition,f(a['spell_f1_mean']),f(b['spell_f1_mean']),f(c['spell_f1_mean']),f(c['spell_f1_mean']-b['spell_f1_mean'])])
            details.append([match,condition,*[f(x['macro_f1']) for x in [a,b,c]],f(c['alive_dead_f1'])])
            if condition.startswith('burst') or condition=='combined':
                gap.append([match,condition,f(b['missing_ball_fraction']),f(b['no_ball_accuracy']),f(c['no_ball_accuracy']),b['hidden_turnovers'],f(b['hidden_turnover_recall_1s']),f(c['hidden_turnover_recall_1s'])])
        for variant in ['v2','v3']:
            r=get(match,'clean',variant)
            dead.append([match,variant,f(r['false_dead_on_live']),f(r['missed_dead']),f(r['dead_onset_f1_1s']),f(r['dead_exit_f1_1s']),r['spurious_spells_at50'],r['missed_spells_at50'],r['excess_fragments_of_long_spells']])
            short.append([match,variant,*[f(r['short_recall'][str(s)]['recall']) for s in [1,2,3]],f(r['turnover_recall_1s'])])
    score_table=table(['Match','Condition','V1 spellF1','V2 spellF1','V3 spellF1','V3 − V2'],scores)
    dead_table=table(['Match','Model','False D / live','Missed D / D','D onset F1 ±1s','D exit F1 ±1s','Spurious spells @.5','Missed spells @.5','Excess long-spell fragments'],dead)
    short_table=table(['Match','Model','Recall <1s','Recall <2s','Recall <3s','Direct H↔A recall ±1s'],short)
    gap_table=table(['Match','Condition','Missing fraction','V2 gap accuracy','V3 gap accuracy','Hidden handovers','V2 hidden recall ±1s','V3 hidden recall ±1s'],gap)
    ablations=table(['Variant','Development spellF1','Frozen holdout spellF1'],[[v,f(dev['summary'][v]['mean_spellF1']),f(hold['summary'][v]['mean_spellF1'])] for v in ['v1','v2','no_tags','no_restarts','no_bridge','dead_cap','learned_dead','blend_dead']])
    means={v:float(np.mean([r['spell_f1_mean'] for r in rows if r['variant']==v])) for v in ['v1','v2','v3']}
    intervals=table(['Match','Condition','Exploratory paired V3−V2 95% range'],[[r['match'],r['condition'],f"[{f(r['paired_v3_minus_v2']['low95'])}, {f(r['paired_v3_minus_v2']['high95'])}]"] for r in errors['rows']])
    write('reports/external_validation_expanded.md',f'''
# Expanded external validation — 14 November 2026

Frozen V3 improves official spellF1 over V2 in all twelve tested views of two
new matches. This is evidence for the dead-ball change, not an estimate of the
competition score. Repeated corruptions are correlated views, not twelve matches.

{score_table}

Unweighted mean across these views: V1 {f(means['v1'])}, V2 {f(means['v2'])},
V3 {f(means['v3'])}. This descriptive mean does not estimate deployment frequencies.
Evaluation took {ext['seconds']:.1f} seconds including XML parsing and local
prediction caching; it is not per-model inference timing.

## Data separation, alignment and licensing

Training/development is **J03WOH**, previously evaluated in the V2 investigation.
It is explicitly no longer untouched holdout. New matches were declared in
`research/final_accuracy/experiment_plan.json` before reading their tracking
outcomes. Candidate source, weights, config and stress generator were frozen
before evaluating either new match; no refit followed these results.

- J03WQQ: Fortuna Düsseldorf–FC St. Pauli, 142,345 frames, 401 reference spells.
  It shares one club with the development match; it is match-disjoint, not fully
  team-disjoint.
- J03WN1: VfL Bochum–Bayer Leverkusen, 141,561 frames, 500 reference spells;
  different teams/stadium from development. Both are 2022/2023, not Barcelona–Athletic.

Attribution: Manuel Bassek, Robert Rein, Hendrik Weber and Daniel Memmert (2025),
[Sportec/DFL dataset](https://doi.org/10.6084/m9.figshare.28196177.v1),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Primary Figshare
metadata verified the licence; all four downloads matched supplied size and MD5.
The external raw files stay outside Git. `final_external_alignment.json` verifies
every ball-frame index and every 40 ms timestamp step independently in each half;
both matches have zero unknown reference frames. Metadata determines home/away.
Centered metre coordinates become normalized coordinates using the 105×68 m pitch.
The [PySport Sportec deserializer](https://github.com/PySport/kloppy/blob/master/kloppy/infra/serializers/tracking/sportec/deserializer.py)
confirms BallStatus=1 means live and BallPossession=1/2 means home/away.

Only X/Y geometry and team IDs enter Tracking. BallStatus and BallPossession
are isolated scoring targets, never inference features. The model receives no
external event annotations or Smart Tagging. Disabling tactical priors on these
matches would be an identical-input check, not an informative tag ablation.

## Perturbations and additional metrics

Clean data has complete ball coordinates, so natural ball-dropout validation is
unavailable here. Burst seeds 1729/3253 use independent two-state missingness,
target fraction .41 and mean missing burst 40 frames. Actual fractions are in
the gap table. Coordinate noise is Gaussian 0.05 m standard deviation, added to
ball and players; it is a small jitter test, not realistic broadcast error.
Slot switches permute IDs within each team every 20 seconds. Combined uses
the separately preregistered seed 14027 for all three perturbations. No reference
labels guide corruption. Crowd-correlated occlusion, false detections and team
ID errors are not reproduced by this experiment.

{table(['Match','Condition','V1 macroF1','V2 macroF1','V3 macroF1','V3 alive/dead F1'],details)}

## Actual possession and boundary errors

{dead_table}

False/missed D are conditional frame error rates. Spurious/missed possessions
use the official one-to-one same-team IoU=.5 matching. Long spells are ≥10s;
the fragmentation count measures additional overlapping same-team predicted
spells, not all possible false splits. Boundary F1 uses a ±1s tolerance.

{short_table}

Short recall uses same-team IoU=.5, so imprecise short boundaries are penalized.
Reference counts for <1/<2/<3s are 37/101/155 (WQQ), 76/171/238 (WN1).
V3 improves aggregate short-spell recall, but it remains poor. Clean short spells
previously matched by V2 were not lost at this threshold; V3 gains 4 and 11
additional <3s matches. Direct H↔A recall nevertheless falls: WQQ loses 3 and
gains 1 matched handover; WN1 loses 13 and gains 1. In 3/3 and 5/13 lost cases,
V3 predicts D within one second. Other losses can reflect boundary displacement
or changed one-to-one matching. These are real regressions, not erased by the
higher spellF1. No correction was tuned on these matches.

{gap_table}

Gap frame accuracy improves, mainly through D recognition. Hidden handover
recall falls in five of these six views; improvement in gap accuracy is not
evidence of better hidden-turnover timing. The combined WN1 view is the exception.

## Uncertainty and definition mismatch

{intervals}

These are 1,000 paired resamples of shared reference spells using fixed prediction
counts, seed 20261114, following the existing scorer-style helper. Within-match
spell dependence, common teams, shared provider, clean tracking and label
conventions remain unaccounted for. They are exploratory ranges, not match-level
or competition confidence intervals. No broad significance claim follows.
DFL provider ownership may retain or change possession differently through
deflections, aerials and contested periods than Metrica's controlled-possession
definition. Its status flags also supply a different stoppage-reference process.
All results are against those provider references, without hand reannotation.

Recommendation: retain the frozen blend as the strongest current candidate for
review, while explicitly tracking increased false D and lost direct handovers.
Do not calibrate on these now-exposed evaluation targets. Raw predictions remain
local; aggregate results are in `external_validation_expanded.json` and
`final_external_error_analysis.json`. Reproduce in a fresh evaluation output
location/check-out; the evaluator refuses to overwrite its recorded outcomes.
''')
    write('reports/dead_ball_failure_analysis.md',f'''
# Dead-ball failure analysis

V3 improves external dead-ball reliability but does not solve stationary-live
ambiguity. Evidence comes from the locked two-match evaluation, the 60-case
frozen artificial holdout and explicit emission/transition probes; no competition
reference labels are involved.

## Responsible features and decoder behavior

`src/possession/v2.py:audit_features` already gates stillness on observed motion
coverage and reliable ball samples. Its dead energy nevertheless includes
`5 × stationary × slow` and `2.6 × missing × slow`, plus outside/restart evidence,
minus activity/live-tag/control quality. The static-pair probe gives mean centre
energies H=2.400, A=−2.400, D=2.800. Accumulating this small D advantage over
seconds beats two .7 transition costs. V2 predicts D from 9.00 to 19.04 seconds
in a true all-live example. This is a feature ambiguity, not just a minimum-dwell bug.

The paired stationary-dead example has exactly the same player/ball arrays and
events but a referee stop from 8–20 seconds. No function of these inputs can
distinguish the two worlds. V3 raises centre D energy to 4.112 and predicts D
from 8.16–19.88: better dead timing, worse live timing. Both models score .1333
on stationary-live and 1.0000 on stationary-dead in the frozen holdout.
A quiet-only dead cap flips those outcomes and leaves their mean unchanged.

## What was implemented and rejected

`learned_dead.py` computes 18 physical features, including player proximity,
stationary/contact interactions, boundary distance, motion coverage and activity.
A small logistic model trained only on another match supplies binary D-vs-live
log odds. `live_dead_experiment.py` blends 50% of this evidence with the existing
D energy, while preserving team geometry, tags, restart timing and decoder costs.
The binary learned energy is relative to the stronger team energy; the resulting
composite is not a calibrated H/A/D probability.

Full learned replacement was rejected before evaluating new matches: it labels
slow goalkeeper and contested loose-ball simulations D, scoring 0 in both.
The blend retains 1.0 on those families and equals V2's mean holdout .8531.
It still misses moving-after-whistle evidence (family spellF1 .8000), whereas
full replacement reaches 1.0 at the cost of those other failures. No approach is
uniformly better on the mechanism tests.

Restart localization in `restarts.py` requires reliable stationary-to-moving
ball support within an automatic SET PIECES interval. It cannot identify the
whistle itself. No-restart ablation changes the suite mean by zero, demonstrating
limited discrimination in these fixtures, not that real restart context is
useless. The new throw-in/corner fixtures had an initial physically inconsistent
receiver; failing tests exposed it and the fixture was corrected before any
holdout outcome. Initial results and revision hashes are preserved.

## External evidence and remaining risks

{dead_table}

Missed-D fractions fall from 54.0%→20.4% and 43.6%→9.1% on clean matches;
false-D/live increases from about .17%→.75% and .20%→.82%. D onset/exit F1
improves, but direct handovers can disappear into D. Increased long-spell
fragmentation on WQQ (5→6) is another measured cost. With combined dropout/noise,
V3 still misses 61.4% and 52.7% of D frames: robustness is incomplete.

An independent referee gesture, local whistle/audio classifier or permitted
automatic event sensor could resolve some ambiguous states. None was trained
or validated here; do not claim those sensors work. Additional team activity
alone cannot distinguish the identical-input pair. Keep this limitation visible,
retain the blend's conservative fallback for unavailable evidence and avoid
stronger D rules without new independent data. See `final_failure_probes.json`,
`final_stress_holdout.json` and the expanded external report for all measurements.
''')
    write('reports/missing_ball_turnover_analysis.md',f'''
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

{gap_table}

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

{short_table}

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
''')
    write('reports/machine_learning_feasibility.md',f'''
# Machine-learning feasibility and executed prototype

A small externally trained LIVE/DEAD head helped the confirmed dead-ball weakness.
No evidence here justifies a large neural training pipeline or claims to solve
unobserved possession histories. The executed model is CPU-only, deterministic
regularized logistic regression, using existing NumPy rather than PyTorch because
the chosen model is a small convex tabular fit.

## Rules and data split

[Current official rules](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/RULES.md)
permit other-game supervised learning and label-free adaptation/pseudo-labels on
the provided match. Human labels on the provided game and public-window tuning
are prohibited. These are different cases. No competition supervision, public
window selection, pseudo-label adaptation or manual corrections enter this work.
The FAQ additionally prohibits restricted-data disclosure to hosted LLMs; all
restricted inference stays local. Signed enrolment terms were not located and
cannot be declared fully verified; see the official guidance report.

J03WOH is explicitly development/training now. Initial prototype trains first
half only and evaluates its correlated second half; that comparison guided the
choice and is not independent validation. Final model uses both development
halves and then locks weights before J03WQQ/J03WN1 evaluation. Neither new match
is used for normalization, fitting, regularization selection or blend tuning.

## Experiments actually run

First-half prototype second-half spellF1 (V2 / full learned / 50% blend): clean
.4163/.5070/.4744, burst1729 .3307/.4549/.3813, 0.05m noise
.3803/.4860/.4166. Full replacement harms goalkeeper and loose-ball artificial
cases, so the conservative blend was selected before new evaluation outcomes.

Final fit: {training['training_frames']:,} rows, one in five frames from both
halves and three label-independent views (clean, burst1729, noise); **18 features,
19 coefficients**, L2=.05, training normalization only, bounded log odds ±5.
Two deterministic fits were exactly equal. Initial training took
{training['seconds']:.2f}s. A later independently invoked retraining to a separate
private path reproduced the canonical weight-file SHA-256 byte for byte.
The model is { (ROOT/'models/ydse_live_dead.json').stat().st_size:,} bytes, not a
GPU checkpoint. The externally trained JSON is shipped with licence/attribution
and source-design credit in `THIRD_PARTY_NOTICES.md`; no competitor weights or
predictions were used. The IRLS design is explicitly credited, not presented as
an invented new learning algorithm.

Features use reliability, stillness, player speed/coverage, outside/boundary
position, control quality/margin, player proximity and interactions. Training
targets are external BallStatus. Inference feature functions accept no labels.
The model falls back to heuristic D energy when neither ball nor player motion
has sufficient support. H/A evidence, costs, minimums, tags and restarts are
unchanged. The .5 blend is a composite energy, not calibrated class probabilities.

Independent clean spellF1 V2→V3 is .4248→.4799 and .3318→.4235; all twelve
corruption views favor V3. Artificial holdout mean remains .8531, equal to V2.
False D and direct-handover regressions remain; see expanded validation.

## Other options assessed, not claimed executed

| Option | Feasibility and missing evidence | Decision |
|---|---|---|
| Self-supervised trajectory encoder | Permitted locally, but anonymous slot discontinuities and no direct D/ownership objective; representation gain alone does not establish spell gain | No neural training attempted |
| Unsupervised HMM/state discovery | Can cluster geometry/motion but state identity need not mean referee-live or controlled ownership; identical static worlds remain ambiguous | Existing duration decoder retained |
| Algorithmic pseudo-labels | Permitted without human correction; can distill and amplify current D/midpoint errors | No pseudo-label model fitted |
| External sequence model/PathCRF | Relevant ball-free interactions, but identity continuity, D mapping, train/evaluation overlap and reproducible weights need audit | Public method inspected; not executed or imported |
| Tracking-confidence learner | Automatic physical signals could supply targets, but no independent correctness labels/calibration demonstrated | Existing coverage gates retained |
| Confidence-adaptive change points | Small CPU prototype was run on development simulations, .8420 mean equals fixed costs | Not adopted |
| Local whistle/referee/video evidence | Potential independent sensor for identical tracking states; suitable annotated training, licensed weights and alignment not verified | Not implemented; no sensor accuracy claimed |

One development match is still a small training population; its corruptions are
not independent samples, and DFL source/semantics are shared across evaluation.
No full posterior calibration, crowded-occlusion model or neural benchmark was
established. The strongest feasible intervention before the deadline is the
small reproducible blend, with its measured tradeoffs documented.

Commands and exact hashes are in `models/README.md` and `docs/technical_report_v3.md`.
Inference never requires network or access to the external evaluation targets.
''')
    write('reports/final_accuracy_investigation.md',f'''
# Final accuracy investigation — YDSE, 14 November 2026

V3 is justified as a separate candidate: an externally trained dead/live evidence
blend improves spellF1 on both newly selected other matches, under every fixed
evaluation condition, without changing V2's team inference or decoder. It is
not automatically promoted. Hidden-turnover timing and stationary-live ambiguity
remain unsolved; direct handover recall and false-D rate regress.

## Preservation and compliance

Started from clean `accuracy-improvement` at
`e329912c9f6db186fb946a1e87d98f173f1c81dc`; work is isolated on
`final-accuracy-investigation`. Sixteen V1/V2 CSVs, reports, configs and private
verification artifacts were hashed and copied before edits. All sixteen remain
unchanged after full V3 generation. V1 hash
`45e91b5246b6a05db7f8b5e034185e0bbd4cf6eab7c9dcc2e4b4d027f369ae35`;
V2 hash `79d4552782eebc37995ccb8603a091518dd45dbcb33cdb7ac93daca714d01f00`.
Original V1/V2 inference modules/configs remain unchanged.

Current RULES/FAQ/CHALLENGE/DATA/EVALUATION/SUBMISSION/scorer were read from
official HEAD `f8f2629`. Label-free provided-match adaptation is permitted,
same-game human supervision is not. V3 trains only on CC BY other-game data.
No supplied-match human annotations, public-window candidate scoring, manual
label corrections or competitor predictions enter these experiments. Restricted
assets and predictions remain local and excluded from Git. Signed terms remain
unverified; the Drive invitation is not sharing permission. See
`research/final_accuracy/rules_and_guidance.md` and `official_recheck.json`.
Official issue/PR/comment queries distinguish successful empty results from
404/unsupported/network failures. No new accessible maintainer conversation
was found. Source-level competitor recheck and MIT attribution are recorded.

## Controlled implementation

Only the D evidence is changed. The small 18-feature logistic head uses external
J03WOH BallStatus, with train-only normalization and L2=.05. A 50% blend with V2
retains coverage fallback and the same H/A emissions, weak bridge, tags, restarts,
costs and minimum durations. First-half prototype validation and development
stress checks preceded source/config/weight lock. J03WOH is no longer holdout.
The full learned replacement was rejected for slow-control regressions.

Source/config/weight hashes and scenario design were frozen before reading
J03WQQ/J03WN1 or synthetic holdout outcomes. A formatting-only pre-evaluation
revision canonicalized LF model bytes and hash normalization for Git portability;
the initial byte lock and unchanged numeric parameters are preserved. No
inference source, parameters or weights changed after new evaluation results.

## Executed evidence

{score_table}

Two matches, twelve correlated views; not a hidden score or competitor ranking.
Definitions, error counts, macroF1, paired ranges and data limitations are in
`external_validation_expanded.md` and its machine-readable JSON.

{ablations}

Forty development and sixty frozen holdout scenarios cover twenty families:
static-live/dead pairs, moving-after-whistle, throw-in, corner, fast restart,
goalkeeper, aerial, loose ball, deflection, short control, long gap, early/late/
multiple hidden turnovers, useful and incorrect tags, duplicate slots, ambiguous
geometry, observation/tempo variation and noisy half boundaries. The no_tags
row disables all phase and restart channels; no_restarts disables restart
channels only. Dead cap is the experimental quiet-only cap. Full learned and
blend share all team evidence. No-bridge tests transition-localization dependence.

Initial restart fixtures lacked consistent receivers and the tag selector
accidentally chose only wrong-tag seeds. Failing tests exposed both fixture
errors; they were corrected **before** new holdout outcomes. Initial reports,
hashes and revision reasons are preserved, so corrected scores are not silently
substituted for the initial runs. Artificial means are diagnostic averages,
not estimates of how often these events occur in matches.

Fifteen additional post-freeze adversarial cases cover identity switches, rapid
controlled turnovers, conflicting tags, outliers and 2m jitter. All three models
score .6568 on rapid turnovers and .2000 on conflicting tags; simple stable
noise/slot/outlier families score 1.0. These are additional diagnostics, not
the preregistered holdout. No model was altered in response.

## Failure mechanisms and decisions

- Stationary tracking cannot determine referee permission in an identical-input
  pair. V3 strengthens D here and cannot be claimed to fix live pauses.
- Hidden opposite-endpoint gaps still use a midpoint prior, with ±5s error in
  early/late examples and unrecovered extra turnovers. No long ball trajectory
  was fabricated. Gap accuracy improvement is mostly D recognition, not timing.
- Fast controls remain vulnerable to integrated switch costs. The strong
  co-motion filter stays excluded; V3 does not lower synthetic short-control
  recall but external direct handover recall declines.
- Useful/incorrect tactical phase priors remain soft, max-pooled and explicitly
  mapped. The tiny balanced-suite no-tag advantage does not justify global removal.
- Development confidence-adaptive costs and shorter dwell minima gave no mean
  gain (.8420 each). A lower fixed cost gave .8595, but was not selected from
  artificial scores or tested/tuned on exposed new matches.

Focused evidence is in `dead_ball_failure_analysis.md`,
`missing_ball_turnover_analysis.md`, `machine_learning_feasibility.md` and
`final_failure_probes.json`. No unsupported claim that every real rapid possession
is preserved follows from these tests.

## Engineering verification and reproduction

71 tests pass, including all prior tests, deterministic learner/schema checks,
target-feature separation, V2-equivalent prepared inference, stationary-input
indistinguishability and V3 block isolation. The optional retraining CLI initially
exposed a missing Path import; it was corrected and rerun successfully to a
separate private file, with the original weight hash reproduced exactly.
All external ball indices and 40ms timestamps passed the independent alignment audit.

Two independent full-match V3 parses/inference runs passed the official CLI
validator and stricter exact-column/index validator. Both have exactly 199,319
rows indexed 0–199318, H/A/D/X only, X outside the published halves and D on all
2,934 required pre-kickoff frames. Output SHA-256:
`{verified['sha256']}`. Run timing/memory and exact commit/input/model hashes
remain in `private/final_accuracy/candidate_verification.json`. Final post-commit
verification records the clean source revision. No original verification file
is replaced. Source hygiene excludes restricted assets and frame predictions.

```powershell
python -m pytest -q
python scripts/verify_final_candidate.py
```

See `docs/technical_report_v3.md` for single-run commands and external evaluation
reproduction. All six requested reports are supplied; original reports/PDFs stay
intact. Recommended candidate and residual risks are stated in
`final_model_recommendation.md`. No publication, submission or promotion occurred.
''')
    write('reports/final_model_recommendation.md',f'''
# Final model recommendation

Recommend **the frozen V3 blend for team review as the strongest current
candidate on the ranking metric**. Keep the submission of record unchanged
until the team approves a final choice. Two new other-match evaluations support
V3, but do not establish a hidden competition score or uniform superiority.

| Criterion | V1 | V2 | V3 |
|---|---|---|---|
| Rule/provenance path | Algorithmic geometry, no same-game labels | Same, audited confidence and tags | Same restrictions; public external labelled training with attribution |
| Exact CSV and deterministic full runs | Preserved PASS | Preserved PASS | Two full runs PASS, identical bytes |
| New clean WQQ spellF1 | .4243 | .4248 | .4799 |
| New clean WN1 spellF1 | .3334 | .3318 | .4235 |
| Twelve-view mean spellF1 | {f(means['v1'])} | {f(means['v2'])} | {f(means['v3'])} |
| New synthetic holdout | .8253 | .8531 | .8531 |
| Stationary-live ambiguity | Unsolved | Unsolved | Unsolved; stronger D prior |
| Hidden-turnover timing | Early tie/persistence risk | Weak midpoint prior | Same midpoint risk; no timing fix |
| Short controlled possessions | Often missed | Often missed | Same synthetic recall; higher clean provider short-spell recall, lower direct-handover recall |
| Complexity | Small deterministic pipeline | Additional confidence/semantic logic | 18-feature CPU head and a 2.5KB JSON parameter file added |

Clean WQQ/WN1 gains are +.0551/+.0917 spellF1. The smallest of twelve gains is
+.0108 (WN1 combined dropout/noise). V3 reduces missed genuine D and improves
dead boundaries but increases false D/live, from .17% to .75% and .20% to .82%
on the clean matches. Direct H↔A recall falls from .2947 to .2881 and .2487 to
.2183. Five of six dropout/combined views regress on hidden handover recall.
No candidate can be called best on
every failure type. The higher ranking-metric evidence favors V3 despite those
documented costs; if the team places extra weight on false-D conservatism,
V2 remains the simpler fallback.

New evidence is only two provider-specific matches; one shares a club with the
training match. Repeated corruptions are correlated, real crowd-related missingness
is not recreated, and Smart Tagging is absent externally. Official hidden-match
performance and superiority over competitors remain unknown. Remaining poor
short-spell recall and unidentifiable gap histories limit football conclusions.
Do not retune on these now-exposed evaluation matches; further model selection
requires a new reserved match or properly separated development data.

V3 CSV: `submission/candidates/YDSE_v3.csv`; reproduced copy beside it.
SHA-256: `{verified['sha256']}`.
Canonical learned-parameter SHA-256:
`{training['model_sha256']}`.
The exact model/config and method are in `docs/technical_report_v3.md`.
V1/V2 artifacts and original technical documents remain byte-identical.

Readiness: technically validated local candidate with reproducible source and
documented training data. Outstanding participant decisions are signed enrolment
terms verification, final candidate approval, exact deadline/delivery instructions,
and whether/when to publish or submit. The Drive invitation is not consent to
hosted processing or redistribution. No external publication, submission or
automatic promotion was performed.
''')
    write('docs/technical_report_v3.md',f'''
# YDSE V3 — separate candidate technical document

V3 adds an externally supervised LIVE/DEAD evidence head to the existing V2
possession detector. Its concrete goal is reducing missed stoppages that join
or misbound genuine H/A possessions. The original V1/V2 files and reports are
preserved; `submission/YDSE.csv` remains the submission of record.

## Inputs, outputs and algorithm

Local official tactical ATD supplies normalized player/ball X/Y and teams;
automatic Smart Tagging supplies weak tactical/restart context. Coordinates are
scaled into metres. Processing is isolated to the official graded halves.
Short ball repairs retain confidence; long gaps get no invented ball coordinates.
V2 deduplicates coincident same-team slots, rejects impossible kinematic jumps,
gates stillness on motion coverage, max-pools semantic team phase evidence and
uses weak two-sided ownership priors across unsupported intervals.

For each frame V2 provides H/A team energy ±s and heuristic D energy d. The new
18-feature head returns clipped D/live log odds z, calculated from reliability,
ball/player motion, control, boundary and interaction features. On supported
frames the new D energy is .5d + .5(|s|+z+restart_delta); otherwise it is d.
The same exact age-state Viterbi decoder integrates emissions per second, using
H/A switch cost 1.1, D cost .7 and minimum durations .32/.32/.64s. No strong
co-motion gate or longer minimum duration is added. Published pre-kickoff D is
enforced by the official frame contract; X is written outside the graded halves.

The composite emissions are scores, not calibrated three-state probabilities.
This model does not solve invisible turnover timing or identify a referee whistle
from static tracking. Automatic tag errors and false D remain material risks.

## Training and attribution

Only J03WOH, Fortuna Düsseldorf–Jahn Regensburg (2022/2023), is used for training.
Its BallStatus labels define D versus live, with no human corrections by YDSE.
Both halves, clean/burst1729/0.05m-noise views and one-in-five frame sampling
produce 82,329 training rows. Standardization uses training data only. L2=.05
logistic IRLS fits 19 coefficients; two fits exactly agree. Training takes about
16s on CPU, and separate retraining reproduced the canonical JSON hash.

Data: Bassek, Rein, Weber and Memmert (2025),
[Sportec/DFL CC BY 4.0 dataset](https://doi.org/10.6084/m9.figshare.28196177.v1).
The small head's public design/IRLS pattern is credited to the MIT-licensed
[stoppage implementation](https://github.com/yassintamer91/more-than-a-hack-2027/blob/906ec8da2e52b1e0c1ade42cd4eca297c0674a2f/solution/stoppage.py);
see `THIRD_PARTY_NOTICES.md`. No competitor weights/predictions or same-game
human labels were used. No provided-match unsupervised training was performed,
although current rules permit it. J03WQQ/J03WN1 are evaluation only, frozen out
before source/config/weight lock. No public-window tuning or hidden labels.

## Evidence and limitations

New clean external spellF1 V2→V3: WQQ .4248→.4799, WN1 .3318→.4235.
All twelve fixed conditions improve spellF1. These are two provider-labelled
matches, one sharing a club with training, not the competition score. Artificial
holdout mean is equal to V2 (.8531, sixty cases). The blend prevents full-head
goalkeeper/loose-ball regressions but does not fix stationary-live ambiguity.
False D/live and direct-handover recall regress externally; short-spell recall
remains weak. Full methods, per-condition results, ablations and uncertainty are
in `reports/final_accuracy_investigation.md` and `reports/external_validation_expanded.md`.

## Reproduction and verification

Use the existing Windows environment or Python with `requirements.txt` (tested
Python 3.14.3, NumPy 2.5.4, pandas 3.1.1). Put official restricted assets in the
existing local data layout; never commit or upload them. Inference is local CPU,
uses the supplied small JSON weights, and requires no external data or network.

```powershell
python scripts/generate_submission.py --model v3 --config configs/audit_v3.json --out submission/candidates/YDSE_v3.csv
python upstream/validate_submission.py submission/candidates/YDSE_v3.csv
python scripts/validate_output.py submission/candidates/YDSE_v3.csv
python scripts/verify_final_candidate.py
python -m pytest -q
```

The generator rejects V3 output paths that would overwrite V1/V2. Full verifier
runs inference twice, both validators, exact 0–199318 indexing, X outside halves,
2,934 pre-kickoff D frames, matching input/code/config/model/output hashes and
all sixteen preservation checks. Private metadata records timings, peak memory,
commit and dirty state. Output hash: `{verified['sha256']}`.
Canonical LF model hash: `{training['model_sha256']}`.
Hash locks normalize text line endings for portable Git checkout verification.
71 tests pass. Format validation is not an official accuracy evaluation.

To reproduce optional training without touching the provided weights:

```powershell
python scripts/fetch_external_dfl.py
python scripts/train_final_dead_model.py --out private/final_accuracy/retrained_model.json --report private/final_accuracy/retrained_model_report.json
```

For external validation, fetch the preselected licensed data and write replay
results to a new private path:

```powershell
python scripts/fetch_final_external.py
python scripts/validate_final_external.py --out private/final_accuracy/external_replay.json
python scripts/audit_final_alignment.py
python scripts/analyze_final_external.py
```

The alignment audit needs adapter caches, created by validation.
`run_final_stress.py --split holdout --model models/ydse_live_dead.json` reproduces
the locked synthetic suite. Existing external evaluation reports are protected
against accidental overwrite; use a separate workspace for a full fresh replay.

No publication, submission or promotion is performed by generation. Signed
participation terms and final delivery instructions remain participant checks.
''')
    print('Built six requested reports and separate V3 technical document from actual results.')


if __name__=='__main__':main()
