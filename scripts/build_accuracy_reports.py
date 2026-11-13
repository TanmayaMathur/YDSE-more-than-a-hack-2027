"""Compile executed audit results. No raw restricted assets are read."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def put(name,text):(ROOT/name).write_text(text.strip()+'\n',encoding='utf-8')

def main():
    dev=read('reports/accuracy_stress_development.json');hold=read('reports/accuracy_stress_holdout.json')
    match=read('reports/accuracy_match_aggregates.json');ext=read('reports/external_dfl_validation.json')
    release=read('private/accuracy_audit/candidate_verification.json')
    old=read('private/accuracy_audit/v1_preserved/manifest.json')
    h1=next(x['sha256'] for x in old['files'] if x['path']=='submission/YDSE.csv')
    summary=['# Synthetic stress tests - accuracy audit','',
        'Executed 64 development scenarios and 128 frozen holdout scenarios, each 30 seconds at 25 FPS, '
        'across 16 families and 11 configurations (2,112 final-protocol model runs). '
        'The initial stronger-contact prototype also ran on development cases and is preserved separately.',
        '', 'Families/holdout seeds were recorded in design_freeze.json before development; '
        'v2.py/config were frozen before the holdout run. No model change followed holdout or external outcomes.',
        '', '| Family | V1 dev | V2 dev | V1 holdout | V2 holdout |','|---|---:|---:|---:|---:|']
    for family in hold['summary']['v1']['family_spellF1']:
        vals=[dev['summary'][m]['family_spellF1'][family] for m in ['v1','v2']]+[hold['summary'][m]['family_spellF1'][family] for m in ['v1','v2']]
        summary.append('| '+family+' | '+' | '.join(f'{v:.4f}' for v in vals)+' |')
    summary+=['',f'Unweighted family/case means: development V1 {dev["summary"]["v1"]["mean_spellF1"]:.4f}, '
              f'V2 {dev["summary"]["v2"]["mean_spellF1"]:.4f}; holdout V1 {hold["summary"]["v1"]["mean_spellF1"]:.4f}, '
              f'V2 {hold["summary"]["v2"]["mean_spellF1"]:.4f}.',
              '', 'Scores use the actual official library. Each case records predicted transition frames/types, '
              'false/missed D rates, missed/spurious spells and failure types in accuracy_stress_*.json. '
              'Synthetic transition traces are public artificial data; match transition traces are private.',
              '', 'Most score gain comes from the ambiguous-tag and hidden-turnover constructions. Many other '
              'families are unchanged, and short control, crowds and wrong primary phases still fail. '
              'The noiseless stationary-live counterexample is separately recorded in audit_probes.json '
              'and fails in both versions. Passing its noisy family does not solve the identifiability problem.',
              '', 'The scenario mix is deliberately adversarial, not a football sampling distribution. '
              'Its tag-bearing cases disproportionately contain incorrect/ambiguous tags. Therefore the '
              'no-tags ablation has an artificial advantage and is not grounds to discard all tagging. '
              'Larger holdout coordinate noise is one distribution shift, not a substitute for independent matches. '
              'No statistical or competition ranking conclusion is drawn from these averages.']
    put('reports/synthetic_stress_tests.md','\n'.join(summary))
    ablation=['# Controlled ablations','',
        'The original V1 path is unchanged. V2 always scopes operations to graded blocks. '
        'The reliability-only ablation adds deduplication, motion coverage, short-window player '
        'kinematics and stationary reliability. Other rows disable one named candidate component.',
        '', '| Configuration | Dev spellF1 | Holdout spellF1 |','|---|---:|---:|']
    for name in hold['summary']:
        ablation.append(f'| {name} | {dev["summary"][name]["mean_spellF1"]:.4f} | {hold["summary"][name]["mean_spellF1"]:.4f} |')
    ablation+=['', 'Interpretation:',
        '- Reliability-only produces no mean score gain on this suite, despite repairing demonstrated invariants. This distinction is intentional: correctness evidence is not an accuracy estimate.',
        '- Explicit tag semantics prevent the designed ambiguous-phase failure; incorrect strong primary phases remain a risk.',
        '- Weak two-sided ownership bridges improve the constructed midpoint turnover cases, but impose an uncertain timing prior and can be wrong for edge-of-gap turnovers.',
        '- The stronger co-motion gate is excluded: its development prototype reduced rapid-turnover family spellF1 from .550 to .281 without helping the incidental-touch family. It remains an experimental ablation only.',
        '- Restart removal changes no mean on these sparse synthetic cases; this is lack of discriminating test evidence, not proof restart cues are useless.',
        '- The quiet-only dead cap remains experimental; identical static observations can encode opposite referee states. It was not adopted.',
        '- +/-25% cost sensitivity changes the outputs materially. Costs 1.1/.7 and dwell times .32/.32/.64 remain fixed; lower-cost synthetic scores did not select parameters.',
        '', 'No factorial claim is made: components can interact. No provided five-minute labels or competitor '
        'scores were loaded or used. No post-holdout parameter search was performed.']
    put('reports/ablation_study.md','\n'.join(ablation))
    erows=['# Independent other-match validation','',
        'Frozen candidate evaluated on J03WOH: Fortuna Duesseldorf versus SSV Jahn Regensburg, '
        '2022/2023, not the competition game. Selected as the smallest tracking XML before '
        'examining outcomes. Primary Figshare licence is CC BY 4.0; download size and MD5 verified.',
        '', 'Attribution: Manuel Bassek, Robert Rein, Hendrik Weber and Daniel Memmert (2025), '
        '[An integrated dataset of spatiotemporal and event data in elite soccer](https://doi.org/10.6084/m9.figshare.28196177.v1).',
        '', f'Parsed {ext["provenance"]["rows"]:,} frames at 25 FPS, 39 player slots, 105 x 68 m pitch, '
        'two independently decoded periods. BallStatus/BallPossession are evaluation targets only. '
        'Coordinates are converted from centered metres to normalized pitch coordinates. '
        'Source coding is checked against the public PySport Sportec implementation and the observed schema.',
        '', 'No phase/event labels are given to either model. No weights are trained. A test changes the '
        'target ownership attributes and verifies Tracking inputs stay identical. Dropout is an independent '
        'two-state Markov process, target .41 missing probability and mean 40-frame burst; seeds fixed in '
        'external_validation_plan.json before reading outcomes.',
        '', '| Condition | V1 spellF1 | V2 spellF1 | V1 macroF1 | V2 macroF1 | Delta spellF1, exploratory paired 95% interval |',
        '|---|---:|---:|---:|---:|---|']
    for condition in ext['paired_intervals']:
        a=next(r for r in ext['results'] if r['condition']==condition and r['model']=='v1')
        b=next(r for r in ext['results'] if r['condition']==condition and r['model']=='v2')
        ci=ext['paired_intervals'][condition]
        erows.append(f'| {condition} | {a["spell_f1_mean"]:.4f} | {b["spell_f1_mean"]:.4f} | {a["macro_f1"]:.4f} | {b["macro_f1"]:.4f} | '
                     f'{b["spell_f1_mean"]-a["spell_f1_mean"]:+.4f}, [{ci["delta_v2_minus_v1_low95"]:+.4f}, {ci["delta_v2_minus_v1_high95"]:+.4f}] |')
    erows+=['', 'All three point estimates favor V2, but two paired intervals include zero. '
        'The intervals resample shared GT spells with prediction counts fixed, using 1,000 draws; '
        'they are exploratory within-match uncertainty measures, not multi-match generalization bounds. '
        'The two corruption seeds are repeated views of the same match, not independent matches.',
        '', 'Important limits: provider ownership semantics may differ from Metrica controlled possession; '
        'these are provider-defined reference attributes, not independently re-annotated gold truth. '
        'Stable player identities, clean coordinates, absence of automatic tactical tags and artificial '
        'missingness differ from the competition. No competition score, rank or superiority over its '
        'official baseline is inferred. No parameters changed after external results.']
    put('reports/external_validation.md','\n'.join(erows))
    put('reports/improvement_summary.md','''# Implemented improvements and rejected changes

| Change/source | Original limitation and evidence | Candidate method | Verification | Risk / included? |
|---|---|---|---|---|
| v2.infer, clipped_events | .6378 slow-score change from ungraded-only input edits | All repair/features/events/restarts scoped per graded block | Boundary invariance test; full-match contract | Short edge windows have less evidence; included |
| v2.audit_features | Single static tracked player became collective slow=1; .01 reliability became stationary=1 | Coverage-gated collective evidence and continuously weighted stationary mass | Sparse/low-confidence probes and tests | Heuristic coverage cutoffs remain; included |
| v2.kinematic_velocity | 4 cm position noise produces >1 m/s differentiated apparent motion | Approximately .2 s centered displacement with jump/sample checks | Known-static noise and constant-velocity tests | Short offline smoothing window may weaken abrupt motion; included |
| v2.unique_slots | Coincident slots inflate density/counts | Remove same-team positions coincident within .05 m | Exact duplicate-invariance test | Near duplicates and real close overlaps not perfectly resolved; included |
| v2.semantic_tags | All defensive transitions/occupancy implied ownership; unknown defending prefix inverted | Explicit category map; weak defensive thirds; neutral ambiguous codes; max-pool repetition | Polarity, unknown, contradiction and overlap tests; designed stress cases | Incorrect long primary phases still cause errors; included |
| v2.gap_evidence | H-before/A-after gap switches at its first frame by tie | Weak two-sided ownership bridge from sustained reliable endpoints; retain timing bracket | Hidden-turnover/false-reappearance tests and ablation | Symmetric prior, not detected invisible contact; included |
| generator CLI | Relative --config crashed after CSV write | Resolve path before hash; require separate candidate destination | Actual full-run failure fixed; two candidate runs pass | Existing V1 defaults retained; included |
| stronger contact gate | Proposed reception filter reduced rapid-control recovery | Experimental only, disabled in final V2 config | Development prototype and frozen holdout ablation | Erases valid rapid interceptions; excluded |
| quiet-only dead cap | False stationary-live stoppages | Experimental ablation only | Paired ambiguous-geometry probe | Misses indistinguishable genuine stoppages; excluded |

The original seven inference modules, original final.json and protected V1 artifacts
remain unchanged. No calibrated posterior, learned HSMM, new vision model or externally
trained model is claimed. New diagnostics are local-only for per-transition match evidence.

57 tests passed and compileall passed during the audit. The full-match candidate was
generated twice, passed the official and strict validators, matched byte-for-byte and
passed published half/pre-kickoff constraints. Frozen synthetic and independent external
results support specific mechanisms and modest measured gains, not universal accuracy.
''')
    comp=['# Final candidate comparison and recommendation','',
        '**Recommended engineering candidate for team review: V2.** It repairs reproducible '
        'evidence/sequence-invariance defects and its frozen external point estimates do not '
        'regress in the three predeclared conditions. This is not proof that it is the more '
        'accurate competition submission. Keep V1 as the unchanged submission of record until '
        'the team explicitly chooses to promote a candidate; there is no automatic promotion.',
        '', '| Item | Preserved V1 | Audit V2 |','|---|---|---|',
        f'| CSV | submission/YDSE.csv | submission/candidates/YDSE_v2.csv |',
        f'| SHA-256 | {h1} | {release["sha256"]} |',
        '| Official schema | PASS | PASS, two independent runs |',
        '| Half and pre-kickoff contract | Original published layout | Explicitly verified, including 2,934 D frames |',
        '| Protected artifacts | Original CSV/PDF/Markdown/release metadata/fallback | All six hashes unchanged |',
        f'| Predicted H/A spells | {match["v1"]["spell_count"]} | {match["v2"]["spell_count"]} |',
        f'| Predicted D segments | {match["v1"]["dead_segments"]} | {match["v2"]["dead_segments"]} |',
        f'| Candidate changes | - | {match["label_disagreements"]:,} labels differ |',
        f'| Synthetic holdout mean spellF1 | {hold["summary"]["v1"]["mean_spellF1"]:.4f} | {hold["summary"]["v2"]["mean_spellF1"]:.4f} |',
        '| Private competition spellF1 | Unknown | Unknown |',
        '', 'Prediction counts, duration percentiles, tag-dominant emissions and weak transition '
        'margins are diagnostics only, not accuracy measures or fitting targets. More dead segments '
        'can be correct extra stoppages or harmful false splits; the unavailable competition truth '
        'does not let us decide. No model was tuned to predicted match counts/durations.',
        '', 'See external_validation.md for actual other-match scores and paired uncertainty, '
        'synthetic_stress_tests.md for family failures and accuracy_audit.md for the unresolved '
        'dead-ball, wrong-tag, unseen-turnover and short-control limitations.',
        '', 'Exact safe candidate reproduction:', '```powershell',
        r'.venv\Scripts\python scripts/verify_accuracy_candidate.py','```',
        'This writes only candidate outputs and separate audit metadata. It asserts all protected '
        'V1 artifact hashes after both runs. It does not invoke the original overwrite-oriented '
        'release command. No repository or submission has been published.']
    put('reports/final_candidate_comparison.md','\n'.join(comp))
    put('reports/accuracy_audit.md',f'''# Accuracy audit - YDSE, 14 November 2026

Starting commit `{old['commit']}` had a clean working tree. The audit runs on
`accuracy-improvement`; V1 source remains on the original branch. Its CSV hash
matches `{h1}`. CSV, PDF, Markdown, release metadata/run metadata and official
smooth50 fallback were copied to a private preservation directory and hash-checked.

## Outcome

The audit found real implementation weaknesses, not an alignment or team-label reversal.
The separate V2 candidate fixes boundary leakage, weak-data confidence promotion,
duplicate observation counting, noisy player-speed bias and ambiguous tactical semantics.
It adds a deliberately weak, two-sided ownership timing prior for invisible turnovers.
The original durations/costs remain fixed; the original V1 inference modules are unchanged.

V2 passed two complete 199,319-frame executions, official/strict schema checks,
byte equality, graded-boundary checks and the published second-half D block. Its SHA-256
is `{release['sha256']}`. V1 and all protected metadata/PDF/fallback artifacts remain unchanged.

57 tests passed (including exact decoder objective, noise/coverage, duplicate, semantic,
boundary and external target-separation tests); compileall passed. There were 64 development
and 128 frozen holdout scenarios across 16 families and 11 configurations. A stronger
co-motion filter was rejected before holdout because it erased genuine rapid control.

One independent CC BY 4.0 other match was evaluated without fitting any parameters.
V2 point estimates improved slightly on clean tracking and two independent dropout
realizations; two exploratory intervals include zero. See external_validation.md for
actual numbers and limitations. Synthetic gains alone did not determine the recommendation.

## Highest-priority findings

1. V1 rolling features cross ungraded boundaries even though its DP resets. A constructed
   ungraded-only edit changed the graded slow feature by .6378. V2 scopes all operations.
2. One stationary player received full collective-stillness evidence; a .01-confidence
   repaired ball received the same stationary score as a real observation. V2 gates
   coverage and preserves reliability continuously.
3. First-difference norm magnifies coordinate noise. V2 uses a short supported displacement
   estimate for collective motion, with tests on known stationary and moving trajectories.
4. V1 broadly interprets defensive transitions and box occupation as ownership. V2 uses
   an explicit weaker/neutral semantic map and bounded pooling. Wrong primary tags remain risky.
5. A hidden turnover has an uncertainty interval, not a known frame. V1 can choose the
   first invisible frame by tie; V2's midpoint tendency is an explicit prior, not reconstruction.
6. Exact DP checks found no optimization bug for the stated energy/minimum-duration model.
   This does not validate its manually chosen costs or feature scales as football-optimal.

## Remaining failure analysis

Both versions misclassify an exact noiseless stationary live pause as dead. Identical
tracking can describe a real whistle, so this cannot be solved universally by geometry.
Moving-after-foul stoppages can also be missed. The dead terms are correlated scores,
not independent calibrated likelihoods. No learned LIVE/DEAD posterior is claimed.

Short weak controls, unseen multiple turnovers, aerial interactions and incorrect long
primary phases remain hard. A no-tags model wins the deliberately adversarial synthetic
mix, but that mix disproportionately supplies wrong/ambiguous tags; this is not evidence
to remove all tags on real football. Timing priors can place hidden turnovers wrongly.

Local match diagnostics reproduce both exact CSVs. Per-transition reliability, component
scores, costs, prior-state ages and dropout/tag indicators are kept in private JSON files.
Only aggregate statistics are public: V1/V2 have {match['v1']['spell_count']}/{match['v2']['spell_count']}
predicted possessions and {match['v1']['dead_segments']}/{match['v2']['dead_segments']} D segments.
Those numbers are not used as targets. Seven of 59 restart windows meet all strict
conditions; most rejected anchors lack the motion pattern or quiet corroboration.

## Official guidance, evidence and decision

Recheck found zero accessible open or closed issues and no accessible PR conversations.
PR listing and issue comments returned 404; commit-comment fallback returned zero;
Discussions are disabled. Official HEAD remains f8f2629. No discussion was invented.
Metric semantics, threshold matching, X propagation and the 2,934-frame D block were
verified against actual official source and independently constructed scorer examples.

Recommend V2 for engineering review because the fixes are demonstrated and frozen external
point estimates are favorable. **Do not claim higher competition accuracy or automatically
replace V1.** Broad superiority is unestablished; preserve both and explicitly review risk
before choosing the upload. No prohibited annotations, public-window tuning, manual prediction
edits, hosted restricted-data disclosure, publication or competition upload occurred.

Detailed source-by-source audit: research/accuracy_audit/implementation_audit.md.
Reproduce safely with `.venv\\Scripts\\python scripts/verify_accuracy_candidate.py`.
''')
    put('docs/technical_report_v2.md',f'''# YDSE V2 - accuracy-audit candidate technical addendum

This addendum describes a separate candidate. The original YDSE.csv, PDF, Markdown,
release metadata and baseline are preserved. V1 remains the submission of record until
the team chooses to promote V2. V2 full-match accuracy is unknown.

## Implemented changes

V2 keeps the original ATD parser, pitch/frame alignment, bounded .8-second trajectory
repair and exact duration-constrained H/A/D decoder. Costs stay 1.1 for team changes
and .7 for dead transitions; minimum dwell remains .32/.32/.64 seconds. No model is trained.

All feature windows, events and restart operations are now scoped to each graded block.
Numerically coincident same-team slots are removed at 5 cm tolerance. Collective motion
uses approximately .2-second centered displacements, rejects impossible/interrupted tracks
and requires sufficient independent position and motion coverage. Stationary-ball evidence
retains continuous endpoint reliability instead of promoting any nonzero repair confidence
to a full observation. These are evidence/invariance fixes, not calibrated probability estimates.

The tag mapper explicitly whitelists codes. Build Up, Progression and Creating Chances
are primary soft evidence; ball zones/long balls and defensive thirds are weaker. Defensive
thirds invert actor polarity. Transitions, Players in the Box, Goals, unknown codes and N/A
teams provide no settled-control vote. Repeated/correlated phases use maximum pooling.
Set-piece windows remain uncertain context, with motion-supported optional restart anchors.

For entirely invisible ball intervals with sustained reliable control at both endpoints,
a weak ownership-only bridge retains same-team evidence or varies symmetrically between
opposing teams. It never creates a long invisible trajectory. Its midpoint preference is
an explicit uncertainty prior; it can be wrong for edge-of-gap or multiple hidden turnovers.

The stronger experimental co-motion gate and quiet-only dead cap are not included. The
former erased rapid legitimate control in development. The latter cannot distinguish
identical live/dead geometry. Dead-ball weights remain heuristic and correlated.

## Verification and independent evidence

57 automated tests passed. The decoder matches exhaustive small-sequence objectives and
preserves expected timing at 20/25/50 FPS. Tests cover noise, sparse/duplicate slots, clipping,
phase semantics, sequence isolation, unknown gaps, exact schema and external target separation.
Sixteen stress families use 64 development and 128 frozen holdout cases. Holdout mean
synthetic spellF1 is {hold['summary']['v1']['mean_spellF1']:.4f} for V1 and {hold['summary']['v2']['mean_spellF1']:.4f}
for V2; this is not a real-match accuracy estimate or sufficient selection evidence.

One preselected independent CC BY 4.0 Sportec/DFL match (J03WOH, 2022/2023) was evaluated
after model freeze. Frame-level BallStatus/BallPossession are separate evaluation references,
never input features or phase priors. No training, pseudo-label fitting or parameter search
used them. Clean and two independent burst-dropout views favor V2 slightly; two exploratory
paired intervals include zero. See reports/external_validation.md for the actual table,
attribution and domain/annotation limits. These are not competition-match scores.

Both complete candidate runs pass official and strict validation, have identical bytes,
use X only outside graded blocks and produce D on all 2,934 published pre-kickoff frames.
Candidate SHA-256: `{release['sha256']}`. Exact timing, memory, source revision, input and
code/config hashes are retained locally in private/accuracy_audit/candidate_verification.json.

## Limits and reproduction

Stationary live play versus a whistle can be unidentifiable from tracking alone; both
versions fail the constructed exact-geometry live pause. Wrong long primary phases,
uncertain restart timing, aerial duels and genuine short weak controls remain failure modes.
External provider semantics/stable tracking and artificial missingness differ from ATD.
No supervised model or new video inference is claimed. No provided five-minute labels,
same-game human annotations, manual prediction edits or competitor outputs were used.

```powershell
.venv\\Scripts\\python scripts/verify_accuracy_candidate.py
.venv\\Scripts\\python -m pytest tests -q
```

Optional independent evaluation uses scripts/fetch_external_dfl.py and
scripts/validate_external_dfl.py, with CC BY 4.0 attribution to Bassek, Rein, Weber and Memmert
(2025), [dataset DOI](https://doi.org/10.6084/m9.figshare.28196177.v1). No network is required to
regenerate the competition candidate. Restricted assets and per-transition diagnostics remain local.
''')
    print('Built accuracy audit, stress/ablation, independent validation, comparison and V2 technical reports from executed results.')

if __name__=='__main__':main()
