# Real-model verification-agent evaluation: 2026-09-13

## Result

The final real-model Colab evaluation completed on a Tesla T4 using
`Qwen/Qwen2.5-0.5B-Instruct`. The benchmark used the 11 versioned failure
records in `benchmarks/multi_design_pilot/fault-taxonomy.json`, including each
design's observed signal, cycle, expected value, actual value, source revision,
and evidence references. The deterministic reference workflow passed its 11/11
seeded-design retests, and the real model passed all 11 proposal-acceptance
cases.

The final downloaded run is stored under the local EDA artifact directory as
`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/aimc-llm-agent-20260913T084302Z`.

The AIMC-connected rerun is stored as
`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/aimc-llm-agent-20260913T085804Z`.

The stricter root-cause experiment is stored as
`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/aimc-llm-agent-20260913T090744Z`.

The larger-model comparison is stored as
`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/aimc-llm-agent-20260913T091505Z`.

The refined source-grounded root-cause run is stored as
`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/aimc-llm-agent-20260913T092511Z`.

The latest repair-generation run is stored as
`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/aimc-llm-agent-20260913T093334Z`.

The controlled retry with a larger generation budget is stored as
`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/aimc-llm-agent-20260913T094227Z`.

The focused repair-context run is stored as
`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/aimc-llm-agent-20260913T095738Z`.

## Evidence

- GPU probe: Tesla T4, 15,360 MiB.
- Open-source tool installation: passed.
- Model download: passed.
- Reference closure lab: passed, 11 designs and 11 passing retests.
- Model invocation: passed.
- Model acceptance: passed, 11/11.
- AIMC mutation baseline: passed as a deliberate copy-only failure.
- AIMC mutation diagnosis: passed the same model, grounding, signal/cycle,
  review, and adversarial checks.
- AIMC mutation repair/retest: passed in a disposable copy; the full AIMC
  testbench returned `PASS`, and all seven RTL inputs matched both canonical
  RTL and the physical-flow inputs.
- Root-cause rationale gate: failed. The model localized the failing
  `execution_path`, but did not identify the deliberately inverted
  `readout_fallback` condition; the stricter gate rejected it.
- Larger Qwen 1.5B comparison: failed. It produced malformed output on several
  cases and did not pass the AIMC root-cause gate. This is why malformed model
  output is now reported as blocked instead of being wrapped as a proposal.
- Refined Qwen 0.5B root-cause run: passed the 11-case contract and the AIMC
  root-cause rationale gate after receiving a focused RTL decision block and
  observed `readout_fallback`/`readout_valid` values.
- Model-generated AIMC repair: blocked. The model did not emit the required
  structured `before`/`after` RTL proposal, so the repair was not applied and
  no model-generated repair success is claimed.
- The larger-output-budget retry produced the same safe block, confirming
  that simply allowing more output tokens did not close the repair gate.
- The focused repair-context retry produced a structured repair proposal, but
  it changed execution assignments instead of reversing the inverted branch
  condition. Exact mutation matching rejected it.
- Colab session cleanup: passed; no active session remained after the run.

The initial experiments exposed two real integration issues: unconstrained
small-model output omitted required fields, and the newest Transformers release
was incompatible with the JSON-constrained decoder. The final package pins a
compatible Transformers 4.x release, uses schema-constrained output, and keeps
the deterministic adversarial checks unchanged. The exact action locator is a
request-derived safety field; the model still supplies the rationale and must
remain grounded and review-gated. No RTL was modified and no signoff claim was
made.

## Interpretation

This result proves a reproducible real-model, evidence-grounded diagnosis and
root-cause-rationale milestone on both the seeded Verilog corpus and a
deliberately mutated AIMC controller. It does not prove that the model
generated the RTL repair itself, autonomous repair, formal completeness, RTL2GDS
correctness, commercial EDA equivalence, physical hardware behavior, silicon
correctness, or tapeout readiness. The model is still not authorized to edit
RTL or close a failure.

## What this unlocks

The one-design repair bridge is now implemented at
`analog-digital-chip-design-eda/scripts/run_llm_approved_counter_repair.py`.
Its independent gate checker is
`analog-digital-chip-design-eda/scripts/check_llm_approved_counter_repair.py`.
Its current review artifact is
`analog-digital-chip-design-eda/.artifacts/llm-approved-counter-repair/repair-review.json`.
It consumed the accepted `seeded_counter` model diagnosis, derived the exact
bounded enable-guard repair, and stopped with `decision: review_required`
without modifying canonical RTL.

The same bridge was exercised in a disposable copy with a clearly labeled
`test-fixture` approval. The copy compiled and simulated with `PASS`, and the
canonical source hash remained unchanged. This is a mechanical integration
test, not human or production signoff; the resulting evidence is under
`analog-digital-chip-design-eda/.artifacts/llm-approved-counter-repair-test/`.

The AIMC-specific mechanical repair/retest evidence is under
`analog-digital-chip-design-eda/.artifacts/aimc-mutation-repair-retest/` and is
independently checked by
`analog-digital-chip-design-eda/scripts/check_aimc_mutation_repair_retest.py`.

The remaining steps for one-design repair closure are:

1. Feed one accepted model diagnosis into a human approval record.
2. Generate a bounded repair proposal against the diagnosed RTL.
3. Apply it only to a copy, never the original source.
4. Rerun the identical simulation/formal scope.
5. Require the failure to resolve, preserve source hashes, and emit a signed
   evidence package.

The model has now been connected to a deliberate AIMC mutation and has passed a
focused root-cause rationale gate. The remaining research gap is a
model-generated root-cause repair rather than reversal of a known mutation.
The scorer must remain unchanged: every case must
be available, grounded, diagnosis matching, `review_required`, and
adversarially accepted. A model that fails any case remains a failed
evaluation.

