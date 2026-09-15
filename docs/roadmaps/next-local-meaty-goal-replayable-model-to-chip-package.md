# Next local meaty goal: replayable model-to-chip qualification package

## Objective

Close the entire model-to-chip software decision loop locally for one frozen
transformer slice. Starting from checked-in workload tensors and a versioned
converter profile family, produce a deterministic package comparing the digital
reference, profile-driven hybrid execution, compiler/runtime schedule, and
guarded fallback decision.

This goal does not claim fresh CUDA, SPICE, board, silicon, or customer
evidence. It makes the software boundary complete and ready to accept those
measurements later without changing the workload contract or decision logic.

## End-to-end path

```text
frozen model slice and held-out tensors
 -> canonical operator/workload contract
 -> digital reference outputs
 -> nominal, calibrated, pessimistic, and failure profiles
 -> profile-driven hybrid execution
 -> compiler partition and runtime trace
 -> accuracy, transfer, latency, energy, and fallback accounting
 -> immutable report, hashes, and bounded decision
```

## Why this is next

The local reference, public release, and customer-pilot rehearsal are already
closed. The physical converter and fresh GPU gates are unavailable at present,
but the software can still be made stronger by proving that every permitted
profile—including adverse and unsupported profiles—propagates consistently
through inference, scheduling, metrics, and authorization.

## Work packages

The first executable increment is now present in
`analog-in-memory-ai-inference/software-architecture/scripts/run_local_profile_family_replay.py`.
It replays five profile classes over the current 162-vector workload and is
independently checked by `check_local_profile_family_replay.py`. The generated
artifact is `experiments/gpt2-hybrid-v1/qualification/local-profile-family-replay`.

### 1. Freeze one complete workload contract

Record model revision, tensor shapes, dtypes, seeds, calibration and held-out
splits, reference outputs, operator order, and artifact hashes. Reject any
profile or result that names a different workload contract.

### 2. Build a versioned profile family

Represent nominal, calibrated, pessimistic, unsupported-range, clipping, and
timeout profiles using one schema. Every profile declares transfer error,
timing, calibration cost, data movement, uncertainty, energy scope, unsupported
regions, and evidence class. Synthetic profiles are counterfactual only.

### 3. Make hybrid execution and fallback deterministic

Run the same held-out tensors through each profile. Verify that clipping,
invalid state, timeout, numerical failure, and error-budget violation route to
the declared digital fallback. Record per-vector and per-operator reasons.

### 4. Close compiler/runtime agreement

Generate partition, conversion schedule, buffer movement, calibration steps,
retry policy, and fallback branches from the same contract consumed by the
simulator. Check operator order, tensor identity, conversion count, bytes moved,
and branch reason.

### 5. Produce one decision package

Create a self-contained archive containing the workload contract, profiles,
reference and hybrid outputs, traces, metric calculations, negative cases,
source hashes, and an independent verifier. The report must say whether the
analog path has a local software-level advantage, no advantage, or remains
unresolved. Keep `analog_authorized` false unless physical gates pass.

### 6. Prove replay and mutation resistance

Replay from a clean temporary directory. Change one bound input, profile field,
trace event, or source hash and verify rejection. Verify missing physical
evidence cannot be promoted by a green software replay.

## Definition of done

- One frozen transformer slice has a complete checked-in workload contract.
- All declared profile classes run against the same held-out inputs.
- Digital and hybrid outputs, fallback reasons, and metric arithmetic replay
  identically.
- Compiler and runtime traces agree on schedule and tensor movement.
- Adverse, unsupported, timeout, and malformed-profile cases are rejected or
  routed deterministically.
- A clean-extraction archive and independent verifier both pass.
- One bounded decision report links every result to source and artifact hashes.
- The report explicitly labels this local software/counterfactual evidence and
  does not authorize CUDA, board, silicon, or energy claims.

## Decision vocabulary

Use exactly one of:

- `digital_reference_and_deterministic_fallback_only`;
- `hybrid_software_path_bounded_but_no_cost_advantage`;
- `hybrid_software_path_locally_promising_physical_validation_required`;
- `unresolved_due_to_contract_or_replay_failure`.

A negative result is successful when reproducible and tied to the limiting
profile field, operator, fallback cause, or accounting term.

## Handoff boundary

When complete, fresh CUDA measurements replace only GPU evidence inputs,
qualified converter measurements replace only physical profile inputs, and
board measurements replace only measured latency/energy inputs. The workload,
compiler contract, runtime verifier, and claim boundaries remain unchanged.

The physical qualification roadmap remains separate at
`analog-digital-chip-design-eda/docs/roadmaps/next-meaty-goal-qualification-to-workload.md`.

## Physical EDA handoff status

The software and digital closed loop is ready to consume a qualified physical
profile, but the analog boundary is not yet qualified. The latest local EDA
milestone is a DRC-clean, hierarchy-checked, uniquely LVS-matched parent
interface for two explicit preamp cells. Its independent gate is:

```bash
python3 scripts/check_hierarchical_preamp_binding.py \
  --candidate evidence/aimc-simulator-adapters/active-converter-macro-candidate/two-single-preamp-parent-wired-20260913T520000Z \
  --output evidence/aimc-simulator-adapters/active-converter-macro-candidate/two-single-preamp-parent-wired-20260913T520000Z/hierarchical-binding
```

The remaining physical sequence is finite and now starts after parent LVS:
pass extracted transient polarity and logic-margin checks, characterize
noise/variation and energy/latency/area from that same run, then submit the
payload through the existing fail-closed converter gate. The 520000 extracted
transient currently measures both cases but fails the 0.9 V margin and one
polarity case in the full view. No fabricated values may be used to advance
the software decision loop.
