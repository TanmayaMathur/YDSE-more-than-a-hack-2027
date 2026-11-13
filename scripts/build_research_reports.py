"""Compile reviewed public evidence into the research handoff. No match inputs."""
import csv
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'research'
UP='https://github.com/metrica-sports/more-than-a-hack-2027'
SHA='f8f2629ff1e0985f81d7e59d8413678514ee1530'

REVIEWS={
'darfattt/mtah-2027-possession':dict(local='darfattt', architecture='Nearest-player baseline with optional linear gap repair; majority vote; separate Viterbi utility',
    missing='Optional bounded interpolation; no uncertainty in inferred ball positions',tags='Soft prior helpers exist, but baseline CLI does not fuse them',
    dead='No separate dead-ball model in baseline path',temporal='Majority vote used; generic Viterbi implemented but not wired into baseline',
    confidence='No calibrated confidence',risk='Normalised-coordinate nearest distance lacks pitch-axis scaling. Smoother votes D and uses a different window convention than upstream despite equivalence claims.',
    test='12 synthetic tests executed and passed',cost='Low, NumPy',source='src/possession/baseline.py',complete='Runnable starter-level implementation; not an advanced model'),
'DivyanshAfk/mtah-2027-possession':dict(local='DivyanshAfk',architecture='Control-proximity evidence, separate dead mask, two-state minimum-cost decoding per live run',
    missing='Neutral team evidence in gaps; separate experimental gradient-boosted ball regressor is not used in v1',
    tags='Restart windows used by dead mask',dead='Fixed restart padding plus player stillness and ball-outside rules',
    temporal='Two-state Viterbi with constant switch penalty',confidence='Near/far distance weights; fast-ball evidence suppressed',
    risk='Fixed restart spans can mask live play; long no-evidence live runs can inherit weak endpoints. Ballfill claim is author-reported, not independently reproduced.',
    test='No tests directory discovered in reviewed source; not executed',cost='Low for v1; higher for optional sklearn ballfill',source='src/v1.py',complete='Complete v1 source present; full-match execution not independently run'),
'ArmicZeroGTRS/more-than-a-hack-2027':dict(local='Armic',architecture='Proximity/contact/density scores, collective stillness and three-state decoding',
    missing='Neutral ownership; dead evidence needs static teams',tags='Weak set-piece mask',dead='Ball static/outside plus team motion',
    temporal='Three-state Viterbi followed by short-run merging and dead bridging',confidence='Physical scores and temperature; calibration unknown',
    risk='Post-hoc minimum spell repair can remove real short possessions. A synthetic end-to-end test fails on Windows when temp and repository are on different drives (os.path.relpath).',
    test='15/16 self-checks passed after supplying omitted organiser helpers; one cross-drive failure',cost='Low, NumPy',source='src/model.py',complete='Complete source path present; Windows portability limitation observed'),
'aditwidi/more-than-a-hack-2027-team-nexus':dict(local='nexus',architecture='Top-three team control margin, multi-scale evidence and formation fallback',
    missing='Interpolated ball and formation fallback',tags='Defensive polarity implemented',dead='Ball absence, motion, stationary ball and restart features',
    temporal='Asymmetric three-state Viterbi plus iterative minimum-duration cleanup',confidence='Emission weights; real calibration unknown',
    risk='emissions.py comments explicitly describe changes chosen from public-window outcomes. Those scores/choices are excluded from our model selection; this is a provenance concern, not an organiser ruling.',
    test='Tests present; not executed',cost='Low, NumPy',source='pipeline/emissions.py',complete='Complete feature/emission/decoder source present'),
'hnfadtya/more-than-a-hack-2027':dict(local='hnfadtya',architecture='Permutation-invariant set Transformer, dilated temporal convolutions and bidirectional GRU',
    missing='Burst dropout, crowd/air-aware corruption and masks for external training',tags='No tag fusion verified in inspected inference path',
    dead='Learned H/A/D output head',temporal='Minimum-duration sequence decoding after windowed neural probabilities',
    confidence='Neural probabilities; independent calibration unknown',risk='External training and compatible weights/GPU dependencies must be reproduced; domain transfer to automatic tracking remains uncertain.',
    test='Decoder tests present; not executed (PyTorch not installed)',cost='Higher, PyTorch',source='mtah/model.py',complete='Training and inference code present; trained performance not reproduced'),
'yassintamer91/more-than-a-hack-2027':dict(local='yassintamer91',architecture='Control-aware structured evidence, motion-localized restarts, optional externally trained stoppage logistic model',
    missing='Gap confidence and explicit unsupported-evidence handling',tags='Phase/restart votes clipped; no midpoint anchor when localization fails',
    dead='Collective motion plus stationary/outside ball; optional learned stop head',temporal='Structured dynamic temporal inference; specialist modules',
    confidence='Reliability and availability gates; calibration not independently measured',risk='Optional video and external-model routes require separate reproduction; real-match superiority unverified.',
    test='Many synthetic tests present; not executed',cost='Low core; optional video higher',source='solution/structured.py',complete='Substantial source and tests present; inspected core not independently run'),
'4139benuzter/mtah2027-mas-bueno':dict(local='mas-bueno',architecture='Touch/control episodes, restart kick boosts and three-state scores',
    missing='Formation logit and optional broadcast ball fill',tags='Set-piece restart candidate windows and phase evidence',
    dead='Stillness, outside pitch, restart cues and onset snapping',temporal='Viterbi plus short-dead merging and onset snapping',
    confidence='Rule-based probability/score gates',risk='Broadcast alignment uses match-specific offset hints rather than a fresh global search. Snapping and short-dead rules can erase brief real events.',
    test='No tests directory in reviewed tree; not executed',cost='Low core; optional matching higher',source='possession/model.py',complete='Complete core and optional broadcast source present')}

