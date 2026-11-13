# Source-level audit of Version 1 and candidate changes

Version 1 source is preserved at commit `8b184b0c626e108679b97a344ef06a661f860d5b`
and on the original branch. Its seven inference modules are unchanged. V2 is an
additive path in src/possession/v2.py; default generation still selects V1.

| Source, significant assumption | Finding/evidence | Action and residual risk |
|---|---|---|
| data.py:13-35, strict contiguous ATD parser | Correct frame_id minus one, shape checks and NaN handling; original roundtrip tests pass | Retained. Partial coordinate availability becomes unavailable geometry. Export speed fields are deliberately unused. |
| data.py:37-45, metadata team order | Follows official home/away convention and validates memberships | Retained; no player-identity meaning assigned to slots. |
| preprocessing.py:14-40, spike/gap repair | Bounded to each block, no long extrapolation; confidence is constant per gap and decays with total span, not age within gap | Retained. Physical 45 m/s limit is heuristic; persistent false tracks can survive. |
| preprocessing.py:42, first-difference velocity | Norm after differentiation has a positive noise bias: stationary 4 cm coordinate noise looks like >1 m/s | V2 uses approximately .2 s centered displacement for collective player speed, requires valid intermediate samples and rejects jumps. This adds a short offline context window. |
| features.py:20, 61, 64 global rolling windows | DEMONSTRATED leakage from ungraded observations: identical graded data changes slow score by .6378 | V2 extracts independently inside each graded block, including all motion, tags and restart operations. Boundary invariance test passes. |
| features.py:16-20, 62, low median speed | DEMONSTRATED one stationary visible player gets maximal collective slow score | V2 requires sufficient independent position/motion coverage; unknown motion contributes no stillness evidence. |
| features.py:61, reliability > 0 | DEMONSTRATED reliability .01 and 1.0 both produce stationary score 1 | V2 weights stationary evidence by endpoint reliability and known-speed coverage. Unit counterexample passes. |
| features.py:40/54/56, counts and density | Duplicate same-team slots increase coverage/density and can bias median motion | V2 removes numerically coincident same-team positions within 5 cm. Exact duplicate-invariance test passes; near duplicates/overlapping real players remain imperfect. |
| features.py:45-54, proximity/control and flight | Correct pitch-axis scaling; only both-team observed distances produce a signed margin. Missing velocities still receive a permissive fallback | Geometry retained. A stronger experimental co-motion gate erased rapid true controls; excluded from candidate. Control versus touch remains imperfect. |
| tagging.py:28-34, broad defensive inversion | Defensive transitions and unfamiliar defending names are treated as settled opponent control; box occupation implies ownership | V2 explicit semantic whitelist: transitions, occupancy, unknown and goal categories are neutral. Defensive thirds give weaker inverse evidence. Weights remain assumptions, not calibrated probabilities. |
| tagging.py:37-40, correlated tags | Repetition is capped, but a long incorrect primary phase can still dominate when ball evidence is absent | V2 maximum pooling retains bounded evidence. Adversarial wrong BUILD UP case still fails; no claim of immunity. |
| restarts.py:6-26, strict motion anchors | Candidate audit: 59 tags, 58 with sufficient coverage, 13 with stationary-to-launch pattern, 7 also quiet enough | Retained thresholds. No anchor fabricated for the remaining windows. Quiet/ball-speed thresholds remain heuristic. |
| restarts.py:31-36, cue padding | V1 operates globally; cue tails may cross a graded boundary | V2 calls the same localizer only on clipped block-local events. |
| pipeline.py:22-26, additive dead energy | Stationary, slow, missing and quiet terms are correlated, not independent probability evidence. Exact stationary live pause is incorrectly D in both versions | Confidence/coverage bugs repaired; core dead weights retained. Conservative cap tested as an ablation, not selected from synthetic score. Referee permission can be unidentifiable from identical tracking. |
| temporal.py:4-43, duration DP | Exhaustive small-sequence checks agree with objective, including duration-one and mixed-duration states | Retained. FPS division gives approximately consistent real-time costs. rint duration quantization permits half-frame rounding; final state may truncate. |
| temporal.py:30-37, mature-state ties | DEMONSTRATED H-before/A-after invisible gap switches at the first gap frame; tie handling does not imply causal persistence | V2 adds a weak symmetric ownership bridge only with sustained endpoint control. Transition timing remains an uncertain bracket, not an inferred invisible contact. |
| pipeline.py:31-36, official pre-kickoff | Correct published block; equality guard is tied to official block list | V2 uses block membership and verifies explicit D contract; candidate verifier checks all 2,934 D frames. |
| generate_submission.py, relative --config | Full candidate generation exposed ValueError hashing a relative config path after CSV write | Resolved config path before hashing; external configs hash by stable filename. Candidate guard prevents V2 overwriting YDSE.csv. |
| verify_release.py, default output paths | Correct original reproduction but overwrites original CSV/metadata by design | Not used for experimentation. Separate verify_accuracy_candidate.py preserves all six V1 artifacts and writes separate metadata. |
| benchmark_synthetic.py:25 and 37-43 | Original simulator directly freezes motion when truth is D; this rewards the same assumption used by inference | Retained as legacy test only. New stress suite varies stoppages, live stillness, gaps, contradictory tags, directions and corruption; it remains a simulator, not unbiased accuracy evidence. |

No frame-index or home/away sign error was found in the official-aligned parser.
Future observations are permitted offline; crossing a different sequence's boundary
is the demonstrated coherence bug. Row-wise log-softmax does not change the DP optimum
because it adds a common per-frame constant. Scaling all evidence without scaling
costs **does** change the model; its feature scale and penalties are not independently calibrated.

All-missing, uninformative spans can still choose H by a deterministic state tie.
Neither version reconstructs control without evidence. Diagnostics expose low reliability
and weak transition margins; these values are not calibrated correctness probabilities.
