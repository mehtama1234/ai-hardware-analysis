# Hybrid Transformer Vertical Slice Review

## Executive Result

The first hybrid execution package has been generated for
`deep-transformer-mlp-stack.onnx`. It explicitly maps fixed-weight matrix
multiplications to analog memory, keeps nonlinear and residual operations on a
digital support path, and uses SRAM for activations, partial sums, calibration
values, and fallback buffers.

The calibrated CrossSim replay passes the named numerical fixture with a
relative output difference of approximately `6.7e-8`. The nominal differential
Sky130 DAC now passes its 16-code transfer gate with `83.5273 mV` minimum
spacing and `1.7651 V` span. The physical converter remains blocked at the SAR
source-interface gate: the isolated calibrated run passes its named
representative cases, but the newer continuous five-conversion run returns
`3/5` correctly (`0→0`, `2→0`, `4→3`, `6→6`, `7→7`) and has out-of-range
bottom-plate nodes.

This is a simulator-backed architecture result. It is not a board, silicon, or
production result.

## Requirements And Specification

The vertical slice must:

1. Start from one versioned transformer-style model fixture.
2. Name the workload, baseline, metric, and acceptance threshold.
3. Assign every operator to analog memory, digital support, or SRAM-backed
   movement.
4. Give each analog operator a tile shape, tile count, precision rule,
   converter boundary, calibration profile, residual budget, and fallback.
5. Give each digital operator a reason for staying digital.
6. Record logical-to-physical bit slicing and recombination assumptions.
7. Compare the hybrid output with the digital baseline on held-out input.
8. Preserve the physical converter limitation as a blocked gate.
9. Keep simulator evidence separate from measured hardware evidence.

The target fixture has three repeated transformer-style MLP blocks and twelve
fixed-weight MatMul candidates. Bias, ReLU, elementwise gating, residual adds,
control, calibration, and fallback stay digital. SRAM is the shared temporary
storage boundary.

## What Was Built

The generator is:

```text
scripts/generate_hybrid_transformer_execution_package.py
```

It consumes the existing source-matched calibrated simulator summary and
CrossSim payload, then writes:

```text
evidence/aimc-hybrid-transformer-vertical-slice/workload_contract.json
evidence/aimc-hybrid-transformer-vertical-slice/hybrid_execution_plan.json
evidence/aimc-hybrid-transformer-vertical-slice/bit_slicing_plan.json
evidence/aimc-hybrid-transformer-vertical-slice/analog_error_replay.json
evidence/aimc-hybrid-transformer-vertical-slice/hybrid_output_comparison.json
evidence/aimc-hybrid-transformer-vertical-slice/hybrid_execution_plan.md
```

The execution plan contains `16` placement rows: `12` analog-memory MatMuls
and `4` digital-support operations. The analog rows use `16 x 16` tiles and
calculate tile count from each matrix shape. The precision plan records
8 logical weight bits, 1-bit physical cells, 8 read slices, 8-bit per-slice
ADC assumptions, and a 24-bit partial-sum width.

The replay handoff is:

```text
scripts/run_hybrid_transformer_vertical_slice.py
```

It consumes the plan and source replay, verifies that all 12 analog operator
IDs match, and writes `execution_schedule.json` and
`hybrid_runtime_trace.json`. The trace contains 76 ordered operator-level
events for SRAM loading, DAC encoding, analog tile execution, ADC decoding,
calibration, partial-sum storage, and digital support.

## Source Evidence

The model-level evidence comes from:

- `evidence/aimc-simulator-adapters/crosssim-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json`

That replay uses seven calibration inputs and one held-out input with a
per-output affine correction. The accepted CrossSim payload reports a held-out
relative L2 output difference of approximately `6.716e-8`. The companion
AIHWKIT payload is retained as evidence, but its residual exceeds the positive
claim threshold and is not accepted as positive evidence.

The physical converter evidence comes from:

- `evidence/aimc-simulator-adapters/sky130-calibrated-physical-sar.json`
- `evidence/aimc-simulator-adapters/sky130-bottom-plate-topology-sweep.json`
- `evidence/aimc-simulator-adapters/sky130-full-array-cap-scale-diagnostic.json`

That run completes `16/16` calibration codes, `20/20` retained-bit
comparisons, and `5/5` representative conversions using a PMOS-only topology
and a `9.0 ns` pre-sample measurement. It still fails the high-code spacing
requirement, so it cannot validate the simulator's 8-bit converter assumption.
An exploratory `8x` full-array capacitor scaling run restores monotonic
upper-code spacing and reaches `96.855 mV` for code `14 -> 15`, but drives the
DAC top plate to `2.544 V` on a `1.8 V` supply. That result is retained as
charge-transfer mechanism evidence and rejected as an implementation.
The follow-up zero-common-mode all-code run measured `16/16` cases with
correct polarity, but was rejected for non-monotonic transfer and supply-range
violations. The focused high-code spacing result cannot be used as converter
acceptance.
The subsequent MSB timing diagnostic also rejects longer redistribution as a
repair: code `7 -> 8` remains non-monotonic at `-94.577 mV` with a 20 ns
interval. The physical converter remains a blocked dependency of the hybrid
execution package.
MSB capacitor-ratio and redistribution-time diagnostics both reject simple
cell sizing and timing repairs, so the physical converter remains a blocked
dependency rather than an analog placement permission.
The targeted selected-MSB switch-scale diagnostic also fails (`-224.255 mV`
for code `7 -> 8` at 4x, with a timeout at 2x), reinforcing that the physical
converter requires a topology change rather than device sizing.

## How It Was Tested

The package was generated with:

```bash
python3 scripts/generate_hybrid_transformer_execution_package.py
```

