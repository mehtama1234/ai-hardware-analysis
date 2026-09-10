# Mixed-length continuous HTTP arrival measurements

Pinned GPT-2 on T4, two slots, eight pending requests, output budgets 1/8/16/32.
Two rounds of eight-second arrival windows. These are bounded loopback measurements.

| Run | Offered requests/s | Completed | Rejected | TTFT p95 ms | Completion p95 ms | Goodput requests/s | Arrival lateness p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| r0-rate4 | 4 | 32 | 0 | 26.84 | 150.55 | 4.09 | 0.34 |
| r0-rate16 | 16 | 128 | 0 | 25.82 | 174.44 | 15.99 | 1.51 |
| r0-rate48 | 48 | 224 | 160 | 392.87 | 476.62 | 26.66 | 0.83 |
| r1-rate48 | 48 | 197 | 187 | 445.09 | 545.58 | 23.57 | 1.89 |
| r1-rate16 | 16 | 128 | 0 | 26.89 | 176.64 | 15.97 | 1.63 |
| r1-rate4 | 4 | 32 | 0 | 24.01 | 146.61 | 4.09 | 0.37 |

Goodput counts correct requests with TTFT <=1,000 ms, completion <=3,000 ms, and maximum inter-token gap <=500 ms. Its denominator includes drain time.

Accepted requests match individual reference tokens; rejected requests and server records reconcile. Controlled HTTP EOS termination passes.

No matched-baseline advantage or independent dynamic-engine replay is established here. Prefill remains synchronous and unchunked.

[Machine-readable decision](continuous-load-decision.json) · [Run instructions](../batch1-decode-vertical-slice/SLOT-DECODE.md)
