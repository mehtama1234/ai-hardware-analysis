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
```

The report is written to `reports/decode-comparison.json`. CPU output is a
correctness and timing baseline only. GPU acceptance additionally requires
synchronized CUDA-event timing, Nsight evidence, and the same comparison
through the HTTP tail-load path.

The serving bridge writes `reports/serving-bridge.json` and compares the same
two decode modes through the loopback HTTP endpoint at concurrency 1, 2, and 4.

Verify captured reports without rerunning the experiment:

```bash
python3 batch1-decode-vertical-slice/verify_reports.py
# or verify an imported GPU handoff without replacing the local baseline
python3 batch1-decode-vertical-slice/verify_reports.py \
  --reports-dir gpu-runs/imports/<run-id>
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

## Latest captured GPU evidence

Run `colab-t4-batch1-decode-20260908-r3` passed on an NVIDIA T4 with both
reports marked `measured_gpu`. All four prompts matched token IDs and logits;
the serving bridge completed 8 requests at concurrency 1, 2, and 4 for both
decode modes with cross-mode output parity. On this deliberately small,
untrained teaching model, KV caching was slower (roughly 0.71–0.77x direct
wall-clock speedup), so this run validates the end-to-end measurement and
correctness path rather than claiming an optimization win.
