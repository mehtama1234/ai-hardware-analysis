# GPUMODE speculative decoding serving

Generated: `2026-08-31T01:53:09.416202+00:00`
Status: `speculative-decoding-ready`

| scenario | workload | engine | status | draft | accept | speedup | wasted ratio | scheduler |
|---|---|---|---|---:|---:|---:|---:|---|
| chat-medusa-draft | interactive-chat | vllm-or-sglang | passed | 4 | 0.72 | 4.725 | 0.28 | speculative-continuous-batching |
| rag-eagle-long-context | long-context-rag | vllm | passed | 6 | 0.66 | 6.6498 | 0.34 | speculative-continuous-batching |
| code-assistant-bursty | mixed-prefill-decode | sglang | passed | 5 | 0.61 | 4.6814 | 0.39 | speculative-continuous-batching |
| offline-throughput-ngram | offline-throughput | tgi-or-vllm | passed | 8 | 0.58 | 6.2445 | 0.42 | speculative-continuous-batching |
| portable-hf-assisted | portable-amd-nvidia | hf-transformers | review | 3 | 0.69 | 3.1625 | 0.31 | speculative-continuous-batching |
| low-acceptance-rollback | adversarial-domain-shift | vllm | review | 6 | 0.43 | 3.1794 | 0.57 | rollback-aware-target-first |

## GPU Host Promotion

- `python3 scripts/run_speculative_decoding_serving.py`
- `python3 scripts/verify_speculative_decoding_serving.py`
- `python3 scripts/run_serving_traces.py`
- `python3 scripts/run_serving_engine_comparison.py`
- `nsys profile -o speculative-decoding-serving python3 <speculative_serving_probe.py>`
- `ncu --set full -o speculative-target-verify python3 <target_verify_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id speculative-decoding-serving --execute`
