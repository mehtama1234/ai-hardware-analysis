# Current State Audit

Start from the [Connected System Map](connected-system-map.html). This audit uses the same contract: object, constraint, design move, evidence, allowed claim, refused claim, and next handoff.

Last updated: 2026-08-29

This is the short answer for where the analog / in-memory AI inference workbench stands.

## Big Picture

The app is now a working prototype for explaining and packaging analog edge AI readiness.

It can take an ONNX model, analyze the graph, estimate quantization and runtime behavior, compare against an estimated digital baseline, build a deployment-readiness package, show Physical AI fit, import normalized evidence, recalculate claim readiness, and export a self-describing archive. It now also connects to the newer `analog-digital-chip-design-eda` lab through package `pkg-e931662a01293df2`.

It does not yet compile a model for real analog hardware. It does not run on a real board by default. It does not prove production readiness.

The browser-readable version of this status is [Current Proof Ledger](current-proof-ledger.html).

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
- strict evidence API paths for ordinary evidence, strict simulator/tool evidence, and strict measured board/power evidence.
- measured energy claim synchronization: valid measured runtime and valid measured power support `C3` only when they name the same runtime trace ID, package, workload, board, start time, and end time.
- generated strict simulator/tool evidence from the newer lab at `evidence/aimc-hardware-lab/analog_error_simulation_strict_tool.json`.
- current-lab bridge proof from backend placement to analog lab records, governor traces, RTL/Yosys checks, OpenLane package readiness, routed OpenLane summaries for selected digital controllers, source-matched residual-aware placement, exported evidence, backend import, and claim readiness.
- residual-aware placement API and archive proof: the backend dense MatMul rows select `deep_transformer_mlp_stack` calibrated CrossSim evidence under the `fixed_weight_matmul_family_match` policy, and the downloaded archive preserves the same selected source and policy.

## What Is Simulated Or Local

These paths are useful workflow proof, but not hardware proof:

- runtime latency and energy are simulated unless real board evidence is imported
- digital baseline comparison is estimated
- local board-runtime and power/thermal evidence can be replay fixtures
- analog error behavior is simulated unless a real simulator artifact is imported
- the current local analog lab evidence is structurally useful but does not pass the strict simulator/tool gate
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
- same-run linkage between runtime and power records
- dataset-backed task accuracy for the selected workload
- sensor-to-output latency and energy accounting
- controller handoff traces for robotics or other physical systems
- real PyTorch/JAX/XLA export or lowering path
- hardware executable package
- production evidence: yield, repeatability, calibration cost, packaging, aging, drift, customer integration, and operating-condition sweeps

## Current Verification

Current verification status:

```text
page contract audit: PASS, checked_html=31, checked_md=37
strict evidence API: PASS
tool evidence readiness: PASS
measured evidence readiness: PASS
residual-aware placement API: PASS
residual-aware placement archive: PASS
backend compile: PASS
AIMC bridge: PASS, 50/50 checks
claim summary: supported_lab_claims=3, needs_review_lab_claims=2, blocked_lab_claims=0, production_claim=blocked
```

The bridge covers backend hardware placement import, SPICE-style comparison fixtures, analog tile error evidence, converter sweeps, tile operating point records, nonideality stack records, transformer-impact records, governor request generation, RTL traces, Yosys synthesis, OpenLane package readiness, routed OpenLane summaries for selected digital controllers, AIHWKIT/CrossSim adapter availability status, optional simulator payload-run summary, workload-shaped simulator payloads for selected analog candidates, tensor-shaped simulator payloads for backend analog MatMul candidates, trained-weight simulator payloads for the uploaded tiny MLP analog MatMul weights, projection-stack simulator payloads for a larger four-MatMul ONNX fixture, transformer-MLP-block simulator payloads with nonlinear and residual operations kept digital, calibrated transformer-MLP-block simulator payloads with held-out affine correction, calibrated deep transformer-MLP-stack simulator payloads with held-out affine correction, attention-block simulator payloads for static projections with dynamic attention kept digital, calibrated attention-block simulator payloads with held-out affine correction, calibrated residual governor bridge decisions, source-matched residual-aware placement decisions, backend residual-aware placement API and archive checks, hardware-lab evidence export, strict simulator/tool payload export, static site build, dry-run simulator payload examples, project validation, analog simulator adapter contract validation, guarded simulator payload import checks, and backend import of the exported evidence.

The strict API check proves the actual FastAPI endpoints used by the frontend can validate and import strict simulator/tool payloads and strict measured payloads, while rejecting current local analog lab evidence from the strict simulator import path. It also proves that local runtime/power cannot enter through measured import and that mismatched measured power can remain imported evidence while keeping `C3` in needs review.

## Next Real Step

The next implementation step should deepen one real evidence path, starting with a larger source-matched simulator replay, compiler, OpenLane, board runtime, or power path:

- larger source-matched simulator replay first if the goal is stronger analog-error evidence for fixed-weight MatMul work beyond the current toy backend and block fixtures
- compiler first if the goal is model-to-hardware feasibility
- OpenLane first if the goal is to promote routed physical-flow results into a separate backend evidence source for the digital control blocks
- board runtime first if the goal is latency and runtime proof
- power/thermal first if the goal is energy claim proof
- task accuracy first if the goal is accuracy-after-quantization proof

Until one of those paths is real, the app is a strong architecture and evidence-readiness workbench, not a measured hardware validation system.
