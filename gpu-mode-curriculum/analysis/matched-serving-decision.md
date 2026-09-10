# Matched native/graph serving comparison

Pinned GPT-2 on T4. Identical offered prompts, output budgets, rates, slot and queue limits; three counterbalanced rounds per rate.

| Offered requests/s | Mode | Completed | Rejected | Median window goodput | Median window completion p95 ms |
| --- | --- | ---: | ---: | ---: | ---: |
| 16 | native_microbatch | 205 | 179 | 4.22 | 1717.30 |
| 16 | graph_microbatch | 384 | 0 | 15.90 | 226.00 |
| 16 | graph_continuous | 384 | 0 | 15.97 | 174.78 |
| 48 | native_microbatch | 212 | 940 | 3.50 | 1951.96 |
| 48 | graph_microbatch | 425 | 727 | 16.61 | 673.44 |
| 48 | graph_continuous | 646 | 506 | 26.33 | 491.08 |

Latency columns are medians of three per-window p95 values, not pooled request percentiles. Goodput uses the declared latency targets and includes drain time.

Native vs graph includes execution and prefill implementation changes. Graph group vs continuous compares grouping/admission policies using the same slot engine. Overload accepted-budget mixes are retained; no universal capacity claim.

Graph allocations remain resident in every mode; native microbatch adds its dynamic cache. These are not isolated minimum-memory measurements.

Independent matched-serving replay remains open. [Raw-derived JSON, budget mixes, and paired comparisons](matched-serving-decision.json).
