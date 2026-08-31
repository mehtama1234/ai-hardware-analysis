# Distributed Topology Plan

Generated: `2026-08-31T01:53:09.498485+00:00`
Status: `topology-plan-ready`
Topologies: `5`
Workloads: `5`

## Recommendations

| workload | topology | TP | PP | DP | bottleneck | collective ms | status |
|---|---|---:|---:|---:|---|---:|---|
| llama-7b-chat | single-gpu | 1 | 1 | 1 | compute-or-scheduler | 0.0 | candidate |
| llama-13b-rag | single-gpu | 1 | 1 | 1 | compute-or-scheduler | 0.0 | candidate |
| llama-70b-batch | eight-nvlink | 8 | 1 | 1 | intra-node-collective | 68.1116 | candidate |
| mixtral-8x7b | eight-nvlink | 4 | 2 | 1 | compute-or-scheduler | 21.6907 | candidate |
| dense-70b-sft | sixteen-ib | 8 | 2 | 1 | intra-node-collective | 68.1536 | candidate |

## Candidate Plans

| workload | topology | status | memory GB/GPU | collective ms | bottleneck |
|---|---|---|---:|---:|---|
| llama-7b-chat | single-gpu | candidate | 16.0428 | 0.0 | compute-or-scheduler |
| llama-7b-chat | dual-pcie | candidate | 16.0857 | 7.8305 | compute-or-scheduler |
| llama-7b-chat | eight-nvlink | candidate | 16.3427 | 17.556 | compute-or-scheduler |
| llama-7b-chat | quad-nvlink | candidate | 16.1713 | 23.4675 | compute-or-scheduler |
| llama-7b-chat | sixteen-ib | candidate | 16.6854 | 37.71 | intra-node-collective |
| llama-13b-rag | single-gpu | candidate | 28.2335 | 0.0 | compute-or-scheduler |
| llama-13b-rag | dual-pcie | candidate | 28.467 | 7.8305 | compute-or-scheduler |
| llama-13b-rag | eight-nvlink | candidate | 5.3084 | 21.6907 | compute-or-scheduler |
| llama-13b-rag | sixteen-ib | candidate | 3.6834 | 21.7087 | compute-or-scheduler |
| llama-13b-rag | quad-nvlink | candidate | 8.5584 | 32.53 | intra-node-collective |
| llama-70b-batch | eight-nvlink | candidate | 19.5339 | 68.1116 | intra-node-collective |
| llama-70b-batch | sixteen-ib | candidate | 10.7839 | 68.1536 | intra-node-collective |
| llama-70b-batch | quad-nvlink | candidate | 37.0677 | 175.03 | intra-node-collective |
| llama-70b-batch | single-gpu | rejected-memory | 142.2709 | 0.0 | memory-capacity |
| llama-70b-batch | dual-pcie | rejected-memory | 72.1355 | 1093.768 | memory-capacity |
| mixtral-8x7b | eight-nvlink | candidate | 13.7792 | 21.6907 | compute-or-scheduler |
| mixtral-8x7b | sixteen-ib | candidate | 7.9042 | 21.7087 | compute-or-scheduler |
| mixtral-8x7b | quad-nvlink | candidate | 25.5292 | 32.53 | intra-node-collective |
| mixtral-8x7b | single-gpu | rejected-memory | 96.1168 | 0.0 | memory-capacity |
| mixtral-8x7b | dual-pcie | rejected-memory | 96.2335 | 7.8305 | memory-capacity |
| dense-70b-sft | sixteen-ib | candidate | 45.0 | 68.1536 | intra-node-collective |
| dense-70b-sft | single-gpu | rejected-scale | 570.0 | 0.0 | insufficient-data-parallel-scale |
| dense-70b-sft | eight-nvlink | rejected-memory | 80.0 | 68.1116 | memory-capacity |
| dense-70b-sft | quad-nvlink | rejected-scale | 150.0 | 175.03 | insufficient-data-parallel-scale |
| dense-70b-sft | dual-pcie | rejected-scale | 290.0 | 1093.768 | insufficient-data-parallel-scale |

## GPU Host Promotion

This planner is source-ready locally; final acceptance requires measured NCCL/RCCL bandwidth and serving/training throughput on the selected topology.
