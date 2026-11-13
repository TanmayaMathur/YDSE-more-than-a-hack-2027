# Third-party notices for V3

The small externally supervised dead/live head and its regularized Newton/IRLS
fitting structure were informed by, and adapt the public design in
[yassintamer91/solution/stoppage.py](https://github.com/yassintamer91/more-than-a-hack-2027/blob/906ec8da2e52b1e0c1ade42cd4eca297c0674a2f/solution/stoppage.py).
This credit applies to `src/possession/learned_dead.py`; the fitting structure
and numerical safeguards share that implementation's pattern. The repository's
[licence at that revision](https://github.com/yassintamer91/more-than-a-hack-2027/blob/906ec8da2e52b1e0c1ade42cd4eca297c0674a2f/LICENSE)
covers its source under MIT. No competitor weights, prediction files or
competition-match annotations were used. YDSE supplies different features,
its own externally fitted weights, a conservative evidence blend and its
existing duration decoder. Prior V1/V2 reports describe their historical scope;
this V3 notice supersedes any broad claim that no competitor design was adapted.

MIT License

Copyright (c) 2026-2027 Metrica Sports

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The licence above excludes the separately restricted competition data.

## External data and trained parameters

Manuel Bassek, Robert Rein, Hendrik Weber and Daniel Memmert (2025),
[An integrated dataset of spatiotemporal and event data in elite soccer](https://doi.org/10.6084/m9.figshare.28196177.v1),
Sportec/DFL, licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
`models/ydse_live_dead.json` is fitted from J03WOH BallStatus with automatically
calculated physical features and label-independent corruptions. It is a
transformed/learned artifact, not original raw tracking; attribution and
training provenance accompany it. No modifications to source annotations.
J03WQQ and J03WN1 are evaluation only.

The official challenge helpers retain their notices in `upstream/PROVENANCE.md`.
PathCRF and hnfadtya source were reviewed for ideas and are credited in
`research/final_accuracy/competitor_recheck.md`; none of their code or weights
is included in V3.
