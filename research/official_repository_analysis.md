# Official repository analysis

Evidence snapshot: 2026-11-13T19:30:17.371733+00:00. Official revision [f8f2629ff1e0985f81d7e59d8413678514ee1530](https://github.com/metrica-sports/more-than-a-hack-2027/commit/f8f2629ff1e0985f81d7e59d8413678514ee1530).

VERIFIED: challenge and data contracts were reviewed in CHALLENGE.md, DATA.md, EVALUATION.md,
SUBMISSION.md, RULES.md, FAQ.md, OVERVIEW.md and README.md. Starter loaders, games.py,
all three notebooks (source cells, not execution outputs), baseline, validator and actual
scorer implementation were inspected. Upstream code is separately MIT licensed.

## Engineering implications

- VERIFIED: ATD uses frame_id minus one; Smart Tagging uses round(seconds * 25); homography is already zero-based. The private IdFrame offsets in games.py must not be applied to ATD. [DATA](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/DATA.md).
- VERIFIED: temporal scoring forward-fills X and back-fills the leading gap independently inside each valid run; all-X remains X. Same-team overlapping spells are sorted by decreasing IoU then stable indices and greedily matched one-to-one at thresholds .3/.4/.5/.6/.7. D spans split possessions but are not possessions. We implement per-half decoding and use X only outside grading. [Actual scorer](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/evaluation/possession_metrics.py).
- VERIFIED: validator source checks row count, integer ordered IDs and valid nonblank labels, but does not reject extra columns. YDSE adds an exact-column check. [Validator library](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/evaluation/possession_metrics.py).
- VERIFIED: second half grading includes 2,934 pre-kickoff D frames. FAQ and loader use kickoff 113742; games.py's playback anchor arithmetic yields 113741. We use KICKOFF_VIDEO_FRAMES from the official tagging loader, consistent with FAQ, and half_video_blocks for graded limits. [FAQ](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/FAQ.md), [loader](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/starter/load_smart_tagging.py).
- VERIFIED: restart tags are uncertain spans, not exact boundaries; defensive tags name the defending team. We invert defensive evidence, cap correlated tags and localize restarts only if motion supports it. [Notebook](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/starter/01_smart_tagging.ipynb), [phase definitions](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/OVERVIEW.md).
- VERIFIED: no hand labels, corrections or human-produced event data about this game, and no public-window tuning. This ruled out supervised learning from the provided window. [RULES](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/RULES.md).

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
[Submission](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/SUBMISSION.md), [rules](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629ff1e0985f81d7e59d8413678514ee1530/RULES.md).
