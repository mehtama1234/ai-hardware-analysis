# Profiler Evidence Report

Rows: 9
Sources: 3

## Classification Counts

- `cache-locality`: 1
- `communication`: 1
- `compute-occupancy`: 1
- `host-device-transfer`: 1
- `launch-overhead`: 1
- `memory-bandwidth`: 2
- `mixed`: 1
- `tensor-core-compute`: 1

## Rows

| Source | Name | Classification | Duration us | Remediation |
|---|---|---|---|---|
| nsight-compute | vector_copy_strided | memory-bandwidth | 412.0 | coalesce or vectorize memory access; raise arithmetic intensity; add tiling/reuse before retiming |
| nsight-compute | wgmma_gemm_mainloop | tensor-core-compute | 193.0 | inspect MMA tile shape; check tensor-core eligibility; compare occupancy against stall reasons |
| nsight-compute | row_softmax_small | cache-locality | 77.0 | change layout or blocking; reduce gathers; separate L2-hit and DRAM-bound kernels |
| nsight-systems | token_prefill | host-device-transfer | 9100.0 | remove sync copies; pin and batch transfers; move preprocessing onto device |
| nsight-systems | decode_step_batch_1 | launch-overhead | 1400.0 | fuse small kernels; use CUDA graphs; batch decode work |
| nsight-systems | all_reduce_logits | communication | 760.0 | compare ring/tree/channel topology; increase payload aggregation; inspect overlap with compute |
| rocprof | hip_vector_add | mixed | 533.0 | split by kernel; collect roofline counters; compare against baseline |
| rocprof | ck_gemm_xdl | compute-occupancy | 221.0 | reduce register pressure; check wave occupancy; try smaller tiles |
| rocprof | hip_layernorm | memory-bandwidth | 118.0 | coalesce or vectorize memory access; raise arithmetic intensity; add tiling/reuse before retiming |
