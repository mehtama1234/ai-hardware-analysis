# Current State Audit

Last updated: 2026-08-25

This is the short answer for where the analog / in-memory AI inference workbench stands.

## Big Picture

The app is now a working prototype for explaining and packaging analog edge AI readiness.

It can take an ONNX model, analyze the graph, estimate quantization and runtime behavior, compare against an estimated digital baseline, build a deployment-readiness package, show Physical AI fit, import normalized evidence, recalculate claim readiness, and export a self-describing archive.

It does not yet compile a model for real analog hardware. It does not run on a real board by default. It does not prove production readiness.

## Implemented End To End

Backend, frontend, saved endpoints, archive files, and smoke coverage exist for:

- `physical_ai_map`: places the workload in the Physical AI landscape.
- `vla_readiness`: explains transformer/VLA fit and why analog MAC efficiency is not enough.
- `weight_update_readiness`: separates fixed inference from field adaptation and on-chip write claims.
- `calibration_drift_readiness`: covers temperature, voltage, drift, aging, recalibration, and failure behavior.
- `control_boundary`: separates model inference from deterministic control and safety handoff.
- `sensor_boundary_readiness`: explains where physical signals become tensors and who owns preprocessing cost.
- `compiler_ecosystem_readiness`: marks ONNX as the current first path and PyTorch/JAX/XLA as roadmap unless implemented.
- `source_check_register`: shows checked examples with source links, allowed use, and do-not-claim boundaries.
- `toolchain_readiness`: describes model import, quantization, compiler mapping, simulation, runtime, power, accuracy, profiling, and handoff.
- `connection_playbook`, connector contracts, adapter execution, adapter templates, connector acceptance, backlog, delivery plan, and risk register.
- evidence import, claim readiness, evidence audit, evidence brief, interview brief, interview drill, decision report, rewrite suggestions, what-if estimates, rewrite plan, and work order.

## What Is Simulated Or Local

These paths are useful workflow proof, but not hardware proof:

- runtime latency and energy are simulated unless real board evidence is imported
- digital baseline comparison is estimated
- local board-runtime and power/thermal evidence can be replay fixtures
- analog error behavior is simulated unless a real simulator artifact is imported
- compiler mapping is not real hardware compiler output unless an imported compiler artifact is attached
- source-checked examples are case-study context, not compatibility or benchmark evidence

## What The App Blocks Or Limits

The app is intentionally conservative.

It does not let the user honestly claim:

- production readiness
- measured hardware performance
- analog is automatically better than digital
- TOPS/W is the full system answer
- prototype silicon proves manufacturable product readiness
- inference latency proves robot or actuator control readiness
- sensor-to-output energy when only inference energy was counted
- PyTorch or JAX/XLA support unless a real lowering path exists
- compatibility with Gemini Robotics, Rho-alpha, IMX636, NXP AFE parts, or Aspirare hardware

## What Is Still Missing

The real remaining work is external evidence and real tool integration.

Missing for stronger claims:

- real compiler-produced mapping artifacts
- real analog behavior simulator output or measured analog error sweeps
- real board runtime traces
- synchronized power and thermal measurement
- dataset-backed task accuracy for the selected workload
- sensor-to-output latency and energy accounting
- controller handoff traces for robotics or other physical systems
- real PyTorch/JAX/XLA export or lowering path
- hardware executable package
- production evidence: yield, repeatability, calibration cost, packaging, aging, drift, customer integration, and operating-condition sweeps

## Current Verification

Last full smoke status:

```text
smoke-ok ... archive_files=63
```

That smoke covers frontend markers, backend endpoints, saved package artifacts, archive contents, local evidence import, claim readiness, project run flow, and saved retrieval.

## Next Real Step

The next implementation step should not be another explanation panel.

The next useful step is to connect one real external evidence path, starting with the compiler mapping adapter or board runtime adapter:

- compiler first if the goal is model-to-hardware feasibility
- board runtime first if the goal is latency and runtime proof
- power/thermal first if the goal is energy claim proof
- task accuracy first if the goal is accuracy-after-quantization proof

Until one of those paths is real, the app is a strong architecture and evidence-readiness workbench, not a measured hardware validation system.
