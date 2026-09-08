# Measured speculative decoding

The local `speculative-decoding-report.json` is a scheduler/accounting model.
The CUDA runner is the executable boundary:

```bash
python3 speculative-decoding-serving/run_speculative_decoding_cuda.py
python3 speculative-decoding-serving/verify_speculative_decoding_cuda.py \
  --report gpu-runs/imports/<run-id>/speculative-decoding-cuda.json
```

The runner uses a target character transformer and a deliberately different
draft transformer. It verifies each proposed suffix in one vectorized target
forward, records accepted and rolled-back draft tokens, logical KV commits,
CUDA-event timings, and requires exact greedy-target parity. CUDA is required;
the local machine writes an explicit unavailable report instead of falling back
to CPU.

The accepted T4 artifact is
`gpu-runs/imports/colab-t4-speculative-20260908-r5/speculative-decoding-cuda.json`.
It covers four scenarios, including an exact-draft control and low-acceptance
shifted drafts. All outputs match ordinary target decoding, rollback and KV
commit accounting pass, and CUDA timings are present.

The runner also measures an acceptance-gated policy. The always-speculative
path measured about 0.15–0.19x baseline for the zero-acceptance smaller drafts;
the policy fell back after the probe and improved those cases to about
0.76–0.86x while preserving parity. The exact-draft control measured about
0.97x. This is still not a speedup claim: it is evidence that admission policy
can prevent a bad draft from catastrophically regressing latency, while a
compatible cheap draft is still needed to produce a positive gain.
