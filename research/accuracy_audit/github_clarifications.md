# Official accuracy-guidance recheck - 14 November 2026

Official HEAD remains `f8f2629ff1e0985f81d7e59d8413678514ee1530` (23 October 2026).
The six accessible commits match the earlier review. The current metric, challenge,
evaluation, rules, FAQ, data and games.py were fetched again from official main.
The source priority in this audit is metric implementation first, then official documents.

| Surface | Actual access result | Interpretation |
|---|---|---|
| Open issues | Successful response, zero records | Zero accessible open issues |
| Closed issues | Successful response, zero records | Zero accessible closed issues |
| Issue search | Successful response, zero records | No additional accessible threads |
| All-state PR listing | HTTP 404 | Inaccessible endpoint, not a verified zero total |
| PR search | Successful response, zero records | Zero accessible PRs to review |
| Global issue comments | HTTP 404 | Inaccessible endpoint |
| Inline PR comments | Successful response, zero records | No accessible inline comments |
| General commit comments | Connected fetch rejected URL locally; gh REST fallback returned zero | Zero accessible commit comments via successful fallback |
| Discussions | Repository metadata has_discussions=false | Disabled |
| Repository issues | has_issues=false but open_issues_count=1 | Conflicting metadata; do not infer hidden issue content |

No authentication failure or rate-limit response occurred in these checks. HTTP 404
does not establish that no private/inaccessible history exists. There was no PR to
traverse for review threads or commits. Public endpoint evidence is in official_recheck.json.

| Official answer/clarification (paraphrased) | Date/source | Code effect and compliance |
|---|---|---|
| Control, rather than an incidental opponent touch, establishes new ownership; last control persists through loose/contested play | [CHALLENGE, current revision](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/CHALLENGE.md), 23 Oct revision | V1/V2 use temporal evidence; short-control and false-touch stress tests added. Imperfect control inference remains disclosed. |
| No same-game hand labels/corrections for any purpose; five public minutes cannot train/tune/select | [RULES](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/RULES.md), clarified 23 Oct | No public-window candidate scores, no hand corrections. Synthetic labels and a different independently licensed match are isolated evaluation sources. |
| Restricted materials cannot go to hosted LLMs | [FAQ](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/FAQ.md), current 23 Oct revision | Match parsing/diagnostics run locally; per-transition evidence remains private. Only aggregates reach model context. |
| Second half is graded before kickoff; 110808-113741 are D | [FAQ](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/FAQ.md), current revision | Candidate verification checks all 2,934 frames using official constants. |
| Automatic phase intervals are uncertain; team indicates the actor of the phase | [DATA](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/DATA.md), [OVERVIEW](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/OVERVIEW.md) | V2 explicitly maps categories, treats transitions/occupancy as neutral and weakens defensive evidence; no copied phase labels. |
| ATD is one-based; tagging timestamps use round(seconds*25) | [DATA](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/DATA.md), [games.py](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/games.py) | Strict parser/alignment unchanged. No private IdFrame offset applied to ATD. |

These are official document/commit clarifications, not invented maintainer conversation
answers. Zero accessible issue and PR conversations were found to quote. Signed participation
terms remain unavailable locally; the Drive invitation is not disclosure permission.
