# Multi-design LLM repair evaluation — 2026-09-13

This report records the next increment after the AIMC end-to-end proof. The
real Qwen model ran in the OAuth-backed Colab runtime and selected bounded,
exact source edits for two different RTL failure patterns.

## Results

| Design | Failure pattern | Model repair | Copy retest | Physical handoff |
|---|---|---:|---:|---:|
| `aimc_multi_clock_control_subsystem` | inverted readout-fallback branch | passed | passed | passed locally |
| `seeded_counter` | missing enable guard | passed | passed | passed locally |
| `seeded_timeout` | one-cycle-late timeout threshold | passed | passed | passed locally |
| `register_peripheral` | missing address-zero decode | passed | passed | passed locally |

The final Colab artifact is:

`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/multi-design-bounded-repairs-20260913/llm-agent-benchmark-colab.json`

It passes the existing 11/11 diagnosis contract, AIMC diagnosis and repair
gates, and the seeded-counter and seeded-timeout repair gates. All repair tasks use
schema-constrained exact source choices and remain review-required until
explicit approval.

The seeded-counter approved copy artifact is:

`analog-digital-chip-design-eda/.artifacts/llm-approved-counter-repair-model-generated-20260913b/repair-review.json`

Its independent checker passes. The repaired copy compiles and produces the
`PASS` testbench marker; the canonical counter source hash is unchanged.

The counter’s specification-model formal proof is recorded at
`analog-digital-chip-design-eda/.artifacts/seeded-counter-formal-model-generated-20260913/formal-report.json`.
It proves the repaired implementation agrees with the reset-seeded reference
model for six bounded cycles. The complete physical handoff is:

`analog-digital-chip-design-eda/evidence/seeded-counter/model-repair-rtl2gds-handoff-20260913.json`

Its independent checker is
`analog-digital-chip-design-eda/scripts/check_seeded_counter_rtl2gds_handoff.py`
and passes with zero LVS errors, zero detailed-route DRC violations, clean
Magic DRC, extracted STA, and zero layout XOR differences.

The third-design temporal proof is recorded at
`analog-digital-chip-design-eda/.artifacts/seeded-timeout-formal-model-generated-20260913/formal-report.json`.
The model-generated repair lowers the timeout threshold from four to three,
passes the copy-only retest, and proves agreement with the specification model
for the bounded proof window. Its complete physical handoff is:

`analog-digital-chip-design-eda/evidence/seeded-timeout/model-repair-rtl2gds-handoff-20260913.json`

The independent checker is
`analog-digital-chip-design-eda/scripts/check_seeded_timeout_rtl2gds_handoff.py`.
It passes with the repaired source hash identical to the staged physical
source, zero LVS errors, clean detailed-route and Magic checks, extracted STA,
GDS, and zero layout XOR differences.

The aggregate release manifest is
`analog-digital-chip-design-eda/evidence/four-design-closed-loop-release-20260913.json`.
Its independent checker is
`analog-digital-chip-design-eda/scripts/check_three_design_release_manifest.py`.
The counter formal report now proves three separately executed property
obligations (reset, hold, and enabled increment), and the timeout report proves
four (reset, start boundary, timeout boundary, and not-early behavior). The
AIMC scheduler/governor property suite is now also recorded and passed;
the aggregate therefore carries formal-suite evidence for all three designs.
The AIMC suite is deliberately scoped to the exhaustive combinational policy
boundary, not the full multi-clock controller or analog substrate.

The AIMC sequential campaign is recorded at
`analog-digital-chip-design-eda/.artifacts/aimc-sequential-property-suite-20260913/sequential-report.json`.
It passes fourteen temporal checks on the actual multi-clock subsystem,
including reset determinism and recovery, both directions of two-edge CDC
latency, repeated acceptance/fallback accounting, and the accounting
partition invariant. This is simulation-backed stress evidence and does not
replace exhaustive formal CDC analysis.

