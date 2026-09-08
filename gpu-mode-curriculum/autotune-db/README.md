# Autotuning Database

This layer converts benchmark reports into reusable tuning records. Each record
binds an operator family and shape class to candidate launch/block
configurations, a selected starting config, modeled speedup, and promotion
targets for CUDA, Triton, or PyTorch extension work. Candidate selection is
explicitly `proposed_not_measured`; no candidate is promoted until it is
compiled, correctness-checked on held-out inputs, and timed on the target
accelerator.

The current machine may only provide CPU measurements. That is still useful:
the database preserves the shape taxonomy and selector contract, then a CUDA or
ROCm host can replace the measured baselines with accelerator timings while
keeping the same schema.

## Run

```bash
python3 scripts/build_autotune_db.py
python3 scripts/verify_autotune_db.py
```
