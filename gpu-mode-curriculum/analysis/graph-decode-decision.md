# Fixed-batch graph-decode decision

Pinned GPT-2 float32 on T4; fixed batches, 16 output tokens in the default protocol; no serving-capacity claim

Compare dynamic/static eager to isolate cache implementation effects; compare static eager/graph to isolate captured host dispatch. Graph replay still executes GPU kernels.

| Session | Batch | Fixture | Native ms | Static ms | Graph ms | Native / graph | Max logit error |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| graph-decode-20260909T184008 | 1 | 0 | 136.72 | 130.34 | 52.61 | 2.60 | 7.62939e-05 |
| graph-decode-20260909T184008 | 1 | 1 | 239.49 | 233.29 | 60.01 | 3.99 | 0.00012207 |
| graph-decode-20260909T184008 | 1 | 2 | 224.17 | 213.10 | 63.01 | 3.56 | 0.000274658 |
| graph-decode-20260909T184008 | 4 | 0 | 187.25 | 169.62 | 84.35 | 2.22 | 7.62939e-05 |
| graph-decode-20260909T184008 | 4 | 1 | 187.24 | 169.26 | 76.84 | 2.44 | 0.000152588 |
| graph-decode-20260909T184008 | 4 | 2 | 205.88 | 181.89 | 89.52 | 2.30 | 0.00152588 |
| graph-decode-20260909T184413 | 1 | 0 | 159.50 | 139.15 | 55.41 | 2.88 | 7.62939e-05 |
| graph-decode-20260909T184413 | 1 | 1 | 198.90 | 184.57 | 59.68 | 3.33 | 0.00012207 |
| graph-decode-20260909T184413 | 1 | 2 | 260.00 | 186.88 | 67.27 | 3.87 | 0.000274658 |
| graph-decode-20260909T184413 | 4 | 0 | 226.33 | 204.42 | 84.93 | 2.66 | 7.62939e-05 |
| graph-decode-20260909T184413 | 4 | 1 | 223.09 | 206.22 | 79.91 | 2.79 | 0.000152588 |
| graph-decode-20260909T184413 | 4 | 2 | 211.45 | 182.50 | 88.68 | 2.38 | 0.00152588 |

Stage samples have extra synchronization and are not additive components of uninstrumented wall time. Dynamic prefill stage starts after initial cache/position setup; static prefill includes validation and cache reset. ATen self time excludes runtime attribution and is not end-to-end latency.

Full stage measurements and launch counts: [JSON evidence](graph-decode-decision.json).

Open gates: dynamic admission, per-slot cache reclamation, HTTP integration, sustained workload envelope.
