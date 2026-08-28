# Silicon To Board Proof Map

This file explains what has to happen before the roadmap can claim that the analog chip works on real hardware.

The short version:

```text
A chip feature becomes a product claim only after the board runs the same package, the lab measures the same run, calibration is tied to the same chip, and the task result still passes.
```

## Why This Exists

Analog chips are sensitive to physical conditions.

A software model can look accurate. A simulator can look promising. A compiler can produce a plan. None of those prove that the physical chip returned the right answer under real temperature, voltage, timing, power, and calibration conditions.

This map keeps the proof path explicit.

## End-To-End Hardware Proof Path

```text
1. Chip feature exists
   -> 2. Board exposes the feature
   -> 3. Runtime can command it
   -> 4. Calibration checks the chip
   -> 5. Board runs the package
   -> 6. Lab measures power and temperature
   -> 7. Task result is checked
   -> 8. Final claim is allowed or blocked
```

## 1. Chip Feature Exists

Plain meaning:

The silicon contains the hardware needed for the claim.

Examples:

- analog compute tiles
- ADC and DAC circuits
- temperature monitors
- voltage monitors
- reference cells
- tile health checks
- fallback paths
- write/update control
- debug counters

Evidence needed:

- chip specification
- register map
- design verification result
- lab bring-up notes after silicon exists

What this can support:

It can support the statement that the feature is intended or present in the design.

What this cannot support:

It cannot prove the feature works correctly on a board.

## 2. Board Exposes The Feature

Plain meaning:

The prototype board gives software and lab equipment a way to reach the chip.

Examples:

- USB for early control
- Ethernet for higher-level host communication
- PCIe for higher-bandwidth host communication
- JTAG for low-level debug
- UART for simple logs
- exposed power rails for measurement
- test points for voltage and timing
- connectors for sensors or host systems

Evidence needed:

- board id
- schematic or board interface summary
- power rail map
- debug link list
- firmware version
- test setup record

What this can support:

It can support the statement that the board can be controlled or measured.

What this cannot support:

It cannot prove that the model ran, used less power, or produced the right answer.

## 3. Runtime Can Command It

Plain meaning:

The software can send a package to the board, load weights, start the run, collect status, and record errors.

Examples:

- board package format
- firmware loader
- runtime command protocol
- register writes
- run start command
- run complete status
- failure reason
- debug trace

Evidence needed:

- runtime log
- package id
- board id
- chip id when available
- firmware version
- command trace
- failure trace if the run fails

What this can support:

It can support a board runtime claim for the exact setup tested.

What this cannot support:

It cannot prove power, heat, or task accuracy unless those are measured for the same run.

## 4. Calibration Checks The Chip

Plain meaning:

Calibration checks how the real chip behaves and gives the runtime correction values.

Examples:

- temperature monitor readings
- voltage monitor readings
- reference-cell readings
- weak-tile list
- correction values
- drift profile
- recalibration command
- failed-calibration behavior
- fallback rule

Evidence needed:

- calibration profile id
- board id
- chip id
- timestamp
- measured monitor readings
- weak-tile list
- correction table
- pass/fail status
- fallback record

What this can support:

It can support trust in a run when the calibration profile is measured and tied to the same chip and condition.

What this cannot support:

It cannot prove long-term reliability unless calibration is repeated across time, temperature, voltage, and workload conditions.

## 5. Board Runs The Package

Plain meaning:

The board actually executes the package generated for the workload.

Evidence needed:

- `board_runtime.json`
- package id
- workload id
- board id
- firmware version
- load status
- start status
- finish status
- latency
- jitter
- failure reason if any
- debug trace location

What this can support:

It can support the statement that this package ran or failed on this board.

What this cannot support:

It cannot prove energy, temperature, model accuracy, or update safety.

## 6. Lab Measures Power And Temperature

Plain meaning:

The lab measures how much energy the system used and how hot it became during the same run.

Evidence needed:

- `power_thermal.json`
- package id
- board id
- firmware version
- power rail map
- energy per run
- peak power
- sampling rate
- equipment used
- temperature trace
- measurement start and stop times

What this can support:

It can support measured power and thermal claims for the exact setup.

What this cannot support:

It cannot prove task accuracy. A low-power wrong answer is still a failed product result.

## 7. Task Result Is Checked

Plain meaning:

The mapped or hardware-run model is tested against the task that matters to the user.

Evidence needed:

- `task_accuracy.json`
- dataset or scenario id
- metric
- baseline result
- candidate result
- hardware result when available
- tolerance
- sample count
- failure slices

What this can support:

It can support a task-level claim for the tested workload and setup.

What this cannot support:

It cannot prove all workloads, all environments, all temperatures, all boards, or all future software versions.

## 8. Final Claim Is Allowed Or Blocked

Plain meaning:

The platform combines the evidence and decides what can be said.

Safe example:

```text
This workload ran on board X with firmware Y, using calibration profile Z. Under this setup, measured latency was A, measured energy was B, peak temperature was C, and task accuracy stayed within D tolerance.
```

Blocked example:

```text
The analog chip is ready for all Physical AI workloads.
```

Evidence needed:

- final answer artifact
- all source artifacts listed in the claim
- matching package id
- matching workload id
- matching chip or board id
- proof level for each claim

## Minimum Hardware Evidence Set

Before any strong board claim, the package should contain:

- board runtime trace
- firmware metadata
- calibration profile or explicit missing-calibration status
- power rail map
- power trace
- temperature trace
- task accuracy result
- failure and fallback record
- package id shared across all artifacts

## Product Meaning

This map prevents a common mistake:

```text
The board responded, so the chip is proven.
```

The correct reading is:

```text
The board response proves only that the board responded. A product claim needs synchronized runtime, calibration, power, temperature, task, and failure evidence for the same run.
```
