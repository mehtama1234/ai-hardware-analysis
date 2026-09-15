# Agentic hardware closure: human review runbook

This is the final review boundary for the agentic hardware closure package. A
reviewer must inspect the evidence and make the decision; fixture approval is
not release approval.

## Evidence package

The retained real-model replay is:

`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/agentic-hardware-closure-realcolab-v4-20260913/`

It contains the Colab model report, primary and held-out repair reviews,
formal proofs, same-run OpenLane handoff, closure summary, AIMC boundary link,
and release manifest.

## Independent review commands

Run from `analog-digital-chip-design-eda/`:

```bash
ROOT=.
BUNDLE=.artifacts/llm-agent-colab/agentic-hardware-closure-realcolab-v4-20260913

python3 scripts/verify_llm_model_evaluation.py \
  "$BUNDLE/llm-agent-benchmark.json" --require-real-model
python3 scripts/check_seeded_counter_rtl2gds_handoff.py \
  "$BUNDLE/physical-handoff.json"
python3 scripts/check_agentic_hardware_closure.py \
  "$BUNDLE/closure-summary.json" \
  --source benchmarks/seeded_counter/counter.sv
python3 scripts/check_agentic_hardware_release_manifest.py \
  "$BUNDLE/agentic-hardware-release-manifest.json"
```

The reviewer should confirm the model is the stated Colab Qwen/T4 run, the
failure evidence and bounded before/after edits are appropriate, both retests
use the recorded scope, the physical source hash matches the repaired copy,
and the AIMC link remains traceability-only with `analog_authorized=false`.

## Record the decision

In a live service, load `/v1/agentic-closure`, copy its current
`manifest_sha256`, and submit an authenticated request to
`/v1/agentic-closure/signoff`:

```json
{
  "reviewer": "<reviewer identity>",
  "notes": "<what was inspected and remaining claim boundaries>",
  "approved": true,
  "manifest_sha256": "<digest returned by GET>",
  "review_started_at": "<UTC ISO-8601 timestamp>"
}
```

The service rejects stale digests and empty reviewer records, writes a
content-digested receipt containing the proposal/source/scope bindings, and
atomically rebuilds the release manifest. `approved: false` records a
`blocked_human_rejected` decision. Approval can produce `passed` only when the
closure, physical evidence, and measured review-effort gates all pass.

No decision authorizes analog execution, measured hardware, silicon, or
tapeout claims. The manifest must continue to report
`analog_authorized: false`.
