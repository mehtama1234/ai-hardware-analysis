# Backend Hardware Placement Governor Input

This file is the hardware lab's local copy of the old backend's `hardware_placement` package artifact.

Source: `http://127.0.0.1:8025/deployment-packages/pkg-e931662a01293df2/hardware-placement`

## Summary

- operators: 5
- analog candidates: 2
- converter boundaries: 4
- fallback points: 3

## First-Principles Reading

The backend sees the model graph. The hardware lab sees physical limits. This artifact is the handoff between them. Each operator is translated into the fields that a hardware controller can understand: whether analog is even a candidate, where DAC and ADC boundaries appear, what error source is expected, how sensitive the model location is, and what fallback action the controller should take.

This does not prove that the hardware lab has consumed the rows in RTL yet. It proves the first connection: model graph facts can be reduced to hardware-control fields without losing the reason for the decision.

## Rows

| operator | kind | placement | analog candidate | sensitivity | residual q8 | sensitivity q8 | action |
| --- | --- | --- | ---: | --- | ---: | ---: | --- |
| dense1.matmul | MatMul | analog | 1 | projection-tolerant | 6 | 96 | analog_path |
| dense1.bias | Add | digital | 0 | digital-support | 0 | 128 | digital_fallback |
| dense1.relu | Relu | digital | 0 | digital-support | 0 | 128 | digital_fallback |
| dense2.matmul | MatMul | analog | 1 | projection-tolerant | 6 | 96 | analog_path |
| dense2.bias | Add | digital | 0 | digital-support | 0 | 128 | digital_fallback |
