# Tiny MLP Task Hybrid Execution Plan

This package puts the existing tiny MLP task and governor rehearsal into the shared compiler/runtime schema.

- operators: `6`
- analog candidates retained: `1`
- selected execution: `digital fallback`
- task result: `classification_accuracy=0.9375` versus baseline `1.0`
- physical converter gate: `blocked_sar_source_common_mode`

The task rehearsal passes its provisional accuracy tolerance, but it uses synthetic data and does not justify a physical analog claim. The dense1 MatMul remains an analog candidate in the compiler record; the guarded runtime must use digital execution until the converter and source interface pass.
