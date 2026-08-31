# GPUMODE MoE Routing and All-to-All

Generated: `2026-08-31T01:53:15.494490+00:00`
Status: `moe-routing-ready`

| scenario | status | drop rate | fairness | imbalance | payload GB | all-to-all ms | bottleneck |
|---|---|---:|---:|---:|---:|---:|---|
| balanced-chat | passed | 0.0 | 0.993039 | 1.173828 | 0.033554 | 0.113886 | balanced |
| skewed-agent-tools | needs-capacity-or-router-tuning | 0.393921 | 0.516176 | 2.708984 | 0.040673 | 0.131683 | router-load-imbalance |
| long-context-mixtral | passed | 0.183044 | 0.718973 | 2.089355 | 0.10965 | 0.269208 | router-load-imbalance |
| cross-node-moe | passed | 0.149261 | 0.78827 | 1.909668 | 0.342553 | 1.815715 | router-load-imbalance |
| training-microbatch | passed | 0.096893 | 0.896499 | 1.618164 | 0.969703 | 1.941534 | capacity-drops |

## GPU Host Promotion

- `torchrun --nproc_per_node=8 <moe_router_probe.py>`
- `nsys profile -o moe-all-to-all torchrun --nproc_per_node=8 <moe_router_probe.py>`
- `ncu --set full -o moe-expert-kernels python3 <moe_expert_kernel_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id moe-routing-all-to-all --execute`
