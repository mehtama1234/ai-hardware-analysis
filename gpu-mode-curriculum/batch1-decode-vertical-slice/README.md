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
  --reports-dir gpu-runs/imports/colab-t4-batch1-graphs-serving-20260908 \
  --profiler-dir gpu-runs/imports/colab-t4-batch1-graph-profile-20260908
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

The widened T4 run showed that preallocation alone is not sufficient: its
long-context gain did not survive the HTTP path. The CUDA Graph path then
reduced direct CUDA-event decode time by 2.70–4.04x and reduced loopback HTTP
median latency across the measured workloads and concurrency levels, while
preserving exact outputs. Graph capture is restricted to fixed batch-1 buckets;
dynamic shapes require an eager fallback.

## Latest captured GPU evidence

Run `colab-t4-batch1-graphs-serving-20260908` passed on an NVIDIA T4 with
decode and serving marked `measured_gpu`. The graph profiler refresh
`colab-t4-batch1-graph-profile-20260908` observed both `cudaGraphLaunch` and
`_append_kv_kernel`. All workloads matched token IDs and logits; the serving
bridge completed 8 requests at concurrency 1, 2, and 4 for every mode with
cross-mode output parity.
