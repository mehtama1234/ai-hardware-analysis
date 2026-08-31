# GPUMODE FlashAttention to vLLM Serving Stack

Generated: `2026-08-31T01:53:08.945279+00:00`
Status: `attention-serving-ready`

| scenario | status | HBM reduction | shared memory | intensity | scheduler | prefix blocks reused |
|---|---|---:|---:|---:|---|---:|
| short-chat-prefill-decode | passed | 0.661458 | 25088 | 63.0154 | chunked-prefill-continuous-batching | 480 |
| long-context-rag | passed | 0.876498 | 82432 | 454.3224 | prefill-first-graph-bucket | 3584 |
| agent-prefix-cache | passed | 0.780107 | 82432 | 227.1612 | chunked-prefill-continuous-batching | 17664 |
| mixed-batch-tail-latency | passed | 0.652423 | 25088 | 60.1248 | chunked-prefill-continuous-batching | 3968 |
| quantized-wide-heads | passed | 0.876284 | 41472 | 453.5363 | chunked-prefill-continuous-batching | 2816 |

## GPU Host Promotion

- `python3 scripts/run_gpu_host_preflight.py`
- `python3 scripts/run_attention_serving_stack.py`
- `python3 scripts/verify_attention_serving_stack.py`
- `nsys profile -o flashattention-serving python3 <vllm_trace_replay.py>`
- `ncu --set full -o flashattention-kernel python3 <flash_attention_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id attention-serving-stack --execute`
