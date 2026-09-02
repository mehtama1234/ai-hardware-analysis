# Action And Evidence Map

This file explains what each future button or import action should do.

Start from the main workbench [Connected System Map](../connected-system-map.html). This map uses the same object, constraint, evidence, allowed-claim, refused-claim, and next-handoff contract for every future run or import action.

The goal is simple:

```text
When a user clicks run or import, the platform should produce one clear artifact, update the proof level, and keep unsupported claims blocked.
```

## Rule

A button is not proof.

An action becomes proof only when it creates or imports a validated artifact tied to the same package, workload, chip target, software version, board setup, and measurement setup.

## Connected-System Contract

Each action should follow this shape:

```text
object -> constraint -> design move -> evidence -> allowed claim -> refused claim -> next handoff
```

The ordinary import path can attach useful local, simulated, RTL, synthesis, or OpenLane evidence. The measured import path is stricter. It should reject a local runtime trace or OpenLane-derived power estimate when the user is trying to upgrade measured latency or measured energy claims.

## Run Actions

| Action | What It Does | Output Artifact | Proof Level | Claim It Can Support | Claim It Cannot Support |
| --- | --- | --- | --- | --- | --- |
| Run Model Intake | Reads the model and records inputs, outputs, layers, operators, shapes, and unsupported parts. | `model_intake.json` | local estimate or parsed result | The platform knows what model was reviewed. | It does not prove analog fit, speed, power, or accuracy. |
| Run Analog Fit | Classifies model regions as analog candidate, digital required, fallback required, or blocked. | `analog_fit.json` | local estimate | Some model parts appear suitable for analog review. | It does not prove the chip can run them. |
| Run Analog Accuracy Simulation | Tests how analog-like noise, drift, limited precision, and imperfect writes may affect the model. | `analog_accuracy_risk.json` | simulator output when backed by a simulator | Analog behavior may or may not hurt accuracy under stated assumptions. | It does not prove board speed, board power, or final silicon behavior. |
| Run Crossbar Layout Check | Tests whether the physical memory grid may create errors from wire effects, bit-slicing, converter range, read noise, or programming error. | `crossbar_layout_risk.json` | simulator output or local estimate | A proposed array layout may be risky or acceptable under stated assumptions. | It does not prove packaged silicon behavior. |
| Run Hardware Cost Estimate | Estimates area, memory, energy, latency, converter cost, and data movement cost. | `hardware_cost_estimate.json` | local estimate | Early tradeoff planning. | It does not prove measured cost, measured power, or yield. |
| Run Compiler Mapping | Produces an analog/digital task plan, tile placement, bit-slicing plan, unsupported operator list, runtime package status, and failure reasons. | `compiler_mapping.json` | compiler mapping | The compiler can or cannot map the workload under the target rules. | It does not prove the board loaded or ran the package. |
| Run Transformer And VLA Check | Separates static matrix-heavy parts from attention, Softmax, LayerNorm, action heads, sensor frontends, and safety/control work. | `transformer_vla_check.json` | local estimate or compiler mapping | The platform knows which modern model parts need analog, digital, fallback, or rewrite paths. | It does not prove full VLA deployment. |
| Run Full-System Runtime Estimate | Counts host dispatch, memory movement, synchronization, ADC timing, DAC timing, tile parallelism, and digital accumulation. | `full_system_runtime.json` | system simulation or local estimate | System overhead may be a bottleneck. | It does not prove measured board latency or energy. |
| Generate Final Answer | Combines the artifacts into fit, proof, broken parts, safe claims, blocked claims, and next work. | `final_answer.json` | derived package result | The package has a readable claim boundary. | It cannot make a claim stronger than its input artifacts. |

## Import Actions

| Action | What It Imports | Output Artifact | Proof Level | Claim It Can Support | Claim It Cannot Support |
| --- | --- | --- | --- | --- | --- |
| Import Board Trace | Board load status, runtime version, run status, repeated latency values, synchronized start/end timestamps, host-overhead boundary, fallback events, failure reason, and debug trace. | `board_runtime.json` | board runtime only when tied to a real board id and revision | The exact package ran or failed on the exact board setup. | It does not prove power, heat, task accuracy, or reliability. |
| Import Power Trace | Power rails, energy per run, average power, peak power, voltage/current samples, sampling rate, meter identity, runtime trace id, integration window, board id, firmware id, and package id. | `power_thermal.json` | power measurement only when tied to a measured board run | Energy and peak power for the tested setup. | It does not prove task accuracy or long-term reliability. |
| Import Thermal Trace | Temperature locations, temperature trace, sampling rate, equipment, board id, firmware id, runtime trace id, integration window, and package id. | `power_thermal.json` | thermal measurement only when tied to the same measured run | Heat behavior for the tested setup. | It does not prove accuracy unless paired with task results under the same condition. |
| Import Task Accuracy | Dataset, scenario, metric, baseline result, candidate result, hardware result when available, tolerance, sample count, and failure slices. | `task_accuracy.json` | task accuracy result | The mapped or hardware-run model still solves the tested task. | It does not prove energy, heat, or update safety. |
| Import Calibration Trace | Calibration profile, monitor readings, weak tiles, correction values, drift profile, pass/fail status, recalibration commands, and fallback behavior. | `calibration_trace` and related step artifacts | lab or board evidence when measured | The run used a known correction profile under known conditions. | It does not prove long-term reliability unless repeated over time and conditions. |
| Import Weight Update Report | Update scope, write latency, write energy, endurance, retention, rollback, recalibration, failed-update behavior, and post-update accuracy. | `weight_update_readiness.json` | reliability/update evidence when measured | Whether the chip supports fixed, periodic, adapter, or adaptive update behavior. | It does not prove full adaptive Physical AI without task and fallback evidence. |
| Import Sensor Path Report | Sensor type, capture latency, preprocessing, buffering, synchronization, input energy, data rate, and task linkage. | `sensor_boundary_readiness.json` | imported lab or system evidence | The package counted the input path before the model. | It does not prove analog core performance by itself. |

## User-Facing Status

Every action should end in one of these states:

- `not_run`: the action has not been started
- `needs_setup`: a tool, file, board, lab instrument, or credential is missing
- `running`: the action started and has not finished
- `passed`: the artifact was produced and validated
- `failed`: the action ran and returned a failure reason
- `imported`: the evidence file was imported and validated
- `rejected`: the file was imported but failed validation
- `blocked`: the action cannot support the requested claim

## What The Frontend Should Show

For every action, the frontend should show:

- what the user is about to run or import
- what file will be created or updated
- what proof level the result can reach
- what claims may unlock if the result passes
- what claims stay blocked even if the result passes
- what setup is missing if the action cannot run
- where the raw log or imported file is stored

## What The Backend Must Enforce

The backend should reject or downgrade evidence when:

- the package id does not match
- the workload id does not match
- the chip target does not match
- the board id does not match a board-bound claim
- the firmware version is missing for a board-bound claim
- the measurement setup is missing for power or thermal claims
- the calibration profile is missing for a calibrated-run claim
- the task dataset or metric is missing for a task claim
- the artifact tries to unlock a stronger proof level than it supports

## Product Meaning

This map keeps the workflow honest.

A user should see that running the compiler, importing a board trace, importing a power trace, and importing a task result are different actions. Each action answers a different question. The final answer is only strong when the required actions all point to the same package and setup.
