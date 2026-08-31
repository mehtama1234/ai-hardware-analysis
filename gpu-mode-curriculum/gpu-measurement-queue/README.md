# GPUMODE GPU Measurement Queue

This layer turns the GPU promotion runbook into per-step measurement contracts:
required host class, command list, expected evidence, metrics, and acceptance
thresholds.

Run:

```bash
python3 scripts/build_gpu_measurement_queue.py
python3 scripts/verify_gpu_measurement_queue.py
python3 scripts/verify_gpu_acceptance_logic.py
```

Artifacts:

- `gpu-measurement-queue/gpu-measurement-queue.json`
- `gpu-measurement-queue/reports/gpu-measurement-queue.md`
- `gpu-measurement-queue/acceptance-logic-report.json`
- `gpu-measurement-queue/reports/acceptance-logic-report.md`
- `site/gpu-measurement-queue.html`
- `site/gpu-acceptance-logic.html`