def git(local,*args):
    p=subprocess.run(['git','-C',str(ROOT/'vendor_research'/local),*args],capture_output=True,text=True,encoding='utf-8')
    return p.stdout.strip()

def write(name,text):
    (R/name).write_text(text.strip()+'\n',encoding='utf-8')

def main():
    scan=json.loads((R/'github_updates/raw/latest.json').read_text(encoding='utf-8'))
    # Old scanner snapshots included compare patches. Retain only metadata to avoid
    # unnecessarily caching public competitors' prediction/data additions.
    for path in (R/'github_updates/raw').glob('*.json'):
        payload=json.loads(path.read_text(encoding='utf-8'))
        for comp in payload.get('fork_comparisons',{}).values():
            for file in comp.get('files',[]):
                file.pop('patch',None)
        path.write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
    comps=scan.get('fork_comparisons',{})
    counts=Counter(c.get('status','unavailable') or 'unavailable' for c in comps.values())
    candidates=scan['competitors'].copy()
    for f in scan['forks']:
        candidates.setdefault(f['full_name'],f)
    code_items=[]
    for path in [R/'github_updates/code_search_metadata.json', R/'github_updates/code_search_pages.json']:
        if path.exists():
            payload=json.loads(path.read_text())
            for page in payload if isinstance(payload,list) else [payload]:
                code_items.extend(page.get('items',[]))
    for item in code_items:
        candidates.setdefault(item['repository'],{'full_name':item['repository'],'html_url':'https://github.com/'+item['repository']})
    fields=['repository','url','relevance','classification','updated_at','pushed_at','ahead_by','licence',
            'source_review','commit_sha','architecture','tracking_features','temporal','missing_ball','dead_ball',
            'confidence','smart_tagging','code_completeness','testing','computational_cost','independent_performance','risks']
    records=[]
    for name,repo in sorted(candidates.items()):
        if name=='metrica-sports/more-than-a-hack-2027':
            continue
        review=REVIEWS.get(name); comp=comps.get(name)
        text=(name+' '+(repo.get('description') or '')).lower()
        relevant=bool(re.search(r'mtah|more.?than.?a.?hack.*2027|spellf1|bar-ath',text))
        classification='Discovery lead; implementation unverified'
        if comp:
            if comp.get('status') in ('identical','behind'):
                classification='Unmodified starter / older upstream'
            elif comp.get('ahead_by'):
                classification=('Active independent code (filename evidence)' if any(f['filename'].endswith('.py') for f in comp['files'])
                                else 'Minor/non-Python modification')
            else:
                classification='Unavailable or unverifiable comparison'
        if review:
            classification='Source-inspected competing implementation'
        row=dict.fromkeys(fields,'Unknown')
        row.update(repository=name,url=repo.get('html_url','https://github.com/'+name),
                   relevance='Relevant challenge candidate' if relevant or review or comp else 'Broad search lead; relevance unverified',
                   classification=classification,updated_at=repo.get('updated_at','Unknown'),pushed_at=repo.get('pushed_at','Unknown'),
                   ahead_by=comp.get('ahead_by','Unknown') if comp else 'Unknown',
                   licence=(repo.get('license') or {}).get('spdx_id','Unknown'),source_review='Yes' if review else 'Metadata/changed-file list only',
                   independent_performance='Unknown; no authorised comparable full-match score')
        if review:
            local=review['local']; sha=git(local,'rev-parse','HEAD')
            row.update(commit_sha=sha,architecture=review['architecture'],tracking_features='See source review',
                       temporal=review['temporal'],missing_ball=review['missing'],dead_ball=review['dead'],confidence=review['confidence'],
                       smart_tagging=review['tags'],code_completeness=review['complete'],testing=review['test'],
                       computational_cost=review['cost'],risks=review['risk'])
        records.append(row)
    with (R/'competitor_inventory.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fields);writer.writeheader();writer.writerows(records)
    relevant_count=sum(r['relevance']=='Relevant challenge candidate' for r in records)
    summary={'official_commits':len(scan['commits']),'official_issues_reviewed':0,'official_prs_reviewed':0,
             'accessible_forks':len(scan['forks']),'fork_status':dict(counts),
             'forks_ahead':sum(bool(c.get('ahead_by')) for c in comps.values()),
             'forks_with_changed_python':sum(bool(c.get('ahead_by')) and any(f['filename'].endswith('.py') for f in c.get('files',[])) for c in comps.values()),
             'candidate_repositories':relevant_count,'source_inspected_repositories':len(REVIEWS),
             'all_inventory_rows':len(records),'code_search_records':len(code_items)}
    (R/'research_counts.json').write_text(json.dumps(summary,indent=2))
    write('official_repository_analysis.md',f'''# Official repository analysis

Evidence snapshot: {scan['timestamp_utc']}. Official revision [{SHA}]({UP}/commit/{SHA}).

VERIFIED: challenge and data contracts were reviewed in CHALLENGE.md, DATA.md, EVALUATION.md,
SUBMISSION.md, RULES.md, FAQ.md, OVERVIEW.md and README.md. Starter loaders, games.py,
all three notebooks (source cells, not execution outputs), baseline, validator and actual
scorer implementation were inspected. Upstream code is separately MIT licensed.

## Engineering implications

- VERIFIED: ATD uses frame_id minus one; Smart Tagging uses round(seconds * 25); homography is already zero-based. The private IdFrame offsets in games.py must not be applied to ATD. [DATA]({UP}/blob/{SHA}/DATA.md).
- VERIFIED: temporal scoring forward-fills X and back-fills the leading gap independently inside each valid run; all-X remains X. Same-team overlapping spells are sorted by decreasing IoU then stable indices and greedily matched one-to-one at thresholds .3/.4/.5/.6/.7. D spans split possessions but are not possessions. We implement per-half decoding and use X only outside grading. [Actual scorer]({UP}/blob/{SHA}/evaluation/possession_metrics.py).
- VERIFIED: validator source checks row count, integer ordered IDs and valid nonblank labels, but does not reject extra columns. YDSE adds an exact-column check. [Validator library]({UP}/blob/{SHA}/evaluation/possession_metrics.py).
- VERIFIED: second half grading includes 2,934 pre-kickoff D frames. FAQ and loader use kickoff 113742; games.py's playback anchor arithmetic yields 113741. We use KICKOFF_VIDEO_FRAMES from the official tagging loader, consistent with FAQ, and half_video_blocks for graded limits. [FAQ]({UP}/blob/{SHA}/FAQ.md), [loader]({UP}/blob/{SHA}/starter/load_smart_tagging.py).
- VERIFIED: restart tags are uncertain spans, not exact boundaries; defensive tags name the defending team. We invert defensive evidence, cap correlated tags and localize restarts only if motion supports it. [Notebook]({UP}/blob/{SHA}/starter/01_smart_tagging.ipynb), [phase definitions]({UP}/blob/{SHA}/OVERVIEW.md).
- VERIFIED: no hand labels, corrections or human-produced event data about this game, and no public-window tuning. This ruled out supervised learning from the provided window. [RULES]({UP}/blob/{SHA}/RULES.md).

The official scorer demo ran successfully once on shipped baselines. The locally regenerated
smooth50 fallback passed the official validator. Published full-match spellF1 .2433 is an
organiser result for their baseline, not a new YDSE score. No candidate was ranked on public labels.

## Public surfaces and limits

One branch (main), zero tags and six reachable commits. Issues disabled in metadata;
Discussions disabled. Issue listing/search returned no records, PR listing returned 404 in
both CLI and connector, and PR search returned none. PR/issue-comment absence is therefore
not proof no inaccessible history exists. Releases and commit comments returned no records.
Wiki page fetch failed; no wiki content was verified. Workflow listing was queried through REST;
see raw local API snapshot for the response. No CI-derived correctness claim is made.

Submission requires CSV, public reproducible code and a short PDF/Markdown report. The form is
emailed to registered teams, one editable response per team. The published date is 17 November
2026; exact cutoff time/timezone remains UNVERIFIED. Team size is 3–5 for stated eligibility.
[Submission]({UP}/blob/{SHA}/SUBMISSION.md), [rules]({UP}/blob/{SHA}/RULES.md).
''')
    write('official_pr_analysis.md',f'''# Official PR analysis

VERIFIED access results: GET [{UP}/pulls]({UP}/pulls) via REST list endpoint returned HTTP 404,
including through the connected GitHub tool. Global repository-scoped PR search returned zero
accessible results. Zero PRs could be reviewed. Do not read this as a verified count of all PRs.

Consequently authors, submission dates, status, changed-file lists, review discussions, inline
comments, fixes and resolutions are UNVERIFIED for inaccessible PRs. The global review-comment
endpoint returned zero records. No speculative PR correction was incorporated into YDSE.

The reusable scanner fetches files, reviews, inline comments, commits and discussion comments
for every PR returned by the public list endpoint on future successful scans.
''')
    write('official_issues_and_comments.md',f'''# Official issues and comments

VERIFIED: repository metadata reports has_issues=false and has_discussions=false. All-state
issue listing returned an empty list, and connected search returned no issues. Zero issue bodies
or comment threads were available to review. The global issue-comment endpoint returned 404.
Metadata also reported open_issues_count=1, so a reliable total cannot be inferred from these
conflicting surfaces. [Repository API](https://api.github.com/repos/metrica-sports/more-than-a-hack-2027).

The general commit-comment and inline PR-comment endpoints returned zero records. No participant
speculation was treated as maintainer guidance. Verified guidance comes from the official documents
and commits listed in organiser_clarifications.md and official_commit_history.md.
''')
    history=['# Complete accessible official commit history','',f'One branch, six commits; current HEAD {SHA}.','']
    for c in reversed(scan['commits']):
        detail=scan['commit_details'].get(c['sha'],{})
        files=', '.join(f['filename'] for f in detail.get('files',[]) if not f['filename'].endswith('.csv'))
        history += [f'## {c["sha"]}',f'- VERIFIED: {c["commit"]["author"]["date"]}; {c["commit"]["message"]}',
                    f'- Source: {c["html_url"]}',f'- Files (CSV contents excluded from this report): {files}','']
    history+=['VERIFIED: git history shows no post-initial change to games.py, the scorer, validator, baseline or alignment loaders.',
              'b429693 clarifies definitions/deliverables; f00bc32 revises possession wording; 3de6b60 adjusts citation.',
              'c073f29 and f8f2629 supersede permissive old annotation wording. OUTDATED older text allowing limited hand labels must not guide implementation.',
              'The final clarification prohibits any hand labels on the competition game for training/validation and restricts human-produced same-game data.']
    write('official_commit_history.md','\n'.join(history))
    fork_lines=['# Public fork analysis','',f'VERIFIED: paginated REST listing yielded {len(scan["forks"])} accessible forks. '
                f'Metadata fork_count may differ; only returned forks were inspected. Compare status counts: {dict(counts)}.',
                f'{summary["forks_ahead"]} have additional commits; {summary["forks_with_changed_python"]} change Python filenames. '
                'Changed-file metadata is screening evidence, not proof of model quality. Seven repositories received deeper source review (five of these forks and two standalone leads).',
                'Comparisons that fail remain unavailable/unverifiable; identical forks were not repeatedly cloned.','',
                '| Fork | Classification | Ahead | Changed files | Source |','|---|---|---:|---:|---|']
    for f in scan['forks']:
        c=comps.get(f['full_name'],{})
        fork_lines.append(f'| {f["full_name"]} | {c.get("status") or "Unavailable/unverifiable"} | {c.get("ahead_by","Unknown")} | {len(c.get("files",[]))} | [compare]({c.get("html_url") or f["html_url"]}) |')
    write('official_fork_analysis.md','\n'.join(fork_lines))
    write('organiser_clarifications.md',f'''# Organiser clarifications

All entries below are VERIFIED from official sources, not competitor interpretations.

| Clarification | Applied decision | Source |
|---|---|---|
| No hand annotations/corrections on this game, for any purpose | No labels or manual edits in inference | [f8f2629]({UP}/commit/{SHA}) |
| Public five minutes are for pipeline sanity only | No YDSE tuning, ranking or version selection on that window | [RULES]({UP}/blob/{SHA}/RULES.md) |
| Hosted LLMs must not receive restricted assets/extracts | Local-only file processing, no raw tool output | [FAQ]({UP}/blob/{SHA}/FAQ.md) |
| Missing ball is common; phases are automatic | Confidence gates, no missing=dead rule, soft tag fusion | [DATA]({UP}/blob/{SHA}/DATA.md) |
| Dead ball has no team owner | Explicit D state rather than tagging dead ownership | [CHALLENGE]({UP}/blob/{SHA}/CHALLENGE.md) |
| Same source timeline; broadcast differs | Tactical-only inference; no guessed broadcast offset | [DATA]({UP}/blob/{SHA}/DATA.md) |

UNVERIFIED: signed participation terms have not been found locally. User has confirmed Drive
access, explicitly not permission to disclose. No terms documents were found by workspace filename
search; archive member inventories contained only expected assets and a README. Terms review remains
open. No restricted asset is uploaded to any third-party service or included in public-ready source.
''')
    reviews=['# Source-level competitor analysis','',f'{relevant_count} relevant candidates in the inventory; '
             'seven implementations deeply inspected. Others are metadata leads, not assessed solutions. '
             'No stars/fork counts or public-window scores are used to rank quality.','']
    for name,r in REVIEWS.items():
        sha=git(r['local'],'rev-parse','HEAD'); count=git(r['local'],'rev-list','--count','HEAD')
        reviews += [f'## {name}',f'VERIFIED source snapshot: [{sha}](https://github.com/{name}/tree/{sha}); '
                    f'{count} total reachable commits (includes upstream where applicable).',
                    f'- Implemented: {r["architecture"]}.',f'- Missing ball: {r["missing"]}.',f'- Smart Tagging: {r["tags"]}.',
                    f'- Dead ball: {r["dead"]}.',f'- Temporal model: {r["temporal"]}.',f'- Confidence: {r["confidence"]}.',
                    f'- Completeness: {r["complete"]}. Cost: {r["cost"]}.',f'- Actual verification: {r["test"]}.',
                    f'- PLAUSIBLE limitations: {r["risk"]}',
                    f'- [Inspected algorithm](https://github.com/{name}/blob/{sha}/{r["source"]}). '
                    'Licence metadata is in competitor_inventory.csv; NOASSERTION/Unknown is not reuse permission. '
                    'No source/weights/predictions were reused. Comparable full-match performance: Unknown.','']
    reviews += ['## Opus Operandi','VERIFIED public organisation profile describes a possession engine, external benchmark '
                'and visible/missing-ball specialists. The two advertised implementation repositories return 404 and are '
                'not in public organisation enumeration. Architecture is therefore an UNVERIFIED implementation claim; '
                'code, weights, tests, licence and performance are Unknown. '
                '[Profile](https://github.com/Opus-Operandi-FC-Barcelona/.github/blob/main/profile/README.md).',
                '', '## Search coverage',f'Twenty repository queries produced {len(scan["competitors"])} deduplicated search/lead records before fork union. '
                'Queries cover alternate titles, MTAH, spellF1, BAR-ATH, possession filenames and generic tracking. '
                f'Code search spellF1 language:Python was paginated, yielding {len(code_items)} metadata records. '
                'Search is index-dependent and mutable; some broad queries were limited to the first 100 results. '
                'No claim of finding every participant is made. Private/unindexed implementations remain inaccessible.']
    write('competitor_comparison.md','\n'.join(reviews))
    matrix=['# Final competitive matrix','', 'Implementation comparison only; transition accuracy and independent real-match performance are Unknown for every row.',
            'No comparable private full-match evaluation was available.','',
            '| Implementation | Missing ball | Tracking/control features | Tactical tags | Dead ball | Temporal model |',
            '|---|---|---|---|---|---|',
            '| YDSE | Short bounded repair with decaying reliability; no long-gap positions | Metres, relative motion, approach/density, jump rejection | Defensive inversion and saturated votes | Motion/outside/quiet plus localized restarts | Exact minimum-duration three-state DP; no longer-neighbour deletion |']
    for name,r in REVIEWS.items():
        matrix.append(f'| [{name}](https://github.com/{name}) | {r["missing"]} | {r["architecture"]} | {r["tags"]} | {r["dead"]} | {r["temporal"]} |')
    matrix += ['', '| Implementation | Reproducibility evidence | Cost | Code completeness | Testing | Independent performance |',
               '|---|---|---|---|---|---|',
               '| YDSE | Two full runs and official validation recorded in reports | CPU, seconds | All submitted path implemented | Executed synthetic/contract tests | Synthetic only; competition Unknown |']
    for name,r in REVIEWS.items():
        matrix.append(f'| {name} | {r["test"]} | {r["cost"]} | {r["complete"]} | {r["test"]} | Unknown |')
    matrix += ['', 'Sources and caveats are in competitor_comparison.md. Source inspection did not establish that '
               'our system outperforms these implementations. Restart localization and exact integrated duration '
               'constraints were adopted as defensible engineering improvements, not copied source.']
    write('final_competitive_matrix.md','\n'.join(matrix))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