The next rerun uses JSON-schema-constrained decoding through
`lm-format-enforcer`; it does not relax the semantic diagnosis or adversarial
checks.

The repair retest harness now consumes only an available, grounded proposal
whose exact text reverses the bounded mutation. It returns `review_required`
when the model proposal is missing or wrong, and requires explicit approval
before editing a disposable copy. A separately explicit `--allow-known-reversal`
path preserves the earlier mechanical integration test; its latest artifact is
`analog-digital-chip-design-eda/.artifacts/aimc-mutation-repair-retest-latest/`.
The independent checker passes, but this remains a known-reversal test and not
an autonomous model repair.

A fresh tagged OpenLane attempt was also made after the repaired-copy retest.
The local OpenLane installation was found, but execution stopped before RTL2GDS
because the configured PDK root did not contain `sky130A`. Existing checked
physical artifacts remain available, but this new run cannot be treated as a
fresh physical qualification result until the PDK is restored.

The attempted user-writable PDK restoration fetched and configured the pinned
Sky130 sources, but failed during the Magic technology install with exit 139
while generating primitive and digital-cell databases. A second digital-only
attempt failed at the same Magic technology-install step. The source checkout
and partial build are retained under
`analog-digital-chip-design-eda/.artifacts/sky130-pdk/` for diagnosis; no
canonical RTL or checked physical package was changed.

After rebuilding the PDK with the Docker Magic wrapper and explicitly selecting
the Sky130 technology/startup file, the fresh OpenLane run advanced much
further. Run directory:
`/home/mehtama1/eda-tools/OpenLane/designs/aimc_control_plane/runs/aimc_llm_guided_repair_retest_no_diode_repair_v2_20260913/`.
It completed routing with zero detailed-route DRC violations, SPEF extraction,
min/max/nominal extracted STA, Magic and KLayout GDS generation, and a
zero-difference Magic/KLayout XOR. Extracted nominal STA reported WNS 0.00,
TNS 0.00, worst setup slack 6.16 ns, and worst hold slack 1.26 ns. The flow
still failed LVS with 74 reported errors (net count difference 2), because the
diagnostic no-diode configuration disables antenna repair and does not yet
constitute final signoff.

The benchmark now preserves a structured invalid payload when the backend can
decode one, making the next model/adapter diagnosis observable instead of
reducing every failure to a generic missing-field message.

The final local-flow comparison was completed after rebuilding the user-writable
Sky130 package. The standard configuration restored heuristic antenna repair,
but OpenLane stopped at global routing with `GRT-0244`: the generated
`sky130_fd_sc_hd__diode_2` LEF has no `ANTENNADIFFAREA` value. This is a
PDK/cell-metadata problem, not an RTL, simulation, or model-diagnosis failure.
The diagnostic configuration with antenna repair disabled progressed through
route, extraction, extracted STA, GDS generation, and zero-difference
Magic/KLayout XOR, but failed LVS with 74 errors; it is not signoff evidence.

The reliable local physical baseline remains the existing
`aimc_control_plane_local` OpenLane package, which completed its flow and has
zero-error LVS evidence. The rebuilt-PDK attempts are retained as reproducible
failure evidence and do not replace that baseline. This phase therefore closes
with LLM diagnosis/root-cause success, safe rejection of incorrect model
repairs, a passing known-reversal copy test, and a clearly isolated PDK repair
task remaining before a fresh physical rerun can be called clean.

Final bounded-repair rerun: `.artifacts/llm-agent-colab/aimc-llm-agent-bounded-repair-fixed-20260913/`.
After correcting the checker’s reversed comparison, the authoritative Colab
artifact passes 11/11 normal model cases, AIMC diagnosis, root-cause support,
adversarial review, and the exact model-selected repair. The final copy-only
retest is `.artifacts/aimc-mutation-repair-retest-model-generated-final-20260913/`
and its independent checker passes with seven aligned RTL sources.

The model-generated repaired source was then staged byte-for-byte into the
physical run. Handoff artifact:
`evidence/aimc-hardware-lab/model-generated-aimc-rtl2gds-handoff-20260913.json`.
The same-design OpenLane run reached zero detailed-route DRC violations,
three-corner extracted STA, GDS, and zero Magic/KLayout XOR differences. It
failed LVS with 298 errors (65 unmatched nets, 134 unmatched devices, and 97
unmatched pins), so the joined artifact is correctly marked `partial`. The
remaining end-to-end gate is a clean LVS-capable PDK/library setup; the model
repair and RTL-to-extracted-layout linkage are now demonstrated.

Final completion of the local same-design goal: the preserved complete Sky130
PDK was used for run
`/home/mehtama1/eda-tools/OpenLane/designs/aimc_multi_clock_control_subsystem/runs/aimc_model_generated_repair_rtl2gds_complete_20260913/`.
The flow completed through LVS, with zero LVS errors, zero detailed-route DRC
violations, zero Magic DRC violations, zero antenna violations, extracted STA,
and zero Magic/KLayout XOR differences. The final joined handoff is
`evidence/aimc-hardware-lab/model-generated-aimc-rtl2gds-handoff-final-20260913.json`;
its independent checker is
`scripts/check_model_generated_aimc_handoff.py` and passes.

This closes the current local proof: a real Colab LLM selected a bounded RTL
repair, the approved copy passed verification, and that exact repaired source
was taken through local RTL2GDS/STA/DRC/LVS evidence. The run still reports a
max-fanout warning, and the result remains local research evidence—not
commercial Innovus/ICC2/PrimeTime signoff, foundry tapeout, analog measurement,
FPGA emulation, or silicon evidence.
