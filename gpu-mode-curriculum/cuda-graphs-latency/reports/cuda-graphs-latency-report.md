# GPUMODE CUDA Graphs Latency Stabilization

Generated: `2026-08-31T01:53:26.175134+00:00`
Status: `cuda-graphs-ready`

## Scenario Results

| scenario | status | eager p95 ms | graph p95 ms | p95 reduction | jitter reduction | fallback |
|---|---|---:|---:|---:|---:|---|
| static-decode-batch-1 | capture-ready | 0.091243 | 0.013743 | 0.849381 | -0.0 | capture decode buckets |
| static-decode-batch-8 | capture-ready | 0.207943 | 0.050943 | 0.755014 | -0.0 | capture decode buckets |
| bucketed-prefill-2k | capture-ready | 0.271243 | 0.016243 | 0.940117 | 0.0 | capture decode buckets |
| rag-dynamic-prefill | fallback-required | 0.13257 | 0.13257 | 0.0 | 0.0 | bucket variable shapes or keep eager for dynamic prefill/adapters |
| mixed-adapter-routing | fallback-required | 0.121534 | 0.121534 | 0.0 | 0.0 | bucket variable shapes or keep eager for dynamic prefill/adapters |

## GPU Promotion Commands

- `python3 scripts/run_gpu_host_preflight.py`
- `python3 scripts/run_gpu_promotion_suite.py --run-id cuda-graphs-latency --execute`
- `nsys profile -o cuda-graphs-decode python3 <serving_decode_probe.py>`
- `ncu --set full -o cuda-graphs-kernels python3 <captured_kernel_probe.py>`
- `vllm serve <model> --enforce-eager=false --max-seq-len-to-capture <tokens>`
