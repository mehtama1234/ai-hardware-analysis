# GPU Evidence Gate

## Claim

A project should not claim real accelerator proof unless the measurement came from a real accelerator host and passed the metric contract.

## Read The Code

- `gpu-runs/gpu_runs/collector.py`
- `gpu-measurement-queue/gpu_measurement_queue/builder.py`
- `gpu-runs/imports/colab-advanced-phase.json`
- `capstone-acceptance/capstone-acceptance.json`

## Predict

Predict that Colab T4 accepts CUDA and Triton checks but fails ROCm, full profiler, and true multi-GPU checks.

## Run

```bash
python3 scripts/build_gpu_runs.py
python3 scripts/build_gpu_provenance.py
python3 scripts/build_gpu_measurement_queue.py
python3 scripts/verify_gpu_measurement_queue.py
```

## Change One Thing

Import a run from a different host class. Compare accepted, failed, and queued counts.

## Explain The Result

The proof is separation of evidence types. The report can accept 15 T4-backed claims while refusing the 3 claims that require other hardware.
