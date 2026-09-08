# GPUMODE Profiler Evidence

This layer turns profiler-shaped exports into a normalized bottleneck report.

Inputs:

- `fixtures/nsight_compute_kernels.csv`
- `fixtures/nsight_systems_timeline.json`
- `fixtures/rocprof_kernels.csv`

Run:

```bash
python3 scripts/run_profiler_evidence.py
python3 scripts/verify_profiler_evidence.py
```

Outputs:

- `profiler-evidence/reports/profiler-evidence-report.json`
- `profiler-evidence/reports/profiler-evidence-report.md`

The normalized nine-row table is deliberately fixture-only. The report also
links one separately labeled native Colab Nsight Compute/SASS capture for the
WMMA tensor-core path; that capture is measured GPU evidence and is not merged
into the heuristic fixture classifications.

The fixtures are intentionally small and deterministic. Their report and every
row remain labeled `fixture`, with no measured GPU execution accepted. Keep
these fixtures for parser regression tests. Future real captures need separate
artifacts and validated native-export adapters, retaining tool versions, commands,
source identity and raw captures; merely replacing a fixture file is not enough
to establish measurement provenance.

Missing profiler counters are preserved as `null` and listed in each row's
`missing_metrics` field. Such rows classify as `insufficient-data`; an absent
counter is never silently converted to zero or used to claim a bottleneck.
