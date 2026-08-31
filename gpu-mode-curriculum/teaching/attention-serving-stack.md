# Attention Serving Stack

## First Question

Attention can spend memory on materialized score matrices and on cached keys and values. Serving also cares about first token delay and time per output token. This lane asks how tiling, online softmax, batching, and KV reuse change those numbers.

## What The Code Does

- `attention-serving-stack/attention_serving_stack/analyzer.py builds the scenario metrics.`
- `serving-traces/serving_traces/replay.py simulates request scheduling.`
- `kv-cache-paged-attention/kv_cache_paged_attention/simulator.py handles block-table style KV accounting.`

## What The Measurement Proves

The measurement proves the scenarios track HBM reduction, shared memory size, prefix reuse, and serving policy fields under one contract.

## What It Does Not Prove

It does not prove production vLLM throughput. It proves the serving variables are exposed and testable before a real serving engine run.

## Read Next

- `site/attention-serving-stack.html`
- `site/serving-traces.html`
- `site/kv-cache-paged-attention.html`
