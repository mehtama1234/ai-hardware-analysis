# GPU Evidence And Acceptance

## First Question

A local CPU result, a generated source file, and a real GPU measurement are different kinds of evidence. This lane asks whether the repo can keep those claims separate.

## What The Code Does

- `gpu-runs/gpu_runs/collector.py writes host evidence from local or Colab runs.`
- `gpu-measurement-queue/gpu_measurement_queue/builder.py checks each step against its required metrics.`
- `capstone-acceptance/capstone_acceptance/evaluator.py turns the evidence state into a score.`

## What The Measurement Proves

The Colab T4 import proves the system can ingest a real GPU run and mark 18 of 18 tasks measured. It accepts 15 tasks and keeps 3 failed because the required hardware or tools were absent.

## What It Does Not Prove

It does not hide missing Nsight, ROCm, or multi-GPU evidence. The failed rows are the point: they stop the report from claiming more than the hardware proved.

## Read Next

- `site/gpu-runs.html`
- `site/gpu-measurement-queue.html`
- `site/capstone-acceptance.html`
