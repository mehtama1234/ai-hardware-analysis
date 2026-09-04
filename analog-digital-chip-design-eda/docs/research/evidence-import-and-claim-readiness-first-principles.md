# Evidence Import And Claim Readiness From First Principles

This page explains the backend step that turns hardware-lab files into allowed and blocked claims.

The question is:

What can the workbench honestly say after it imports evidence from the hardware lab?

The answer is not decided by excitement about the chip. It is decided by source IDs, required fields, provenance, quality checks, and claim boundaries.

## Workflow Contract

Consumes: hardware-lab evidence JSON, backend evidence schema, package ID, provenance fields, and claim-readiness rules.

Produces: imported evidence records, claim statuses, quality issues, evidence details, safe statements, and do-not-claim warnings.

Supports: a reviewer can see which narrow lab claims are supported, which need review, and which claims remain blocked.

Refuses: turning local simulation, local RTL traces, or local OpenLane estimates into measured board, measured power, calibrated silicon, or production-readiness claims.

## The First Principle

An artifact is not a claim.

An artifact is a recorded result:

```text
file
  -> fields
  -> provenance
  -> validation
  -> import record
  -> claim rule
  -> supported / needs review / blocked
```

The backend should never jump straight from "a file exists" to "the claim is true." It must ask what kind of file it is, what fields it contains, how it was produced, and what the claim requires.

That is why the evidence importer and claim-readiness code are central. They are the part of the system that prevents the pages from overclaiming.

## Evidence Source IDs

The current hardware-lab batch exports six backend-compatible evidence records:

- `compiler_mapping`
- `analog_error_simulation`
- `board_runtime`
- `power_thermal`
- `task_accuracy`
- `physical_flow`

Each source ID has a different job. They must not be swapped.

`compiler_mapping` is about model-to-hardware placement. It can support a discussion of analog candidates, digital-only regions, converter boundaries, and fallback points. It cannot support latency, energy, accuracy, or production readiness by itself.

`analog_error_simulation` is about the local analog error chain. It can support a discussion of residual error under the selected local assumptions. It cannot support calibrated silicon behavior.

`board_runtime` is about runtime trace shape. In the current project it is a local RTL/runtime trace, not a real board trace. It can show the control path, generated cases, fallback events, synthesis context, and OpenLane context. It cannot prove measured board latency.

`power_thermal` is about energy and thermal evidence. In the current project it is a local OpenLane-derived estimate. It can support a needs-review energy discussion. It cannot prove measured power or measured thermal behavior.

`task_accuracy` is about model-facing effect. In the current project it is a toy transformer-sensitivity proxy. It can support a local accuracy/sensitivity claim for that toy setup. It cannot prove full pretrained-model quality.

## Claim Rules

The backend groups those sources into claim IDs:

```text
C1 compiler placement: compiler_mapping
C2 latency: board_runtime
C3 energy: board_runtime + power_thermal
C4 accuracy: analog_error_simulation + task_accuracy
P1 production readiness: always blocked for this lab slice
```

The rule is intentionally strict.

If a required source is missing, the claim is blocked.

If all required sources exist but the payload has a quality issue, the claim needs review.

If all required sources exist and the payload has no claim-specific quality issue, the claim is supported.

Production readiness stays blocked even when all lab evidence exists, because lab evidence is not enough for yield, repeatability, drift, calibration cost, packaging, software integration, customer operating conditions, and signoff.

## Why Local Runtime Needs Review

The current `board_runtime` record contains useful evidence:

- generated model-impact governor cases
- 10 trace events
- 6 fallback events
- local RTL checker result
- Yosys synthesis context
- OpenLane context

That is enough to discuss the local control path. It is not enough to claim measured board latency.

The quality issue is:

```text
Board runtime artifact came from local simulation, not a real board or external simulator trace.
```

So `C2` becomes `needs review`, not `supported`.

This is the correct behavior. The backend is not punishing the project. It is keeping the words matched to the evidence.

## Why Local Power Needs Review

The current `power_thermal` record contains:

- OpenLane-derived control-block estimate
- critical path
- area
- cell count
- assumed room-temperature boundary
- no meter
- no measured supply voltage
- `not_measured_hardware: true`

That is useful for a local estimate. It is not measured power.

The quality issue is:

```text
Power/thermal artifact came from local simulation, not synchronized hardware measurement.
```

So `C3` becomes `needs review`, not `supported`.

This prevents a common mistake: using layout or cell estimates as if they were measured chip energy.

## Why Placement And Accuracy Are Supported

`C1` is supported because a compiler-mapping artifact is present and its role is narrow. It only says the package has model-to-hardware placement evidence.

`C4` is supported because both analog error and task accuracy records are attached, and the local task-accuracy proxy passes within its recorded tolerance.

Those claims are still bounded.

`C1` does not mean the model has a complete compiler lowering.

`C4` does not mean a full pretrained model preserved quality.

They mean the current local evidence supports the current local placement and sensitivity discussion.

## Current Live Result

Endpoint:

```text
http://127.0.0.1:8025/deployment-packages/pkg-e931662a01293df2/claim-readiness
```

Current summary:

```text
supported lab claims: 2
needs-review lab claims: 2
blocked lab claims: 0
production claim: blocked
overall: claim evidence needs review
```

The important word is `needs-review`. It means the records exist, but their provenance is weaker than the stronger claim.

## What The Frontend Should Show

The frontend should not collapse the claim states into one success/failure badge.

It should show:

- `C1`: supported placement discussion.
- `C2`: needs-review latency discussion because runtime is local simulation.
- `C3`: needs-review energy discussion because power is a local estimate.
- `C4`: supported local accuracy/sensitivity discussion.
- `P1`: blocked production readiness.

That is the honest product answer.

## What Would Upgrade The Claims

To upgrade `C2`, attach a real board trace or a stronger external simulator/runtime trace with the setup named. The required runtime fields and claim boundary are defined in `board-and-power-measurement-boundary.md`, and the step-by-step upgrade path is `measured-runtime-power-claim-upgrade-path.md`.

To upgrade `C3`, attach synchronized runtime and power measurement: meter, supply voltage, sampling window, workload, host overhead boundary, and thermal setup. The power record must describe the same runtime trace ID and run window as the runtime record; otherwise it stays an imported artifact but the claim remains needs review.

To make production readiness less blocked, add calibrated silicon behavior, analog macro layout, repeatability, drift over time, packaging, test, reliability, customer operating envelope, and signoff evidence.

The page language should not change before the evidence changes.

## Where This Page Fits

Previous pages:

- `backend-hardware-placement-first-principles.md`
- `aimc-evidence-ledger.md`
- `board-and-power-measurement-boundary.md`
- `measured-runtime-power-claim-upgrade-path.md`

Next pages:

- `cross-repo-aimc-loop-proof.md`
- `aimc-page-flow-audit.md`

Old backend source:

```text
ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend/evidence_imports.py
ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend/claim_readiness.py
```

Old frontend review:

```text
http://127.0.0.1:8024/analog-in-memory-ai-inference/software-architecture/index.html
```