The generator checks that the source evidence exists and preserves its
provenance in the new artifacts. The resulting JSON files were parsed with:

```bash
python3 -m json.tool evidence/aimc-hybrid-transformer-vertical-slice/hybrid_execution_plan.json
python3 -m json.tool evidence/aimc-hybrid-transformer-vertical-slice/bit_slicing_plan.json
python3 scripts/run_hybrid_transformer_vertical_slice.py
python3 scripts/build_hybrid_compiler_runtime_package.py
python3 scripts/compile_hybrid_transformer_execution_package.py
python3 scripts/run_hybrid_runtime_estimator.py
```

The package structure was then checked programmatically:

```text
placements: 16
analog placements: 12
digital placements: 4
simulator relative L2: 6.71634969e-08
simulator pass: True
replay events: 76
shared compiler/runtime package: 4 models/workloads, 38 operators, 138 events
target lowering: 138 commands, 160 register writes, 294 planning cycles
runtime schedule: verified, 20 analog tile, 40 converter, 40 SRAM actions
physical converter gate: blocked_sar_source_common_mode
```

The complete project validator also passed:

```bash
python3 scripts/validate_project.py
```

The site was rebuilt successfully with:

```bash
python3 scripts/build_site.py
```

## Results By Gate

| Gate | Result | Meaning |
| --- | --- | --- |
| Workload contract | pass | One named fixture, baseline, metric, and threshold are recorded. |
| Analog/digital placement | pass | All 16 planned rows have an explicit placement and rationale. |
| SRAM boundary | pass | Activation, partial-sum, calibration, and fallback storage are named. |
| Bit slicing | pass as a mapping rule | Logical and physical precision assumptions are recorded. |
| Calibrated simulator replay | pass for fixture | CrossSim held-out output residual is below the simulator threshold. |
| Physical converter compatibility | blocked | The real PMOS-only converter has insufficient high-code spacing. |
| Transformer task accuracy | not yet tested | This fixture has numerical output comparison, not a real task dataset or token metric. |
| Board runtime and power | not tested | No synchronized board or meter trace exists. |

The capacitor-scale diagnostic is also a blocked physical gate: spacing passes
in the exploratory run, but the supply-range constraint fails.

## Safe Claim

The project can say:

> A three-block transformer-style MLP fixture has an explicit hybrid placement
> plan and a calibrated CrossSim replay in which the twelve fixed-weight MatMul
> candidates preserve the held-out numerical output under the stated simulator
> assumptions.

The attention-shaped fixture now has a companion plan at
`evidence/aimc-hybrid-transformer-attention-slice/`. Its four static Q/K/V/output
projection MatMuls are analog candidates, while dynamic score selection,
scaling, Softmax, and value selection remain digital with SRAM buffers. Its
calibrated CrossSim replay reports approximately `4.177e-8` relative L2 output
difference. This is still a projection replay, not full transformer token
accuracy.

The transformer plans and wake-word plan now feed the shared compiler/runtime
handoff generated by `scripts/build_hybrid_compiler_runtime_package.py`. The
package contains four model/workload plans, 38 operator rows, and 138 ordered
operator-level schedule events. The wake-word package retains two dense
MatMuls as analog candidates but selects digital execution because converter
overhead is not amortized at its small workload size.

The single-block transformer package adds four more fixed-weight MatMul analog
candidates and four digital support operations. Its calibrated CrossSim replay
reports relative L2 difference `4.944978e-8` and passes the simulator threshold.
It is a deterministic review handoff; compiled binary, register file, cycle
trace, and board runtime are still not generated.

The target-lowering step is generated by
`scripts/compile_hybrid_transformer_execution_package.py`. It produces
`runtime_commands.json`, `register_writes.json`, and
`target_execution_trace.json`: for the original four-workload slice it produced
138 commands, 160 register writes, and a 294-cycle planning schedule. The newer
shared twelve-workload compiler extends this to 321 commands, 460 register
writes, 687 planning cycles, 321 review bytecode words, and complete SRAM maps.
These are deterministic target artifacts with symbolic SRAM addresses and
planning cycle counts, not ISA-validated firmware or an observed board trace.

The schedule verifier and runtime estimator is
`scripts/run_hybrid_runtime_estimator.py`. It confirms no command overlaps or
sequence gaps and writes `hybrid_runtime_estimate.json` and
`hybrid_runtime_estimate.md`. The verified estimate contains 16 analog tile
executions, 40 converter actions, 40 SRAM actions, and 294 serialized planning
cycles across the four packages. Energy and measured latency remain
intentionally unreported.

The audio package is generated by
`scripts/generate_audio_hybrid_execution_package.py`. Its 24-sample generated
audio task rehearsal reports wake-word F1 `1.0` for both digital and analog
candidate paths, but its cost record reports normalized latency `41` versus
`28` and energy `154.2` versus `152.0`; the compiler therefore selects the
digital path and preserves analog as a candidate/fallback option.

## Claims Still Blocked

This package does not prove:

- pretrained foundation-model accuracy;
- full transformer attention execution;
- KV-cache, Softmax, LayerNorm, or token-decision behavior;
- physical 8-bit converter operation;
- calibrated silicon behavior;
- board latency, energy, or thermal performance;
- weight-update reliability;
- analog macro layout or tapeout readiness;
- production or customer readiness.

## Next Engineering Gate

First redesign the charge-transfer network so high-code spacing and legal node
range pass together, then rerun the same threshold-spacing and SAR tests. Then
connect a converter profile that matches
the physical result to this execution plan. After that, add the attention-shaped
fixture while keeping dynamic attention selection, Softmax, normalization,
KV-cache movement, and token decisions on the digital/SRAM path until those
operations have their own evidence.
