# Batch-1 Decode Vertical Slice

This is the next end-to-end GPU-systems slice:

`reference decode -> KV-cached decode -> model output parity -> timing -> serving integration -> profiler`

The first executable comparison uses the existing untrained character
transformer and deliberately holds weights, prompts, token count, and greedy
sampling constant. `uncached` recomputes the full prefix for every token;
`cached` appends one token to the model's KV tensors after prefill.

Run locally from the curriculum root:

```bash
python3 batch1-decode-vertical-slice/run_decode_comparison.py
python3 batch1-decode-vertical-slice/run_serving_bridge.py
python3 batch1-decode-vertical-slice/run_profiler_evidence.py
```

The report is written to `reports/decode-comparison.json`. CPU output is a
correctness and timing baseline only. GPU acceptance additionally requires
synchronized CUDA-event timing, Nsight evidence, and the same comparison
through the HTTP tail-load path.

The serving bridge writes `reports/serving-bridge.json` and compares the same
three decode modes through the loopback HTTP endpoint at concurrency 1, 2, and
4. The protocol measures short-context/12-token, long-context/24-token, and
long-decode/96-token workloads, so cache behavior is not inferred from only a
toy prompt.

Verify captured reports without rerunning the experiment:

```bash
python3 batch1-decode-vertical-slice/verify_reports.py
# or verify an imported GPU handoff without replacing the local baseline
python3 batch1-decode-vertical-slice/verify_reports.py \
  --reports-dir gpu-runs/imports/<run-id>
# A profiler-only refresh may be supplied explicitly when its capture is a
# separate GPU session.
python3 batch1-decode-vertical-slice/verify_reports.py \
  --reports-dir gpu-runs/imports/colab-t4-batch1-batchgraphs-20260908
```

## Acceptance contract

- identical generated token IDs and per-step logits within tolerance;
- fixed prompt suite, model seed, data seed, warmups, repeats, and token count;
- raw wall-clock samples for both paths, plus CUDA-event samples when CUDA is
  available;
- separate prefill and decode timing scope;
- source hashes for the runner and model implementation;
- explicit evidence kind: `measured_cpu`, `measured_gpu`, or unavailable;
- no speedup claim without application-level serving evidence.
- profiler evidence must show CUDA activity on GPU runs and must not show more
`aten::cat` calls for preallocated storage than for dynamic cache storage.

The comparison also records a bounded candidate search for each workload. It
enumerates the available cached, preallocated, and CUDA-graph paths, applies
token and logit parity to every candidate, and selects the fastest accepted
candidate using synchronized CUDA-event medians when available (wall medians
otherwise). A candidate that is faster but changes outputs is retained as
rejected evidence and cannot be selected.

The widened T4 run showed that preallocation alone is not sufficient: its
long-context gain did not survive the HTTP path. The CUDA Graph path then
reduced direct CUDA-event decode time by 2.74–4.37x and reduced loopback HTTP
median latency across the measured workloads and concurrency levels, while
preserving exact outputs. A four-slot graph pool supports concurrency 1/2/4
without racing static buffers. Graph capture is restricted to fixed batch-1
buckets; dynamic shapes require an eager fallback.

## Latest captured GPU evidence

Run `colab-t4-batch1-buckets-20260908` passed on an NVIDIA T4 with
decode and serving marked `measured_gpu`. The graph profiler refresh
`colab-t4-batch1-graph-profile-20260908` observed both `cudaGraphLaunch` and
`_append_kv_kernel`. All workloads matched token IDs and logits; the serving
bridge completed 8 requests at concurrency 1, 2, and 4 for every mode with
cross-mode output parity. An unseen `(prompt, max_tokens)` pair was explicitly
served by the eager fallback and labeled
`neural-cuda_graph-decode-fallback`; it did not trigger capture on the request
path.

The same run also exercises the bounded arrival-window microbatch scheduler.
The latest T4 report (`colab-t4-batch1-microbatch-20260908`) formed 42 batches,
including 18 vectorized groups with observed sizes 1/2/4, rejected zero
requests, and preserved parity. At concurrency 4, vectorized microbatching
reduced long-context median latency to about 26 ms versus about 66 ms for the
uncached path; the CUDA Graph pool remains the lower-latency fixed-bucket
option.

The batch-aware graph scheduler is also measured in
`colab-t4-batch1-batchgraphs-20260908`: equal-length groups use
`cuda-graph-vectorized` buckets for batch sizes 2/4, singleton groups remain
`single`, and all outputs remain parity-checked. At concurrency 4 on the
long-decode workload, graph microbatching measured about 15.6 ms median versus
about 99.9 ms for vectorized eager microbatching.

The bounded candidate-search handoff
`colab-t4-batch1-search-20260908/decode-comparison.json` passed on T4. It
selected `cuda-graph` for all three direct-decode workloads, with CUDA-event
speedups of 2.88x, 3.70x, and 2.78x versus full-prefix recomputation. Every
candidate passed exact token/logit parity; this is direct decode evidence, not
yet a replacement for the separate HTTP serving and profiler gates.

The combined handoff
`colab-t4-batch1-e2e-20260908/` passed all three gates together: decode
candidate selection, HTTP serving parity at concurrency 1/2/4, and profiler
capture. It observed CUDA-graph microbatch vectorization and dynamic fallback,
so the selected direct-decode candidate was exercised through the application
boundary as well as measured in isolation.
