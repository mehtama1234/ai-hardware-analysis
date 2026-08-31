# Serving Trace Replay Lab

This layer turns the vLLM/KV-cache topic into an end-to-end serving systems lab.
It replays deterministic request traces through two policies:

- `static-batching`: one request at a time with no prefix cache reuse.
- `continuous-batching-prefix-cache`: admission over arrivals, prefill sharing,
  decode interleaving, and KV block accounting.

The local simulator is intentionally CPU-only so it can run in CI and on this
machine. A GPU host should replace the timing constants with measurements from
vLLM, SGLang, TGI, TensorRT-LLM, or a custom server while keeping the report
schema stable.

## Run

```bash
python3 scripts/run_serving_traces.py
python3 scripts/verify_serving_traces.py
```

The generated report includes TTFT, TPOT, output-token throughput, prefix-cache
block savings, peak live KV blocks, and request-level timelines.
