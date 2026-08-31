# GPU Host Promotion

This layer turns local CPU/source-ready evidence into an ordered GPU-host
runbook. It lists each accelerator promotion step, required capabilities,
commands, expected evidence, and validation criteria.

The local machine can verify the runbook structure even when CUDA, ROCm, Nsight,
or multi-GPU hardware is unavailable. A GPU host should run the ready-on-GPU-host
steps, refresh reports, and then run the full `python3 run_all.py` gate.

## Run

```bash
python3 scripts/build_gpu_promotion.py
python3 scripts/verify_gpu_promotion.py
```
