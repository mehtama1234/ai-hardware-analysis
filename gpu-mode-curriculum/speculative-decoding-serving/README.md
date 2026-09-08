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
`gpu-runs/imports/colab-t4-speculative-20260908-r4/speculative-decoding-cuda.json`.
It covers four scenarios, including an exact-draft control and low-acceptance
shifted drafts. All outputs match ordinary target decoding, rollback and KV
commit accounting pass, and CUDA timings are present.

This run intentionally does not claim a speedup: the equal-size exact draft
measured about 0.93x baseline, while the smaller shifted drafts measured about
0.15–0.19x because their acceptance was zero. That is the measured design
boundary: speculative decoding needs a compatible, cheap draft model before
draft work can amortize target verification.
