# Backend Hardware Placement From First Principles

This page explains the `hardware_placement` artifact that connects the restored backend to the hardware lab.

The artifact answers one narrow question:

Which parts of this model graph are allowed to try analog in-memory compute, and what fields must the hardware lab see before that decision can be checked?

It does not answer whether the chip is fast, energy efficient, calibrated, or ready for production.

## Workflow Contract

Consumes: the restored backend's analyzed model graph and package context.

Produces: analog candidates, digital-only regions, DAC boundaries, ADC boundaries, expected error sources, model sensitivity classes, fallback points, and governor fields.

Supports: discussion of model-to-hardware placement for the current analyzed graph.

Refuses: final compiler lowering, silicon placement, measured latency, measured energy, analog macro layout, and tapeout signoff.

## Why Placement Is Not Just A Label

A model graph contains operations. A chip contains physical resources. Placement is the translation between those two objects.

For analog in-memory compute, this translation is dangerous if it stops at "MatMul goes analog." A matrix multiply can be a good analog candidate because it is a repeated weighted sum. But using analog changes the path:

```text
digital activation
  -> DAC code
  -> row voltage
  -> conductance-weighted current
  -> column sum
  -> ADC code
  -> corrected digital value
  -> next model operation
```

Every arrow adds a question. Does the DAC have enough levels? Does row voltage drop matter? Does conductance drift change the result? Does the ADC saturate? Does the next model operation tolerate the residual? Where does the digital path resume if the answer is unsafe?

That is why `hardware_placement` is not only a placement field. It is a small contract.

## Current Live Artifact

Source endpoint:

```text
http://127.0.0.1:8025/deployment-packages/pkg-e931662a01293df2/hardware-placement
```

Local imported copy:

```text
labs/analog/analog-in-memory-foundation-model-hardware/measurements/backend-hardware-placement.json
```

Human-readable imported copy:

```text
labs/analog/analog-in-memory-foundation-model-hardware/measurements/backend-hardware-placement-governor-input.md
```

Current summary:

```text
operators: 5
analog candidates: 2
digital only: 3
converter boundaries: 4
fallback points: 3
```

The analog candidates are the two `MatMul` operators. The digital-only regions are bias and activation support operations.

## What Each Row Means

Each row carries the fields the lab and governor need:

- `operator_id`: the model graph location.
- `operator_kind`: the operation type, such as `MatMul`, `Add`, or `Relu`.
- `placement`: the backend's current analog or digital decision.
- `analog_candidate`: whether analog is allowed to be considered.
- `dac_boundary`: whether a digital activation must become a row voltage before this operation.
- `adc_boundary`: whether a column current must become a digital code after this operation.
- `expected_error_source`: the physical or digital source of possible error.
- `model_sensitivity_class`: how dangerous error is at this model location.
- `fallback_point`: where the digital path can resume.
- `governor_fields`: compact numeric fields for RTL-facing decisions.

The important idea is simple: the row says what must be true before analog is allowed, not only where analog might be attractive.

## Why The MatMuls Are Analog Candidates

A dense matrix multiply is a stored-weight weighted sum:

```text
y_j = x_1 w_1j + x_2 w_2j + ... + x_n w_nj
```

An analog crossbar has the same physical shape:

```text
I_j = V_1 G_1j + V_2 G_2j + ... + V_n G_nj
```

The match is not exact. `x` must become voltage. `w` must become conductance. Current must become a code. But the operation shape is close enough that analog is worth trying when the model location can tolerate the residual.

That is why `dense1.matmul` and `dense2.matmul` are marked:

```text
placement: analog
sensitivity: projection-tolerant
residual_q8: 6
sensitivity_q8: 96
fallback_action: analog_path
```

The row does not say the result is trusted forever. It says the hardware lab may test this operator under the current residual and sensitivity budget.

## Why Bias And ReLU Stay Digital

Bias addition and ReLU are not large resident weighted sums. They are small support operations that are cheap and exact in digital logic.

Moving them into analog would add boundary cost without the same reuse benefit. It would also make the correction story harder because the result would need more checking after very little saved work.

That is why the current rows mark them:

```text
placement: digital
analog_candidate: false
fallback_action: digital_fallback
```

This is not anti-analog. It is the main hybrid design rule: use analog where the physical operation matches the model operation, and keep digital where the object is control, support arithmetic, comparison, addressing, or fallback.

## How The Lab Consumes It

The lab import command is:

```bash
python3 scripts/import_backend_hardware_placement.py
```

That writes:

- `backend-hardware-placement.json`
- `backend-hardware-placement-governor-input.csv`
- `backend-hardware-placement-governor-input.md`

Then the analog lab appends these backend-derived rows to the model-impact governor requests:

```bash
python3 labs/analog/analog-in-memory-foundation-model-hardware/python/model_impact_governor_requests.py
```

The current generated governor table has 10 rows:

- 5 local transformer-sensitivity rows
- 5 backend-derived placement rows

That matters because the hardware lab is no longer checking only a hand-written toy placement. It is checking rows that came from the restored backend package.

## How RTL Consumes It

The generated governor rows become Verilog test cases:

```text
residual_q8
sensitivity_q8
allow_analog
fallback_action
```

The RTL checker verifies that the controller refuses paths whose residual, sensitivity, calibration age, or accumulated state error make analog unsafe.

Current proof:

```text
PASS generated_model_impact_governor_trace
cases 10
```

This proves that the backend placement rows can enter the same hardware decision path as the local analog/model-sensitivity rows.

## What Still Has To Improve

The current artifact is a first bridge, not a full compiler.

Still missing:

- richer tensor shapes and tiling.
- explicit partial-sum boundaries.
- layer and tensor identifiers for full transformer blocks.
- attention/KV-cache placement from real model graphs.
- calibration profile selection per operator.
- cost model for DAC, ADC, memory movement, fallback, and batching.
- integrated scheduler/governor traces driven directly by backend placement rows.
- MLIR, TVM, IREE, or analog-MLIR lowering.

The next good build is not to rename this as a compiler. The next good build is to make the small placement artifact more precise until it can honestly become compiler input.

## Where This Page Fits

Previous page: `combined-aimc-workbench-end-to-end-goal.md`

Next pages:

- `cross-repo-aimc-loop-proof.md`
- `aimc-evidence-ledger.md`
- `mixed-signal-trust-boundary-spec.md`

Old backend source:

```text
ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend/hardware_placement.py
```

Old frontend review:

```text
http://127.0.0.1:8024/analog-in-memory-ai-inference/software-architecture/index.html
```
