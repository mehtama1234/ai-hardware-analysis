# GPUMODE parallel primitives

Generated: `2026-08-31T01:52:59.584702+00:00`
Status: `parallel-primitives-ready`

| scenario | primitive | algorithm | efficiency | bandwidth proxy GB/s | occupancy | status |
|---|---|---|---:|---:|---:|---|
| warp-block-reduction-bf16 | reduction | warp-shuffle-block-tree | 1.7273 | 61.0081 | 1.0 | passed |
| exclusive-prefix-scan-int32 | scan | blelloch-hillis-steele-hybrid | 1.6471 | 59.2137 | 1.0 | passed |
| predicate-stream-compaction | compaction | scan-scatter | 1.6364 | 114.3901 | 1.0 | passed |
| radix-sort-pass-32bit-keys | sort | histogram-scan-scatter-radix8 | 1.5263 | 17.6602 | 1.0 | passed |
| shared-histogram-token-bins | histogram | block-private-shared-atomics | 1.6296 | 49.7103 | 1.0 | passed |
| segmented-reduce-ragged-batches | segmented-reduction | head-flag-scan-reduce | 1.4194 | 16.236 | 1.0 | passed |

## GPU Host Promotion

- `python3 scripts/run_parallel_primitives.py`
- `python3 scripts/verify_parallel_primitives.py`
- `python3 kernel-benchmarks/kernels/triton/reduction.py`
- `python3 kernel-benchmarks/kernels/cuda/reduction.cu`
- `ncu --set full -o parallel-primitives python3 <parallel_primitives_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id parallel-primitives --execute`
