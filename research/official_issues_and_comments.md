# Official issues and comments

VERIFIED: repository metadata reports has_issues=false and has_discussions=false. All-state
issue listing returned an empty list, and connected search returned no issues. Zero issue bodies
or comment threads were available to review. The global issue-comment endpoint returned 404.
Metadata also reported open_issues_count=1, so a reliable total cannot be inferred from these
conflicting surfaces. [Repository API](https://api.github.com/repos/metrica-sports/more-than-a-hack-2027).

The general commit-comment and inline PR-comment endpoints returned zero records. No participant
speculation was treated as maintainer guidance. Verified guidance comes from the official documents
and commits listed in organiser_clarifications.md and official_commit_history.md.
