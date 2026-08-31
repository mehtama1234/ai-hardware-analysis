# GPUMODE Multi-Tenant GPU Scheduling

Generated: `2026-08-31T01:53:26.814667+00:00`
Status: `scheduling-ready`
Recommended policy: `cluster-queue`

## Policy Results

| policy | accepted | queued | fairness | utilization | score |
|---|---:|---:|---:|---:|---:|
| exclusive | 1 | 4 | 1.0 | 0.55 | 16.5 |
| mig-pack | 2 | 3 | 0.930769 | 0.55 | 51.461538 |
| mps-fair-share | 2 | 3 | 0.98 | 0.35 | 39.2 |
| cluster-queue | 4 | 1 | 0.801282 | 0.454545 | 117.564685 |

## Recommended Placements

| tenant | partition | status | isolation | SLO | reason |
|---|---|---|---|---|---|
| tenant-c-long-context-rag | node-a-gpu0-full | accepted | exclusive | pass | fits partition with required isolation and capacity |
| tenant-a-interactive-7b | node-b-gpu0-mig-4g-40gb | accepted | hardware-slice | pass | fits partition with required isolation and capacity |
| tenant-e-70b-training-smoke | queue | queued | none | queued | no partition satisfies memory, SM, and isolation constraints |
| tenant-b-batch-embedding | node-b-gpu0-mig-2g-20gb | accepted | hardware-slice | pass | fits partition with required isolation and capacity |
| tenant-d-kernel-ci | node-c-gpu0-mps-pool | accepted | process-share | pass | fits partition with required isolation and capacity |

## GPU Host Promotion

- `kubectl get nodes -o json`
- `kubectl describe node <gpu-node>`
- `nvidia-smi -L`
- `nvidia-smi mig -lgip`
- `nvidia-cuda-mps-control -d`
- `kubectl apply -f <gpu-workload.yaml>`
- `kubectl top pods -A --containers`
- `python3 scripts/run_gpu_promotion_suite.py --run-id multi-tenant-scheduling --execute`
