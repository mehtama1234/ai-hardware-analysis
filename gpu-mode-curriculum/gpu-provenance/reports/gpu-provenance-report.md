# GPUMODE GPU Evidence Provenance

Generated: `2026-09-08T18:00:21.734265+00:00`
Status: `provenance-clear`
Real GPU evidence: `present`
Measured GPU runs: `3`

## Summary

- Sample fixture runs: `2`
- Host-collected runs: `1`
- Rows with provenance: `89/89`

## Runs

| run | provenance | measured | vendor | accelerator | rows | passed | skipped | failed |
|---|---|---:|---|---|---:|---:|---:|---:|
| `colab-advanced-phase` | `real-measured` | `True` | NVIDIA | Tesla T4 | 18 | 15 | 3 | 0 |
| `colab-full-20260908` | `real-measured` | `True` | NVIDIA | Tesla T4 | 18 | 15 | 3 | 0 |
| `colab-t4-promoted-20260907` | `real-measured` | `True` | NVIDIA | Tesla T4 | 23 | 21 | 0 | 0 |
| `local-cpu-collector-smoke` | `host-collected` | `False` | unknown | unavailable | 16 | 0 | 16 | 0 |
| `sample-a100-gpu-run` | `sample-fixture` | `False` | NVIDIA | NVIDIA A100 | 9 | 9 | 0 | 0 |
| `sample-mi300-gpu-run` | `sample-fixture` | `False` | AMD | AMD MI300 | 5 | 5 | 0 | 0 |
