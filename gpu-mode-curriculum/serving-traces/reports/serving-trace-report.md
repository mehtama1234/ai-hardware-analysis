# Serving Trace Replay Report

Generated: `2026-08-31T01:53:08.742726+00:00`
Traces: `3`
Policies: `continuous-batching-prefix-cache, static-batching`

| trace | policy | completed | throughput tok/s | p50 TTFT ms | p95 TTFT ms | mean TPOT ms | peak KV blocks | prefix blocks saved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| long-context-prefix-cache | static-batching | 4/4 | 754.9361 | 245.8 | 373.78 | 0.5 | 325 | 0 |
| long-context-prefix-cache | continuous-batching-prefix-cache | 4/4 | 2255.843 | 21.305 | 25.843 | 0.5619 | 421 | 544 |
| mixed-prefill-decode | static-batching | 6/6 | 1592.3567 | 82.652 | 134.67 | 0.42 | 101 | 0 |
| mixed-prefill-decode | continuous-batching-prefix-cache | 6/6 | 3207.6205 | 7.692 | 14.179 | 0.5007 | 126 | 86 |
| short-chat | static-batching | 5/5 | 1674.4597 | 3.876 | 9.0984 | 0.42 | 14 | 0 |
| short-chat | continuous-batching-prefix-cache | 5/5 | 1689.8355 | 1.9016 | 2.4171 | 0.4286 | 17 | 12 |

## Checks

- `long-context-prefix-cache`: `passed` (all_static_completed=True, all_continuous_completed=True, continuous_throughput_gte_static=True, prefix_cache_saves_blocks=True, p95_ttft_gte_p50=True, kv_peak_within_capacity=True)
- `mixed-prefill-decode`: `passed` (all_static_completed=True, all_continuous_completed=True, continuous_throughput_gte_static=True, prefix_cache_saves_blocks=True, p95_ttft_gte_p50=True, kv_peak_within_capacity=True)
- `short-chat`: `passed` (all_static_completed=True, all_continuous_completed=True, continuous_throughput_gte_static=True, prefix_cache_saves_blocks=True, p95_ttft_gte_p50=True, kv_peak_within_capacity=True)
