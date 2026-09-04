# Lab: AIMC Control Plane Synthesis With Yosys

This lab asks what changes when the AIMC control-plane RTL is lowered by a synthesis tool. The object is not the analog array. The object is the digital decision circuit that chooses analog, batched analog decode, hybrid operation placement, or digital fallback.

## Workflow Contract

Consumes: checked AIMC control-plane RTL, generated controller cases, Yosys scripts, and the policy boundaries defined by the analog and RTL labs.

Produces: synthesized Verilog netlists, Yosys statistics, cell counts, register counts, hierarchy summaries, and synthesis interpretation.

Supports: the claim that selected digital control rules can be lowered into gate-like logic in the local Yosys flow.

Refuses: routed layout, timing closure, power measurement, board behavior, analog macro behavior, and production signoff.

Handoff: this lab feeds the EDA/OpenLane labs and the hardware-lab evidence exporter. Its role in the backend package is context for local runtime/control evidence, not measured board proof.

## Where This Lands In The Combined Workbench

This lab is the translation-evidence part of the larger AIMC workflow.

```text
RTL decision rule
  -> Yosys lowering
  -> cells, registers, and mux/comparator structure
  -> OpenLane-ready block
  -> local evidence context
  -> backend claim readiness
```

The first-principles point is simple: synthesis changes the form of the rule without changing the rule. If the RTL says a sensitive path must fall back to digital, the synthesized logic must still contain the comparison and selection structure that enforces that refusal.

The current backend claim effect is limited. Synthesis evidence helps explain that the local controller is more than a Python rule, but it does not prove physical timing, routed geometry, measured latency, or measured energy. Those stronger claims need OpenLane evidence, then board and meter evidence.

## Object

The first object being preserved is the priority decision from `../aimc-control-plane-rtl/aimc_control_plane.v`.

The RTL says:

```text
unsafe or unavailable analog work -> digital fallback
long-context single decode -> digital fallback
batched decode -> batched analog path
otherwise -> analog path
```

Synthesis may rewrite the structure, but it must preserve that decision.

The second object is the operation partition from `../aimc-control-plane-rtl/aimc_operation_partition.v`.

That RTL says:

```text
digital-only transformer operations -> digital
fixed trained projections -> analog when evidence is inside budget
attention, value mixing, logits, adapters -> hybrid unless selection metrics force fallback
missing weights, stale weak tiles, high state error, high attention flips, or high token flips -> digital fallback
```

Synthesis may rewrite this structure too, but it must preserve the partition rule.

The third object is the tile readout from `../aimc-control-plane-rtl/aimc_tile_readout.v`.

That RTL says:

```text
ADC code becomes a centered digital measurement
gain and bias correction produce a bounded value
disabled tiles, stale calibration, high residual, and saturation force fallback
```

Synthesis may rewrite the arithmetic and comparison structure, but it must preserve the rule that analog output is not trusted until digital correction and validity checks accept it.

The fourth object is the integrated micro-tile controller from `../aimc-control-plane-rtl/aimc_micro_tile_controller.v`. It composes the operation partition and tile readout. The important rule is that an analog placement decision starts a readout, but the corrected value is accepted only on the next cycle if the readout reports valid.

The fifth object is the tile-service scheduler from `../aimc-control-plane-rtl/aimc_tile_service_scheduler.v`. It sits above the per-tile health action. It does not correct analog values and it does not store new history. It chooses whether this cycle should use analog service, recalibration, probe, or digital fallback after looking at four tile health actions, busy bits, the requested tile id, and the maintenance budget.

The sixth object is the error-budget governor from `../aimc-control-plane-rtl/aimc_error_budget_governor.v`. It sits beside the scheduler. The scheduler asks which tile action is available. The governor asks whether the next analog error is worth spending at all. It combines local residual, calibration age, model-path sensitivity, and cumulative state error into a bounded next-error estimate.

The seventh object is the integrated scheduler/governor from `../aimc-control-plane-rtl/aimc_scheduler_governor.v`. It instantiates the tile scheduler and error-budget governor together. The final decision is analog only when a serviceable tile exists and the governor permits the next error spend.

## Constraint

Yosys can convert the always block into registers, comparators, logic, and muxes. That proves the RTL can be lowered into a gate-like representation. It does not prove physical timing, clock-tree behavior, routing, power, or area in a real process.

The useful question is narrower:

```text
Does the RTL become a small sequential decision circuit with explicit registers and comparison logic?
```

## Concrete Design Move

Run:

```bash
yosys synth_aimc_control_plane.ys
yosys synth_aimc_operation_partition.ys
yosys synth_aimc_tile_readout.ys
yosys synth_aimc_micro_tile_controller.ys
yosys synth_aimc_tile_service_scheduler.ys
yosys synth_aimc_error_budget_governor.ys
yosys synth_aimc_scheduler_governor.ys
```

This writes:

