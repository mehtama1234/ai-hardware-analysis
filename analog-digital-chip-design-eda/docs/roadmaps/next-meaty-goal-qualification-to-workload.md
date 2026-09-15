# Next meaty goal: qualified converter to real workload

The next end-to-end target is to take the current continuous Sky130 SAR
candidate through a bounded operating envelope, then use its measured error and
timing in one real transformer workload. The result should tell us whether the
analog path is useful, where it fails, and what a GPU or chip implementation
would actually need.

## Plain-language outcome

Given one frozen GPT-2-style layer and one held-out input set, produce the same
answer three ways:

1. the digital reference;
2. a simulator using an error/timing profile exported from the qualified SAR;
3. the compiler/runtime path that schedules the layer's analog and digital
   work.

The comparison must include accuracy, latency, energy assumptions, calibration,
fallbacks, and data movement. It must be possible to trace every model-level
number back to a circuit run and every circuit run back to a source revision.

## Why this is next

The remote evidence now proves the environment, one-bit polarity, reset-per-bit
operation, and nominal five-conversion continuous operation. SS and SF
continuous corners also pass. FF and FS currently measure but decode the wrong
codes, and the mismatch trial is a measured functional failure. Therefore the
next work is robustness and calibration, followed by workload propagation; a
new model or a larger UI would not close the current engineering gap.

## Work sequence

### 1. Freeze the qualification contract

Declare the supported supply, temperature, process corners, input range,
conversion count, code-error tolerance, legal internal-node range, timeout,
and calibration-data split in `qualification/matrix.json`. Keep held-out
conversion references separate from calibration fitting.

### 2. Make the continuous SAR robust

Use the persistent Colab wrapper for reproducible CPU/T4 runs. For each change,
record the complete map, sampled waveforms, timestep controls, and failure type.
Close the currently open FF and FS corners with a documented calibration or
revise the operating envelope. Run a statistically bounded mismatch campaign
with a fixed seed list and report measured, numerical-failure, and functional-
failure counts separately. Do not call synthetic variation silicon yield.

### 3. Bind physical behavior to the software model

Export a versioned profile containing transfer error, timing, clipping,
calibration cost, and uncertainty. Validate the profile against fresh circuit
cases that were not used to fit it. Keep the extracted-layout and schematic
identities explicit; neither can silently substitute for the other.

### 4. Run one real transformer slice

Select one frozen GPT-2 layer and held-out examples. Run the digital baseline,
the profile-driven analog simulator, and the existing compiler/runtime trace.
Measure task error, fallback rate, conversion count, bytes moved, estimated
latency, and energy at a clearly stated boundary. Use Colab for the GPU and
SPICE experiments; save command, environment, hashes, and raw artifacts.

### 5. Produce the decision package

Emit one report that says whether the analog path meets the declared error
budget and whether it has a credible cost advantage. If it does not, record the
failure mechanism and the smallest next design change. A negative result is a
successful outcome when the evidence is reproducible.

## Definition of done

This goal is complete when all of the following exist for the same candidate
and source revisions:

- a passing or explicitly bounded continuous-SAR qualification matrix;
- fixed-seed mismatch and PVT receipts with raw artifacts;
- a held-out circuit-derived error/timing profile;
- digital and profile-driven inference results for one real transformer slice;
- a compiler/runtime execution trace that matches the workload schedule; and
- a final accuracy/latency/energy/fallback decision with unsupported claims
  left open.

Until then, `analog_authorized` remains false.

## Current checkpoint — 2026-09-10

The local schematic calibration sweep found a shared FS/FF reference profile,
and the guarded workload trace now counts the corresponding GPT-2 schedule.
The explicit sequential switch-network control has now been measured in fresh
FS/FF T4 campaigns. Both corners complete five conversions but decode all 15;
direct probes show the held state decaying below the switch threshold. A fixed-
decision open-loop replay reaches FF but decodes `[0,13,11,9,8]` and violates
bottom-plate rail legality, while FS remains incomplete. The next hardware step
is therefore to repair bottom-plate drive/reset timing and acquisition
isolation; finite-edge PWL precharge, enlarged bidirectional rail clamps,
longer non-overlap, complementary switching, and top-plate reset did not
restore legality. Treat the physical bottom-plate switching model as the
primary defect, and require complete, legal FS/FF open-loop receipts before
revisiting closed-loop state capture. The
digital T4 path remains the authoritative fallback until those receipts exist.