The aggregate now also includes a separate stateful formal artifact at
`analog-digital-chip-design-eda/.artifacts/aimc-stateful-formal-suite-saturation-depth32-final-20260913/formal-report.json`.
Yosys SAT proves 20 assertions through bounded depth 32 for the single-clock
micro-tile controller, including reset state, counter monotonicity, bounded
per-cycle increments, saturation behavior, and execution/reason consistency.
This strengthens the controller proof boundary but intentionally does not
claim exhaustive multi-clock CDC proof.

The fourth protocol-design package is
`analog-digital-chip-design-eda/evidence/register-peripheral/model-repair-rtl2gds-handoff-20260913.json`.
The model selected the exact address-zero decode repair, the disposable copy
passed its hierarchical bus testbench, and three separate CSR properties
(reset, nonzero-address hold, and zero-address write) passed. The physical
handoff is hash-linked to the repaired CSR source and has zero LVS errors,
clean detailed-route and Magic checks, extracted STA, GDS, and zero XOR
differences.

## What this proves

The repair interface is no longer specific to AIMC. It represents three
bounded repair operators: changing an inverted Boolean guard, adding a missing
enable guard, and lowering a temporal timeout threshold. The model still
proposes a reviewable action; the system
does not allow free-form source mutation, automatic production release, or an
unsupported closure claim.

## Remaining gate

The four-design local generalization gate is now complete. The next
implementation increment is to measure repair/retest/review latency and
persistent optimization history, then add exhaustive formal CDC/controller
properties where the available tool flow supports them. The multi-design
release should report per-design
repair accuracy, formal status, physical closure, warnings, source hashes, and
human review time.

The first measured workflow baseline is
`analog-digital-chip-design-eda/evidence/closed-loop-measurement-20260913.json`,
with append-only history in
`analog-digital-chip-design-eda/evidence/closed-loop-measurement-history.jsonl`.
The model batch p50/p95 was 184.1 seconds. Local OpenLane runtimes were 1,312.2
seconds for AIMC, 375.7 seconds for the register peripheral, 301.9 seconds for
the counter, and 364.0 seconds for the timeout design. These are run metadata,
not a statistically controlled performance benchmark. The history verifier is
`analog-digital-chip-design-eda/scripts/check_closed_loop_history.py`.

The first controlled physical optimization comparison is
`analog-digital-chip-design-eda/evidence/register-peripheral-density-optimization-20260913.json`.
Both configurations used the same repaired CSR source hash and passed LVS,
route/physical checks, and extracted STA. The low-density target used
0.0043055 mm² and 292.3 seconds; the high-density target used 0.0021498 mm²
and 306.5 seconds. Both had zero SPEF WNS/TNS and six recorded warnings, so
the result is a two-point Pareto frontier: high density wins area, low density
wins runtime. No single configuration is promoted as globally optimal.

This remains local open-source research evidence. It does not establish
Innovus, ICC2, PrimeTime, foundry signoff, FPGA emulation, analog measurement,
manufactured silicon, or zero-bug operation.

The larger-controller optimization follow-up is recorded at
`analog-digital-chip-design-eda/evidence/aimc-density-optimization-20260913.json`.
The same repaired AIMC source was run through two controlled OpenLane density
configurations. The low-density point used 0.107877 mm² and 989.9 seconds;
the high-density point used 0.050354 mm² and 1,438.8 seconds. Both completed
the local flow with zero detailed-route violations, zero Magic DRC violations,
zero LVS errors, zero layout XOR differences, and zero extracted SPEF WNS/TNS.
Both retain the same max-fanout and standard-cell-blackboxing warnings. This
is therefore a second two-point Pareto result: high density wins area and low
density wins runtime. The append-only history now contains three hash-linked
measurement records; the history checker passes.

The deterministic next-candidate recommendation is
`analog-digital-chip-design-eda/evidence/next-physical-configuration-recommendation-20260913.json`.
Using explicit weights of 50% area, 30% runtime, and 20% timing, it selects
the high-density AIMC point for human review. The recommendation is advisory;
it does not launch a run or authorize a physical-design change.
