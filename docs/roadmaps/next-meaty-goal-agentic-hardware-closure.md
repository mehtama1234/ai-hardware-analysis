# Next meaty goal: agentic hardware failure-to-closure loop

## Objective

Demonstrate one complete, reproducible LLM-assisted hardware engineering loop:
start from a requirement and seeded hardware failure, let an agent produce an
evidence-grounded diagnosis and bounded repair proposal, require human approval,
apply the repair only to a disposable copy, rerun the identical verification
scope, and carry the accepted RTL through the local physical-design flow into a
hash-bound release package.

The product claim is not autonomous tapeout. The claim is that an agent can
reduce engineering effort while deterministic tools, immutable evidence, and a
human reviewer control every state-changing action and every release claim.

The provider-free first replay is:

```bash
VERIFICATION_LLM_BATCH_COMMAND='python3 scripts/mock_llm_backend.py' \
VERIFICATION_COUNTER_REPAIR=1 \
VERIFICATION_TIMEOUT_REPAIR=1 \
VERIFICATION_REGISTER_REPAIR=1 \
python3 scripts/run_llm_agent_benchmark.py \
  --output /tmp/agentic-hardware-loop/llm-agent-benchmark.json
python3 scripts/run_llm_approved_counter_repair.py \
  --model-report /tmp/agentic-hardware-loop/llm-agent-benchmark.json \
  --output /tmp/agentic-hardware-loop/repair-review
python3 scripts/check_llm_approved_counter_repair.py \
  /tmp/agentic-hardware-loop/repair-review/repair-review.json \
  --model-report /tmp/agentic-hardware-loop/llm-agent-benchmark.json \
  --source benchmarks/seeded_counter/counter.sv
```

The first two commands create a review-required package. Applying the repair
requires an explicit reviewer identity and note:

```bash
python3 scripts/run_llm_approved_counter_repair.py \
  --model-report /tmp/agentic-hardware-loop/llm-agent-benchmark.json \
  --output /tmp/agentic-hardware-loop/repair-review \
  --approve --reviewer '<human reviewer>' \
  --approval-note 'Approve the bounded repair and identical-scope retest.'
```

The approval command must never be run merely because the model proposal is
valid; the reviewer is responsible for deciding whether the proposed change is
appropriate.

The same review-required boundary is available as one command:

```bash
python3 scripts/run_agentic_hardware_closure.py \
  --output /tmp/agentic-hardware-loop
```

It refuses to reuse a non-empty output directory, records the benchmark,
primary repair-review, and held-out temporal repair-review paths in
`closure-summary.json`, and exits successfully only when both review packages
pass independent verification.

After a real human review, the same orchestrator can complete the disposable
copy-only retest:

```bash
python3 scripts/run_agentic_hardware_closure.py \
  --output /tmp/agentic-hardware-loop-approved \
  --approve --reviewer '<human reviewer>' \
  --approval-note 'Approve the bounded repair and identical-scope retest.' \
  --physical-handoff evidence/seeded-counter/model-repair-rtl2gds-handoff-20260913.json
```

The approved mode still hashes the canonical source before and after the run;
it never writes the canonical RTL. The optional physical handoff is imported
evidence and is accepted only when its staged RTL hash exactly matches the
repaired copy and its recorded LVS result is clean; it is not represented as a
same-run physical execution.

When the local OpenLane prerequisites are available, the stronger same-run
path is:

```bash
python3 scripts/run_agentic_hardware_closure.py \
  --output /tmp/agentic-hardware-loop-openlane \
  --approve --reviewer '<human reviewer>' \
  --approval-note 'Approve the bounded repair and identical-scope retest.' \
  --run-physical
```

`--run-physical` runs the formal suite and OpenLane against the approved
disposable `counter_repaired.sv`, then independently checks the generated
RTL-to-GDS handoff and staged-source hash.

An existing verified real-model report can be fed into the same state machine;
the Colab runner used `Qwen/Qwen2.5-0.5B-Instruct` on a Tesla T4:

```bash
python3 scripts/run_agentic_hardware_closure.py \
  --output /tmp/agentic-hardware-loop-real-model \
  --model-report .artifacts/llm-agent-colab/<run>/llm-agent-benchmark-colab.json \
  --approve --reviewer '<human reviewer>' \
  --approval-note 'Approve the bounded repair and identical-scope retest.' \
  --run-physical
```

The real-model artifact is independently verified before it enters the repair
boundary; the approval flag remains a human-controlled state transition.

## Canonical journey

```text
requirement/specification and RTL intake
  -> typed design and failure contract
  -> generated tests/assertions and baseline execution
  -> evidence-grounded LLM diagnosis
  -> bounded repair proposal with exact source revision
  -> adversarial contract review
  -> explicit human approval
  -> copy-only patch application
  -> identical-scope simulation/formal retest
  -> OpenLane synthesis, STA, DRC, LVS, and GDS checks
  -> joined release manifest and reviewer decision
```

The same evidence contract must then be exercised on a held-out temporal or
interface design, and the accepted digital result must remain traceably linked
to the AIMC physical boundary. Analog execution remains disabled unless its
independent converter gates pass.

## Required acceptance gates

1. The request contains a requirement ID, baseline source hash, failure signal,
   cycle or trace location, expected/actual behavior, and evidence references.
2. The LLM returns schema-valid JSON grounded in the supplied source revision
   and evidence. Invalid, incomplete, or unsupported output is rejected.
3. A repair is bounded to an allow-listed operator or exact before/after
   mutation, includes rationale and expected effect, and cannot claim closure.
4. A human approval record names the proposal, source hash, scope, reviewer, and
   decision. The original source is never silently modified.
5. The repaired copy passes the same simulation, formal, assertions, inputs,
   timeout, and coverage scope as the baseline, with a machine-checked diff and
   regression report.
6. The repaired RTL is hash-linked to the OpenLane run. Extracted STA, DRC,
   LVS, GDS, and XOR results are independently checkable.
7. The final manifest separates passed, failed, blocked, modeled, and
   unauthorized claims, and is replayable from a clean checkout.
8. The held-out design repeats the diagnosis/repair/retest contract, including a
   temporal or interface failure and at least one formal property.

## Deliverables

- Benchmark metrics for diagnosis accuracy, repair success, regression rate,
  unsupported-claim rate, latency, and human review effort.
- One complete primary-design evidence bundle and one held-out-design bundle.
- Independent checkers for grounding, approval, identical scope, source hashes,
  physical-flow provenance, and release-manifest integrity.
- A conservative agentic release manifest that records digital/physical claim
  status, keeps `analog_authorized=false`, and cannot turn fixture approval into
  a releasable decision.
- Browser/API/CLI exposure of the same state machine and deterministic errors.
- A traceable handoff to the AIMC qualification package, with
  `analog_authorized=false` until physical converter gates pass.

## Explicit non-goals

This does not claim unrestricted code generation, unattended repair, commercial
EDA signoff, measured analog or energy performance, GPU performance, silicon
yield, or tapeout readiness. Those remain separate evidence tiers.

## Done means

An independent reviewer can replay the run, inspect the exact failure and
evidence presented to the LLM, approve or reject the bounded repair, verify that
the retest scope did not change, reproduce the RTL-to-GDS results, and see
precisely why any analog, hardware, or production claim remains blocked.

The reviewer-facing checklist and digest-bound API example are in
[`agentic-closure-human-review-runbook.md`](agentic-closure-human-review-runbook.md).
