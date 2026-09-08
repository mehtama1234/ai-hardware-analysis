# Profiling, tuning and synthesis inventory

## Topic 7: profiler interpretation

[`parser.py`](../profiler-evidence/profiler_evidence/parser.py) reads three small,
deterministic profiler-shaped fixtures. It normalizes their columns and assigns
bottlenecks using thresholds; it does not invoke a profiler. Its report now marks
both the report and each row as `fixture`, `measured: false`.
[`verify_profiler_evidence.py`](../scripts/verify_profiler_evidence.py) checks those
labels, fixture coverage, classifications, remediation text and site presence.
Passing this verifier does not prove a hardware diagnosis.

The normalized CSV schemas are local contracts, not demonstrated adapters for
arbitrary native tool exports. Missing counters are now preserved as `null`,
listed in `missing_metrics`, and classified as `insufficient-data`; they are
not inferred as zero. Hardware acceptance still needs retained native
captures, exact commands and tool/device versions, source/workload hashes,
validated schema adapters, explicit missing-counter handling, and a before/after
kernel explanation. SASS inspection and counter-based optimization remain open.

## Topics 5 and 16: search is not yet synthesis

[`autotune_db/builder.py`](../autotune-db/autotune_db/builder.py) enumerates fixed
configuration dictionaries. `_candidate_rows` multiplies an imported baseline
timing by preset factors, then selects the lowest estimate. It does not compile,
execute or compare candidate kernels. The names `tensorcore-64x64x32` and
`fused-forward-backward` are configurations in this model, not executed candidates.
The [verifier](../scripts/verify_autotune_db.py) checks record coverage and selected
estimated speedups; it does not establish optimization gains.

The newer [Inductor experiment](../compiler-runtime-inspection/README.md) does
capture actual generated CPU forward/backward code and check execution, but it
is not LLM-driven kernel synthesis or formal equivalence verification. The inspected
artifacts do not close topic 16. A bounded synthesis lab still needs candidate
source retention, isolated resource-limited execution, held-out shapes/values,
rejected candidates, oracle comparisons and independently timed finalists.

## Topics 12 and 20: regression and competitive engineering

[`regression_ledger/builder.py`](../regression-ledger/regression_ledger/builder.py)
extracts heterogeneous report metrics and applies fixed thresholds. Some paths
default missing timings to zero, and `_status` accepts unknown metric names by
default. A nonnegative timing can pass without any prior-run comparison. This
is a reporting ledger, not evidence that performance has not regressed.

The newer [executable checkpoint](EXECUTABLE-CHECKPOINT.md) verifies subprocess
success and source/artifact freshness, but does not yet supply statistically
controlled cross-run performance acceptance. Topic 20 additionally needs a
reproducible optimization exercise with a fixed workload, correctness holdouts,
measured baseline/candidates, raw samples and a written explanation of losses
and gains. No competition ranking or external submission is established here.

This audit reviews local source behavior. Primary-source research for these
topics remains incomplete; it makes no claim to have surveyed all implementations
elsewhere in the repository or the handbook's named external projects.
