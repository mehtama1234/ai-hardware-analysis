# GPUMODE KV Cache and PagedAttention

Generated: `2026-08-31T01:53:08.838305+00:00`
Status: `kv-cache-ready`

| scenario | status | peak block savings | waste reduction | admission delta | prefix blocks reused |
|---|---|---:|---:|---:|---:|
| chat-short-mixed | passed | 12 | -0.000992 | 0 | 16 |
| long-context-rag | passed | 32 | 0.0 | 1 | 192 |
| prefix-heavy-agents | passed | 130 | 0.0 | 0 | 440 |
| fragmented-adapters | passed | 0 | 0.0 | 0 | 0 |
| capacity-pressure | passed | 0 | 0.0 | 0 | 0 |

## GPU Host Promotion

- `python3 scripts/run_gpu_host_preflight.py`
- `vllm serve <model> --enable-prefix-caching --block-size 16`
- `python3 scripts/run_serving_traces.py`
- `nsys profile -o paged-attention python3 <vllm_trace_replay.py>`
- `ncu --set full -o kv-cache-kernels python3 <paged_attention_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id kv-cache-paged-attention --execute`