- `reports/aimc_control_plane_synth.log`
- `reports/aimc_control_plane_synth.v`
- `reports/aimc_operation_partition_synth.log`
- `reports/aimc_operation_partition_synth.v`
- `reports/aimc_tile_readout_synth.log`
- `reports/aimc_tile_readout_synth.v`
- `reports/aimc_micro_tile_controller_synth.log`
- `reports/aimc_micro_tile_controller_synth.v`
- `reports/aimc_tile_service_scheduler_synth.log`
- `reports/aimc_tile_service_scheduler_synth.v`
- `reports/aimc_error_budget_governor_synth.log`
- `reports/aimc_error_budget_governor_synth.v`
- `reports/aimc_scheduler_governor_synth.log`
- `reports/aimc_scheduler_governor_synth.v`

Before technology mapping, the report should show two state registers:

- `path`
- `reason`

After technology mapping, those two registers appear as five flip-flop bits: two bits for `path` and three bits for `reason`. The report should also show comparison, Boolean, and mux logic for resident weights, tile count, estimated error, calibration age, context length, and batch size.

## Measurement

The measurement is the Yosys statistics section. For the current RTL, the important evidence is:

- five async-reset flip-flop bits for `path[1:0]` and `reason[2:0]`
- comparison cells for batch, context, tile count, error, and calibration age
- mux cells implementing the priority decision
- no inferred memories
- no remaining Verilog process after lowering

This is not a performance number. It is translation evidence: the control policy can move from readable RTL into a lower hardware representation.

For the operation-partition RTL, the important evidence is different. The module is combinational, so the report should show no flip-flop bits. It should show comparisons and Boolean logic for operation class, resident weights, state error, attention selection flips, token-choice flips, calibration age, and weak tiles. That proves the operation map can become hardware control logic rather than remaining only a prose rule.

For the tile-readout RTL, the important evidence is the presence of registered corrected output, valid/fallback bits, reason bits, arithmetic for gain/bias correction, and comparison logic for residual, calibration age, and saturation. That proves the analog tile boundary can become explicit digital hardware rather than a hidden assumption after the ADC.

Current tile-readout synthesis result:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 1556
$_DFF_PN0_: 21
$_AND_: 718
$_MUX_: 62
$_NOT_: 41
$_OR_: 276
$_XOR_: 438
```

The 21 flip-flop bits are the registered corrected value, valid bit, fallback bit, and reason code after optimization. The larger Boolean count comes from fixed-point multiply, signed add, saturation checks, residual comparison, calibration-age comparison, and reason selection.

Current integrated micro-tile controller synthesis result:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 2990
$_DFF_PN0_: 110
$_AND_: 954
$_MUX_: 757
$_NOT_: 100
$_OR_: 451
$_XOR_: 618
```

The 110 flip-flop bits include the tile readout registers plus the controller's execution path, reason code, one-bit pending state, pending tile id, last fallback tile id, fallback counter, accepted counter, residual-fallback counter, stale-calibration fallback counter, and registered `tile_health_action`. The recovery extension does not add storage. It uses the spare two-bit health action value as `probe` and adds combinational steering from `calibration_done`, `probe_request`, `probe_passed`, and `probe_failed`. The health action is now a small lifecycle: serve, recalibrate, disable, probe. Stale calibration moves the tile to recalibrate unless it is already disabled; repeated residual failure moves it to disable; a disabled tile must pass a probe before it can serve again.

Current tile-service scheduler synthesis result:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 154
$_AND_: 22
$_MUX_: 58
$_NOT_: 30
$_OR_: 34
$_XOR_: 10
```

There are no flip-flop cells in the scheduler result. That is the intended boundary. The per-tile controller owns memory: counters, last failing tile, pending readout, and health action. The scheduler is a combinational policy selector over those already-visible states. It answers a narrower question: given the state now visible, which tile action is worth spending this cycle?

Current error-budget governor synthesis result:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 353
$_AND_: 126
$_MUX_: 88
$_NOT_: 13
$_OR_: 68
$_XOR_: 58
```

There are no flip-flop cells in the governor result. That is intentional for this first version. It is a combinational decision over evidence that another runtime block would register: residual, drift age, sensitivity, and cumulative state error. The cell count is higher than the tile scheduler because the governor does arithmetic, not only selection. It estimates the next state-error spend, clamps it, and then chooses analog, digital fallback, recalibration, or disablement.

Current integrated scheduler/governor synthesis result:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 601
```

The hierarchy reports 154 cells for the scheduler, 353 cells for the governor, and 601 cells for the integrated top after optimization. There are no flip-flop cells because this is still a combinational policy object. The physical wrappers for scheduler and governor add registers when the object is sent into OpenLane.

## Failure Mode

The failure mode is treating a successful Yosys run as a finished chip. Synthesis does not prove the clock is fast enough, that reset is integrated correctly, that the control signal reaches the scheduler in time, or that the chip has enough physical area and power margin.

The next evidence step would be timing and physical implementation. The control policy is now a circuit candidate; it is not yet placed, routed, timed, or signed off.
