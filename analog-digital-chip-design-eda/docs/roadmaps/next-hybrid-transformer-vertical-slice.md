# Next Hybrid Transformer Vertical Slice

## Goal

Take `deep-transformer-mlp-stack.onnx` from model file to one reproducible
hybrid execution package. The package must show which work uses analog memory,
which work uses digital logic, which values live in SRAM, how converter and
calibration costs are paid, and whether the analog error changes the model
output on the named fixture.

This is a model-and-hardware simulation milestone, not a silicon or product
claim.

## Fixed Scope

- Model: `deep-transformer-mlp-stack.onnx`
- Model shape: three repeated transformer-style MLP blocks, 12 fixed-weight
  matrix multiplications
- Analog candidates: the fixed-weight matrix multiplications
- Digital path: bias, ReLU, elementwise multiply, residual addition, control,
  calibration, fallback, and all unsupported operations
- SRAM: activations between operators, partial sums, calibration values, and
  digital fallback buffers
- Physical evidence: corrected PMOS-only Sky130 converter calibration
- Current converter boundary: DAC threshold sampled at `9.0 ns` before
  comparator closure

The fixture is intentionally smaller than a pretrained transformer. It lets us
prove the complete path before adding token attention, KV-cache traffic, or
VLA action logic.

## Required Flow

```text
ONNX model
  -> operator inventory
  -> analog/digital/SRAM placement
  -> tile and bit-slice plan
  -> converter and calibration schedule
  -> analog-error replay
  -> digital recombination and fallback
  -> output comparison against the digital baseline
  -> execution package and claim report
```

## Required Artifacts

1. `workload_contract.json`: model, fixture version, task proxy, baseline,
   tolerance, and hardware profile identifiers.
2. `hybrid_execution_plan.json`: one row per operator with placement, tile,
   memory location, converter crossings, calibration profile, and fallback.
3. `bit_slicing_plan.json`: logical precision, physical slices, read order,
   recombination width, and overflow margin.
4. `analog_error_replay.json`: per-matmul residuals, calibration cases,
   held-out input, converter assumptions, and simulator provenance.
5. `hybrid_output_comparison.json`: digital baseline output, hybrid output,
   residual metric, tolerance, and pass/fail.
6. `hybrid_execution_plan.md`: a plain-language report that links every
   positive result to its source evidence and lists blocked claims.

## Acceptance Gates

The vertical slice is complete only when all of these are true:

- every model operator has exactly one placement;
- every analog operator has a named tile, bit-slice rule, DAC/ADC boundary,
  calibration profile, and fallback rule;
- every digital operator has a reason for remaining digital;
- SRAM traffic is counted between analog and digital boundaries;
- the same plan is consumed by the simulator report and execution schedule;
- the calibrated replay completes for all 12 matrix multiplications;
- the hybrid output is compared with the digital baseline on held-out input;
- failure remains visible when the physical converter range is insufficient;
- no result is labeled measured silicon, board runtime, measured power, or
  production readiness.

## Current Evidence

The calibrated CrossSim replay already covers the 12 fixed-weight matrix
multiplications and reports a held-out relative output residual of approximately
`6.7e-8` for this software fixture. That result is useful simulator evidence,
but it does not validate the physical converter. The Sky130 PMOS-only SAR
calibration separately completes `16/16` calibration codes, `20/20` retained
comparisons, and `5/5` representative conversions; its code `14 -> 15`
spacing is only `16.361 mV` versus the `56.25 mV` 4-bit half-LSB target.

Therefore the first implementation gate is allowed to pass the software
replay, but the physical converter gate must remain blocked until the high-code
topology is repaired or the supported operating range is explicitly reduced.

The latest converter diagnostic corrected the differential fixture to a
break-before-make sequence and then added `4x` top-plate dummy capacitance.
The complete nominal DAC transfer now measures `16/16` codes with `83.5273 mV`
minimum spacing, `1.7651 V` span, legal plate range, and correct nonzero
polarity. The coupled calibrated SAR now measures `16/16` calibration codes and
`20/20` conversion comparisons at the stable `0.8x` level-shift setting, but
only `2/5` representative conversions are correct. A `0.9x` setting reduces
low-end convergence and returns `1/5`. The hybrid execution package must
continue to record analog candidates as physically gated with digital fallback
until the source common-mode/input-range contract and SAR loop are closed.

## Current Follow-On

The attention-shaped companion package is now generated under
`evidence/aimc-hybrid-transformer-attention-slice/`. It keeps static
Q/K/V/output projections as analog candidates only where the error budget
allows them and keeps dynamic score selection, scaling, Softmax, and value
selection digital with SRAM buffers. Its CrossSim replay reports approximately
`4.177e-8` relative L2 output difference.

Both packages now share an operator-level compiler/runtime handoff at
`evidence/aimc-hybrid-compiler-runtime/`, with 24 operators and 104 schedule
events. The next engineering step is to replace that review handoff with a
target-specific compiler output and measure the cost of the digital attention
boundary. Keep normalization, KV-cache movement, and token decisions digital
until those costs have their own evidence.

Only after both fixtures share the same compiler plan and evidence schema should
we attempt a larger transformer or VLA workload.
