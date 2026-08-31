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

The fixtures are intentionally small and deterministic. On a GPU host, replace them with real `ncu`, `nsys`, or `rocprof` exports while keeping the normalized schema stable.
