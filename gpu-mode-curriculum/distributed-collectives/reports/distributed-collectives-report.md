# GPUMODE Distributed Collectives

Generated: `2026-08-31T01:53:09.646714+00:00`
Status: `distributed-collectives-ready`

| scenario | collective | algorithm | ranks | backend | exposed ms | efficiency | overlap gain | status |
|---|---|---|---:|---|---:|---:|---:|---|
| dp-grad-all-reduce-nvlink | all-reduce | ring | 8 | nccl | 0.0 | 0.555797 | 0.214422 | passed |
| tp-activation-all-gather | all-gather | ring | 4 | nccl | 0.0 | 1.273632 | 0.13215 | passed |
| zero-reduce-scatter-pcie | reduce-scatter | ring | 4 | nccl | 3.627 | 1.329345 | 0.256813 | passed |
| moe-expert-all-to-all-ib | all-to-all | pairwise | 16 | nccl/nvshmem | 0.0 | 0.980843 | 0.191771 | passed |
| small-control-broadcast | broadcast | tree | 8 | nccl | 0.012 | 0.769231 | 0.088496 | passed |
| amd-rccl-grad-all-reduce | all-reduce | ring | 8 | rccl | 0.0 | 0.552438 | 0.278586 | passed |

## GPU Host Promotion

- `python3 scripts/run_gpu_host_preflight.py`
- `python3 scripts/run_distributed_collectives.py`
- `python3 scripts/verify_distributed_collectives.py`
- `torchrun --nproc_per_node=2 <collective_benchmark.py>`
- `nccl-tests/build/all_reduce_perf -b 8M -e 1G -f 2 -g 1`
- `rocprof <rccl_collective_benchmark>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id distributed-collectives --execute`
