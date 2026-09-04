# Cross-Repo AIMC Loop Proof

This page is the browser-reviewable version of the generated proof report.

The generated proof files are:

- `evidence/aimc-hardware-lab/cross-repo-loop-proof.md`
- `evidence/aimc-hardware-lab/cross-repo-loop-proof.json`

Run the proof from this repo:

```bash
python3 scripts/prove_cross_repo_aimc_loop.py
```

## What It Checks

```text
backend health
  -> backend hardware placement
  -> hardware-lab placement import
  -> governor request generation
  -> generated Verilog governor cases
  -> RTL trace check
  -> AIHWKIT/CrossSim adapter availability check
  -> optional AIHWKIT/CrossSim payload run path
  -> tensor-shaped backend MatMul simulator payload run path
  -> trained-weight uploaded-model simulator payload run path
  -> projection-stack simulator payload run path
  -> transformer-MLP-block simulator payload run path
  -> calibrated transformer-MLP-block simulator payload run path
  -> calibrated deep transformer-MLP-stack simulator payload run path
  -> attention-block simulator payload run path
  -> calibrated attention-block simulator payload run path
  -> calibrated residual governor bridge
  -> residual-aware placement decisions
  -> hardware-lab evidence export
  -> physical-flow evidence export
  -> backend hardware-lab evidence import
  -> backend residual-aware placement API check
  -> backend archive check for residual placement and C2/C3 claim boundaries
  -> package claim-readiness refresh
```

This is the shortest concrete test that the old workbench and the newer hardware lab are connected.

## Current Passing Result

```text
PASS cross_repo_aimc_loop
package,pkg-e931662a01293df2
backend_operators,5
backend_analog_candidates,2
governor_rows,10
backend_governor_rows,5
rtl,pass
export_items,6
backend_import_accepted,6
strict_tool_evidence_imported,True
aihwkit_adapter,available
crosssim_adapter,available
optional_simulator_payloads,{"aihwkit": "wrote_payload", "crosssim": "wrote_payload"}
calibrated_deep_transformer_mlp_stack_simulator_payloads,{"aihwkit": "wrote_payload_threshold_fail", "crosssim": "wrote_payload"}
calibrated_residual_governor_rows,6
residual_aware_placement_allowed,2
claim_summary,{"blocked_lab_claims": 0, "needs_review_lab_claims": 2, "overall": "claim evidence needs review", "production_claim": "blocked", "supported_lab_claims": 3}
```

## Workflow Contract

Consumes: backend health, backend `hardware_placement`, hardware-lab placement import, governor generation, RTL checker output, routed OpenLane summary, AIHWKIT/CrossSim adapter status, simulator payload summaries, calibrated residual bridge output, residual-aware placement output, evidence export, strict analog simulator/tool sidecar export, backend evidence import, backend archive, and claim readiness.

Produces: a JSON proof report, a Markdown proof report, and a repeatable command result.

Supports: the old backend and the newer hardware lab are wired into one prototype loop for model graph to hardware-lab evidence to backend claim readiness. The saved deployment archive preserves the same residual-aware placement and C2/C3 claim-readiness boundaries exposed by the API.

Refuses: measured board performance, measured power, measured energy without same-runtime-trace runtime and power evidence, calibrated silicon, analog macro layout, package reliability, signoff, or tapeout readiness.

## What This Proves

The restored backend can turn a model graph into a hardware-placement artifact. The hardware lab can import that artifact, convert it into governor-sized rows, generate Verilog cases, pass the RTL checker, check AIHWKIT/CrossSim availability, run simulator payloads from small fixtures through calibrated deep transformer-MLP and attention-shaped fixtures, convert calibrated residuals into governor decisions, filter backend analog candidates through source-matched residual-aware placement, export normalized evidence including `physical_flow.json`, and re-import that evidence into the backend package.

The important point is not that every hardware question is solved. The important point is that the system now has a closed evidence path. A model-side decision becomes a lab input. A lab result becomes backend evidence. Backend evidence becomes a claim-readiness answer.

The archive is part of that path. The archive check now verifies that `claim-readiness.json` keeps the same C2 and C3 status as the live endpoint: local runtime remains a needs-review latency claim, local power remains a needs-review energy claim, and measured energy requires runtime and power from the same runtime trace ID, package, workload, board, start time, and end time.

## What This Does Not Prove

This proof does not make the analog chip real.

It does not prove:

- measured board latency
- measured energy
- calibrated silicon behavior
- physical analog macro integration
- foundation-model-scale AIHWKIT/CrossSim agreement
- final timing signoff
- package reliability
- manufacturability
- tapeout readiness

The correct current answer is narrower: placement and local accuracy evidence are supported, latency and energy need review, and production readiness remains blocked.

Even if a measured power payload is valid by itself, it does not support `C3` unless it matches the runtime window. Importing evidence and supporting a claim are separate decisions.

## Where It Fits

Previous page: `combined-aimc-workbench-end-to-end-goal.md`

Next pages:

- `aimc-evidence-ledger.md`
- `evidence-import-and-claim-readiness-first-principles.md`
- `ai-hardware-architecture-to-working-lab-bridge.md`
- `aimc-page-flow-audit.md`

Old workbench page:

```text
http://127.0.0.1:8024/analog-in-memory-ai-inference/software-architecture/index.html
```

The old frontend should use this page as the readable proof anchor for its Hardware Lab Evidence panel.
