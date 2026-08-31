# GPUMODE Distributed Training Optimizer

Generated: `2026-08-31T01:53:15.261928+00:00`
Status: `training-optimizer-ready`

| scenario | strategy | ranks | memory GB/GPU | exposed comm ms | bubble ms | tokens/s | status |
|---|---|---:|---:|---:|---:|---:|---|
| ddp-7b-nvlink-baseline | ddp | 8 | 74.0 | 21.222444 | 0.0 | 281942.099537 | passed |
| zero2-13b-pcie | zero-2 | 4 | 59.045 | 228.2145 | 0.0 | 41143.65499 | review |
| fsdp-70b-ib-checkpoint | fsdp-full-shard | 16 | 53.59 | 240.1475 | 0.0 | 131052.669731 | passed |
| zero3-70b-ib-offload-risk | zero-3 | 16 | 58.49 | 121.1475 | 36.0 | 61993.241246 | passed |
| pipeline-tp-70b-ib | tp-pp-fsdp | 16 | 63.025 | 0.0 | 96.0 | 248242.424242 | passed |
| fp8-fsdp-70b-ib | fsdp-full-shard | 16 | 48.615 | 0.0 | 0.0 | 234057.142857 | passed |

## GPU Host Promotion

- `python3 scripts/run_distributed_training_optimizer.py`
- `python3 scripts/verify_distributed_training_optimizer.py`
- `torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>`
- `nsys profile -o fsdp-zero-step torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id distributed-training-optimizer --execute`
