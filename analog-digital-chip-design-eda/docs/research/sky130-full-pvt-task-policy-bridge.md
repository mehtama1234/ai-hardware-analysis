# Sky130 Full PVT And Task Policy Bridge

This page is the model-to-circuit policy handoff. It combines the accepted calibrated deep transformer MLP simulator result with the independent transistor PVT eligibility matrix.

Both conditions are required:

1. The mapped fixed-weight MLP projections must remain inside the accepted CrossSim surrogate error gate.
2. The physical preamp must converge, preserve polarity, and exceed the `0.5 mV` handoff margin.

If either condition fails, the operation uses the digital reference path and records a reason.

## Reproduce

```bash
python3 scripts/run_full_pvt_task_policy_bridge.py
```

The output is `evidence/aimc-simulator-adapters/sky130-full-pvt-task-policy-bridge.json`.

## Boundary

The CrossSim task result is a calibrated simulator surrogate, not language-model accuracy. The PVT matrix is deterministic schematic evidence, not mismatch/noise yield. This bridge therefore proves the shape of the fallback policy, not end-to-end silicon behavior.
