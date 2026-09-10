# Serving capstone decision: bounded shape and budget graph buckets

Decision date: 2026-09-10

## Decision

Promote the StaticCache plus SDPA CUDA Graph bucket as a **bounded serving
component** for fixed-shape decode on supported CUDA devices. Keep native
batched execution as the comparison baseline and retain an eager dynamic
fallback. Do not promote the graph bucket as a universal serving engine or as
a T4 performance win until the target-hardware comparison is rerun.

## Evidence

The workload is pinned `EleutherAI/pythia-70m`, revision
`a39f36b100fe8a5377810d56c3f4789b9c53ac42`. The graph uses batch size two,
tokenized prompt-width buckets, StaticCache, SDPA masking, and recapture for
each cache lifetime. Every accepted request is checked against an independent
Transformers `generate` reference.

The mixed-budget HTTP report is
`gpu-runs/imports/pythia-mixed-budget-backpressure-20260910T190000/reports/static-graph-http.json`.
It passed exact parity for eight requests across two prompt widths and output
budgets of four and eight tokens. A 12-request overload produced four HTTP 200
responses and eight HTTP 429 responses, and all queues drained.

The sustained report is
`gpu-runs/imports/pythia-mixed-budget-sustained-20260910T200000/reports/static-graph-http.json`.
Three primary rounds served 144 tokens with exact parity. Recapture cost was
102.986 ms total, 4.291 ms per primary request, and 0.715 ms per primary token.
Peak allocated memory was 268,818,432 bytes on an NVIDIA A100-SXM4-40GB.

## What this establishes

The implementation has a tested admission boundary for prompt width and
output budget, a bounded overload policy, a safe recapture lifecycle, and a
measured amortization signal under repeated arrivals. Singleton scheduler
groups are padded inside the fixed graph and expose events only for the real
request, preserving graph shape without reporting duplicate work as a user
request.

The result is a systems decision about correctness and bounded behavior. The
loopback endpoint is not a production capacity benchmark, and A100 numbers are
not interchangeable with earlier T4 measurements.

## Open gates

1. Repeat the mixed-budget and sustained protocol on T4 or the deployment GPU.
2. Compare graph buckets against native batching and eager dynamic fallback
   under matched duration, latency targets, memory, and rejection semantics.
3. Add cancellation, prefix reuse, chunked prefill, and recovery probes as
   separate interventions.
4. Replay the accepted source bundle from a fresh environment and retain the
   verifier output with the report.

This decision closes one bounded C-package milestone. It does not close the
long-term GPU systems program, whose distributed, portability, multimodal, and
broader kernel capstones remain open.
