# ONNX Fixture Inventory

This page is the review page for the local ONNX model-slice inventory.

The generated source report is:

- `evidence/aimc-hardware-lab/onnx-fixture-inventory.json`
- `evidence/aimc-hardware-lab/onnx-fixture-inventory.md`

## Object

The object is the set of ONNX fixtures in the restored backend.

The question is simple: before we ask for a new uploaded model, what local model-shaped slices already exist, and which one is strongest for analog in-memory compute evidence?

## Boundary

A useful analog slice is not just a larger file.

It needs fixed-weight MatMul rows, initializer tensors, and surrounding digital operations. Fixed weights can be stored as conductance. The digital support operations show whether the analog work survives inside a graph instead of only inside a single matrix multiply.

## Refused Claim

This page does not claim that a fixture is a pretrained foundation model. It does not prove measured latency, measured energy, calibrated silicon, analog macro layout, production readiness, or tapeout readiness.

## Next Handoff

Use the selected local fixture as the current best available model-shaped slice. The next stronger step is to replace it with a real uploaded or imported model slice and run the same guarded simulator path.
