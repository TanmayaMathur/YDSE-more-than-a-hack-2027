# Architecture

```mermaid
flowchart TD
    ATD[Local tactical ATD] --> P[Strict parser and team mapping]
    P --> B[Bounded ball repair and reliability]
    P --> M[Collective player motion]
    B --> G[Control geometry and ball motion]
    TAG[Local automatic tactical XML] --> T[Defensive inversion and saturated priors]
    B --> R[Optional motion-supported restart localization]
    TAG --> R
    M --> D[Dead-ball evidence]
    G --> E[Three-state evidence]
    T --> E
    R --> E
    D --> E
    E --> DP[Per-half duration-constrained Viterbi]
    DP --> CSV[Complete deterministic CSV]
    CSV --> V[Official validator and exact-column check]
```

No ground-truth file is an input. No raw match data leaves local processing.
`data.py` parses; `preprocessing.py` repairs; `features.py`, `tagging.py` and
`restarts.py` build evidence; `temporal.py` solves the state sequence; `pipeline.py`
assembles them. The generation script writes LF UTF-8 CSV and hashes every used
input, code/config snapshot and output. No cache is reused for release verification.
