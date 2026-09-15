# Model to GPU to Chip: End-to-End Meaty Goal

## The goal

Build one evidence-backed path that starts with a real transformer workload and
ends with a physically qualified hardware execution path. We will use the
DeepSeek-from-scratch implementation and the existing GPU curriculum to make a
small, measurable model workload; then map the same operations through a GPU
kernel path, a digital fallback, and an analog in-memory/converter candidate.

The final result must let a reviewer answer, from saved artifacts:

> Which model operation ran, on which representation, on which device, with
> what latency, energy, accuracy, and failure behavior?

This is a research and verification system, not a claim that analog hardware is
automatically faster or cheaper. Native digital GPU execution remains the
authoritative baseline until every analog gate closes.

## Repositories and their jobs

| Repository | Job in the end-to-end path |
| --- | --- |
| `DeepSeek-From-Scratch` | Small language-model implementation, training/inference mechanics, and model-level correctness reference. |
| `gpu-mode-curriculum` | Colab GPU notebooks, kernel experiments, profiling, and reproducible T4 handoff receipts. |
| `analog-in-memory-ai-inference` | Workload partition, hybrid software architecture, accuracy contract, and model-to-array mapping. |
| `analog-digital-chip-design-eda` | Sky130 circuit generation, SPICE experiments, EDA checks, qualification matrix, and evidence dashboard. |
| `analog-in-memory-ai-inference/analog-in-memory-ai-inference` and related analysis folders | Analog compute assumptions, memory-array behavior, and hardware cost/energy models. |

The repositories remain independently runnable. This goal connects them through
versioned manifests and evidence files rather than hidden copied state.

## The vertical slice

Start with one projection or MLP block and a small fixed evaluation set. The
slice must run in four modes:

1. reference PyTorch or NumPy execution;
2. optimized GPU execution on a Colab T4;
3. native digital fallback with identical tensor and numerical contracts; and
4. hybrid analog candidate with explicit ADC/DAC, transfer, accumulation, and
   fallback costs.

Every mode receives the same inputs, seeds, tokenizer/model revision, precision,
sequence lengths, and acceptance tolerances. The output report compares task
outputs, layer error, latency, energy, memory movement, and unsupported claims.

## Work stages

### 1. Freeze the model contract

Select the smallest useful DeepSeek-derived workload. Record model revision,
tokenizer, weights or initialization seed, tensor shapes, precision, batch and
sequence lengths, and the exact reference outputs. Add a deterministic test
that fails if a backend silently changes shapes, rounding, or operation order.

### 2. Establish the Colab GPU baseline

Run the workload on a T4 using the existing GPU curriculum patterns. Capture
kernel source, launch configuration, device properties, warm-up policy,
latency distribution, peak memory, power/energy method, and output hashes.
The baseline must be rerunnable from a notebook or script without relying on a
live interactive cell.

### 3. Build the digital fallback

Implement the same workload with a clear digital path and explicit transfer,
packing, accumulation, and fallback boundaries. Verify numerical agreement with
the reference and measure end-to-end latency and energy. This is the safety path
for any unsupported analog operation.

### 4. Map the workload to the hybrid candidate

Define which matrix operations are placed in the array, which reductions happen
digitally, ADC/DAC precision, calibration, tiling, data movement, and fallback
conditions. The simulator must expose these costs instead of treating an array
multiply as free.

### 5. Qualify the converter and array primitives

For each candidate primitive, run nominal, process-corner, supply/common-mode,
noise, mismatch, settling, code-map, and legality checks. The Sky130 physical
SAR must reproduce the required conversion map across the complete requested
history before it can enter the workload path.

### 6. Close the controller-to-circuit handoff

Verify reset, acquisition, comparator capture, retained state, trial enable,
break-before-make ownership, DAC gate levels, and conversion boundaries with
named waveform probes. A transient that completes is insufficient; the measured
state and code sequence must be correct.

### 7. Run matched end-to-end comparisons

Use identical workload inputs and report accuracy, latency, energy, memory
traffic, area assumptions, and fallback fraction for GPU, digital, and hybrid
modes. Include uncertainty and failed experiments. A model-level match cannot
promote an unqualified circuit claim.

### 8. Package a reviewable demonstration

Publish a small dashboard linking model operation → backend → circuit run →
waveform/measurement → claim decision. A reviewer must be able to reproduce the
numbers on Colab and inspect the exact source revision and artifact hashes.

## Hard gates

The project may advance only when the relevant evidence exists:

- **Model gate:** deterministic reference outputs and shape/precision contract.
- **GPU gate:** repeatable Colab T4 run with latency and resource receipt.
- **Digital gate:** matched fallback output and complete cost accounting.
- **Circuit gate:** exact conversion map, legal node ranges, stable transient,
  and explicit reset/capture/retention evidence.
- **Robustness gate:** PVT or model-availability record, noise, mismatch, and
  repeated-history behavior.
- **Workload gate:** end-to-end accuracy, latency, energy, transfer, and
  fallback measurements with the same workload contract.
- **Claim gate:** every headline claim points to evidence of the right kind;
  unsupported analog speedup or energy claims remain rejected.

## Definition of done

The goal is complete only when a clean checkout can run the selected model slice
in all four modes, produce linked artifacts, and show that the hybrid path
meets its declared accuracy and cost thresholds under the accepted circuit and
robustness gates. If a gate fails, the system must preserve the failure and
route execution to the digital/GPU fallback. The current state has not reached
this definition yet.

## Immediate milestone

The model and GPU portions have crossed their current gates: the frozen
MiniDeepSeek workload has measured Tesla T4 receipts, a consolidated CUDA
provenance record, and a passing integration validator. The active hardware
milestone is now the Sky130 two-control SAR handoff. The corrected local
transient shows near-rail retained state in the first two conversions
(`evidence/aimc-simulator-adapters/local-retention-fix.json`), while later DAC
nodes still leave the legal range and decode incorrectly. Raw comparator
decisions are valid, but this repair still needs a matching Colab receipt and
an exact legal conversion map. Until the converter map is exact and robust,
continue optimizing and measuring the GPU/digital path rather than claiming
analog benefit.
