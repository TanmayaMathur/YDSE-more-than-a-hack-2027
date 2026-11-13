# Current official guidance, checked 14 November 2026

Official HEAD remains `f8f2629ff1e0985f81d7e59d8413678514ee1530` (six
reachable commits). The seven current documents in `official_recheck.json`
were fetched through the GitHub connector and read, including the scorer.

[RULES.md](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/RULES.md)
permits other-match labelled training, unsupervised/self-supervised methods
and algorithmic pseudo-labels without human correction on the provided match.
It bans human-produced same-game annotations for training/validation, manual
prediction corrections and private evaluation labels. The public five-minute
window is for pipeline correctness, not training or model selection. Improving
automatic tracking through code is permitted. Every dependency must be
inspectable and the method explained. V3 uses only public other-match labels;
no competition unsupervised adaptation was needed or attempted.

[FAQ.md](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/FAQ.md)
explicitly prohibits disclosing restricted materials or extracts to hosted
LLMs. [DATA.md](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/DATA.md)
and RULES defer to accepted enrolment terms. A local workspace filename search,
including ignored files, found no signed agreement. This does not establish
that no terms were accepted elsewhere. The Drive invitation establishes access,
not permission to share. Signed-term verification remains with the participant;
all restricted processing in this investigation runs locally, with only hashes,
validation status and aggregate diagnostics returned. Raw assets, frame-level
predictions, private logs and reconstruction-capable exports remain gitignored.

[CHALLENGE.md](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/CHALLENGE.md),
[EVALUATION.md](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/EVALUATION.md),
[SUBMISSION.md](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/SUBMISSION.md)
and the [current scorer](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/evaluation/possession_metrics.py)
confirm spellF1 as the ranking metric, macroF1 as tie breaker, exact frame
indexing, X propagation separately within valid halves and the published
second-half pre-kickoff D interval. H/A controlled spells exclude D, so both
missed and invented stoppages can damage possession matching.

## Accessible conversations and failures

The all-state issue listing succeeded with zero entries. Repository metadata
disables issues, PRs and discussions, despite a nonzero summary open-issue
counter; the summary counter is not an accessible conversation. PR search
succeeded with zero results. The PR listing and issue-comment endpoints returned
404; these are inaccessible endpoints, not independently established zero
comments. The global PR-review-comment endpoint returned an empty list.
No accessible PR exists on which to enumerate review submissions. Commit
comments were unsupported by the connector; the first sandbox CLI attempt had
a network error, then the authorized public `gh api` retry succeeded with `[]`.
No new maintainer clarification was found. No comments, issues or questions were
posted. Details and document modification dates are in `official_recheck.json`.

Deadline supplied by the participant is 17 November 2026. Exact cutoff time
and delivery instructions still require the organiser's message. Nothing was
published, submitted or promoted.
