# Lab: AIMC Control Plane RTL

This lab turns the analog in-memory foundation-model scheduler into digital logic. The point is not to build a production chip controller. The point is to make the control decision explicit enough that it can be simulated, synthesized, and checked.

## Workflow Contract

Consumes: analog/model-impact governor request rows, tile health fields, calibration age, residual budgets, operation placement, and scheduler pressure.

Produces: Verilog decisions, reason codes, generated test cases, checked RTL traces, fallback counters, and synthesis-ready controller blocks.

Supports: the claim that the analog-use rule is not only prose. It is encoded as clocked logic and checked against generated cases from the lab evidence.

Refuses: physical timing, routed layout, power, board behavior, analog macro behavior, and production controller signoff.

Handoff: this lab sends checked controller logic to the synthesis and EDA labs, and its trace results are summarized by the hardware-lab evidence exporter.

## Where This Lands In The Combined Workbench

This lab is the decision-rule part of the larger AIMC workflow.

```text
analog residual and model sensitivity
  -> governor request rows
  -> Verilog decision
  -> checked reason code
  -> synthesis candidate
  -> evidence export
  -> backend claim readiness
```

The important object is not an analog multiply. The important object is the permission to let an analog value affect model state. The RTL receives small fields, not prose: analog candidate bit, residual budget, attention flip risk, token flip risk, sensitivity class, tile health, calibration age, and scheduler pressure.

The current backend claim effect is bounded. A passing RTL checker strengthens the local runtime/control-path evidence inside `board_runtime.json`, but it does not make `C2` a measured board-latency claim. It shows that the refusal rule can be encoded and checked. Measured latency still requires a board or instrumented runtime trace tied to the same package and workload.

## Object

The object being controlled is the execution path for one model request phase.

The controller receives a compact description of the request and tile pool:

- phase: prefill or decode
- batch size
- active context length
- resident weight status
- healthy tile count
- weak tile count
- calibration age
- estimated state error

It returns one of three paths:

- analog projection path
- analog batched-decode path
- digital fallback path

The companion `aimc_operation_partition` module controls a smaller object: the placement of one transformer operation. It separates fixed trained projections, changing attention memory, logits, cache movement, normalization, sampling, and fallback.

The `aimc_tile_readout` module controls the next lower boundary. It receives one analog tile readout after ADC conversion, applies digital gain and bias correction, clamps unsafe values, and decides whether the corrected output can be used or must fall back.

The `aimc_micro_tile_controller` module composes those two decisions. It asks whether the current transformer operation is allowed to use analog compute, starts a tile readout only for analog fixed-weight work, waits one cycle for the corrected result, and then accepts the analog value or falls back to digital.

The `aimc_tile_service_scheduler` module adds the next runtime layer. The micro-tile controller says what one tile is allowed to do now: serve, recalibrate, disable, or probe. The scheduler looks across four tiles, a requested tile id, busy bits, and a maintenance budget. It then chooses the least risky useful action: serve the requested healthy tile, serve a spare healthy tile, spend maintenance budget on recalibration, spend maintenance budget on probe, or fall back to digital. This keeps analog service from becoming a local yes/no decision with no system budget.

The `aimc_error_budget_governor` module adds a different runtime layer. It does not choose a tile. It decides whether another analog result is worth spending at all. It reads local residual, calibration age, model-path sensitivity, and cumulative state error. It permits analog service only when the next estimated error remains inside the model-state budget. A high residual disables the tile path, old calibration requests recalibration, a sensitive path can force digital even for moderate residual, and a nearly spent state budget can stop analog service before the next token makes the error worse.

The `aimc_scheduler_governor` module composes the two runtime decisions. The scheduler says which tile action is available. The governor says whether analog error can be spent. The final path is analog only when both conditions are true. Scheduler maintenance decisions still pass through, because recalibration and probe are the mechanisms that make future analog service possible.

The `aimc_scheduler_governor_pipelined` module keeps that same policy but adds a timing boundary. It registers the request, tile state, and governor evidence, computes the same integrated policy from that registered stage, and registers the final decision. The point is not a new policy. The point is to stop pretending that a large policy expression has no clock cost. A faster chip needs a stage boundary that timing tools can see.

It also records the first accounting signals needed for runtime learning: which tile most recently failed readout, how many readout fallbacks have happened since reset, how many analog readouts have been accepted, and how many refusals came from residual error versus stale calibration.

## Constraint

The analog path is allowed only when the chip has enough resident and healthy analog resources, the estimated model-state error is below the request budget, and the request shape is not dominated by cache movement or stale calibration.

The constraint is not only logical correctness. The decision must be stable at a clock edge, encoded into a small number of bits, and easy to check in a testbench.

## Concrete Design Move

The Verilog module implements a priority decision:

```text
missing resident weights -> digital fallback
too few healthy tiles -> digital fallback
estimated state error too high -> digital fallback
stale calibration with weak tiles -> digital fallback
single-request long-context decode -> digital fallback
batched decode -> analog batched decode
otherwise -> analog
```

The ordering matters. A chip should not claim batched analog decode if the tile state is already unsafe. Safety and availability checks come before performance choices.

The operation-partition module implements the second decision:

```text
embedding, mask, softmax, residual, norm, KV cache, sampling -> digital
Q/K/V, attention output, MLP -> analog when resident and healthy
attention scores, value mixing, logits, adapters -> hybrid when measured evidence is inside budget
state error, attention selection flips, token flips, stale weak tiles, or missing weights -> digital fallback
```

This mirrors the transformer partition simulator in the analog lab. The simulator estimates the error. This RTL encodes the decision rule that would use that estimate.

The tile-readout module implements the third decision:

```text
ADC code - calibrated zero -> centered analog result
centered result * gain -> scaled digital result
scaled result + bias -> corrected value
residual too high, stale calibration, disabled tile, or saturation -> fallback
otherwise -> valid corrected output
```

This is the boundary that makes analog compute checkable. The array is not trusted because it produced a current. It is trusted only when the digital side can show that the measured output is inside the correction and residual budget.

The micro-tile controller implements the fourth decision:

```text
operation partition says digital -> use digital
operation partition says hybrid -> send to hybrid review
operation partition says analog -> sample tile readout
tile readout valid next cycle -> accept corrected analog value
tile readout fallback next cycle -> force digital fallback
readout fallback -> record tile id and increment fallback counter
valid readout -> increment accepted counter
residual-high readout fallback -> increment residual fallback counter
stale-calibration readout fallback -> increment stale fallback counter
```

The one-cycle wait is not incidental. It is the hardware form of the claim that analog output must be measured and checked before the scheduler lets it affect model state.

The matching first-principles article is `docs/concepts/analog-placement-is-not-analog-acceptance.md`.

The follow-on article is `docs/concepts/analog-foundation-models-need-a-digital-referee.md`. It explains why the controller should not only schedule analog work, but also judge whether the measured analog result is allowed to become model state.

## Run

```bash
iverilog -o aimc_control_plane_tb aimc_control_plane.v aimc_control_plane_tb.v
vvp aimc_control_plane_tb
```

Run the operation partition testbench:

```bash
iverilog -o aimc_operation_partition_tb aimc_operation_partition.v aimc_operation_partition_tb.v
vvp aimc_operation_partition_tb
```

Run the tile readout testbench:

```bash
iverilog -o aimc_tile_readout_tb aimc_tile_readout.v aimc_tile_readout_tb.v
vvp aimc_tile_readout_tb
```

Run the integrated micro-tile controller testbench:

```bash
python3 check_generated_micro_tile_trace.py
```

Run the generated tile-service scheduler trace:

```bash
python3 check_generated_scheduler_trace.py
```

Run the generated error-budget governor trace:

```bash
python3 check_generated_error_budget_governor_trace.py
```

Run the generated model-impact governor trace:

```bash
python3 check_generated_model_impact_governor_trace.py
```

Run the generated integrated scheduler/governor trace:

```bash
python3 check_generated_integrated_scheduler_governor_trace.py
```

Run the generated pipelined scheduler/governor trace:

```bash
python3 check_generated_pipelined_scheduler_governor_trace.py
```

Optional waveform:

```bash
gtkwave aimc_control_plane.vcd
```

## Measurement

The measurement is the decision trace printed by the testbench. Each case states the request condition, expected path, actual path, and reason code.

The generated-trace checker adds one more gate: the Verilog output must match the CSV emitted by the analog vector generator. The useful output is:

```text
PASS generated_micro_tile_trace
cases 8
```

The useful questions are:

- Does a prompt batch choose analog when tiles are healthy?
- Does batched decode choose the batched analog path?
- Does long-context single-request decode fall back to digital?
- Does stale calibration with weak tiles fall back before the model state is damaged?
- Does a missing resident weight block force digital fallback?
- Are fixed trained projections assigned to analog?
- Do attention-score and logits operations remain hybrid unless their selection metrics exceed budget?
- Do cache, normalization, softmax, and sampling remain digital?
- Does the tile readout correct gain and bias before exposing a value?
- Does it refuse disabled, stale, high-residual, and saturated outputs?
- Does the integrated controller wait for readout evidence before accepting analog output?
- Does the error-budget governor reject analog work when local residual, calibration age, sensitive model paths, or accumulated state error make the next analog use too expensive?
- Does the integrated scheduler/governor block analog service unless a tile can serve and the next analog error remains inside the model-state budget?

Current tile-readout simulation result:

```text
centered_adc_with_unit_gain,value=32,valid=1,fallback=0,reason=0
gain_and_bias_correction,value=43,valid=1,fallback=0,reason=0
disabled_tile_fallback,value=32,valid=0,fallback=1,reason=1
residual_fallback,value=32,valid=0,fallback=1,reason=2
stale_calibration_fallback,value=32,valid=0,fallback=1,reason=3
high_saturation_fallback,value=2047,valid=0,fallback=1,reason=4
low_saturation_fallback,value=-2048,valid=0,fallback=1,reason=5
PASS aimc_tile_readout_tb
```

Current micro-tile controller simulation result:

```text
qkv_analog_readout_accepted,path=1,reason=1,value=32,last_fallback_tile=0,fallback_count=0,accepted_count=1,residual_fallback_count=0,stale_fallback_count=0,tile_health_action=0
qkv_residual_forces_fallback,path=0,reason=10,value=32,last_fallback_tile=12,fallback_count=1,accepted_count=1,residual_fallback_count=1,stale_fallback_count=0,tile_health_action=0
qkv_stale_calibration_fallback,path=0,reason=11,value=32,last_fallback_tile=17,fallback_count=2,accepted_count=1,residual_fallback_count=1,stale_fallback_count=1,tile_health_action=1
qkv_disabled_tile_fallback,path=0,reason=9,value=32,last_fallback_tile=13,fallback_count=3,accepted_count=1,residual_fallback_count=1,stale_fallback_count=1,tile_health_action=1
attention_score_hybrid_review,path=2,reason=2,value=32,last_fallback_tile=13,fallback_count=3,accepted_count=1,residual_fallback_count=1,stale_fallback_count=1,tile_health_action=1
softmax_partition_digital,path=0,reason=0,value=32,last_fallback_tile=13,fallback_count=3,accepted_count=1,residual_fallback_count=1,stale_fallback_count=1,tile_health_action=1
missing_weights_partition_digital,path=0,reason=3,value=32,last_fallback_tile=13,fallback_count=3,accepted_count=1,residual_fallback_count=1,stale_fallback_count=1,tile_health_action=1
second_residual_disables_tile,path=0,reason=10,value=32,last_fallback_tile=18,fallback_count=4,accepted_count=1,residual_fallback_count=2,stale_fallback_count=1,tile_health_action=2
maintenance_disabled_enters_probe,path=0,reason=10,value=32,last_fallback_tile=18,fallback_count=4,accepted_count=1,residual_fallback_count=2,stale_fallback_count=1,tile_health_action=3
maintenance_probe_failed_disables,path=0,reason=10,value=32,last_fallback_tile=18,fallback_count=4,accepted_count=1,residual_fallback_count=2,stale_fallback_count=1,tile_health_action=2
maintenance_disabled_enters_probe_again,path=0,reason=10,value=32,last_fallback_tile=18,fallback_count=4,accepted_count=1,residual_fallback_count=2,stale_fallback_count=1,tile_health_action=3
maintenance_probe_passed_serves,path=0,reason=10,value=32,last_fallback_tile=18,fallback_count=4,accepted_count=1,residual_fallback_count=2,stale_fallback_count=1,tile_health_action=0
post_probe_stale_recalibrates,path=0,reason=11,value=32,last_fallback_tile=19,fallback_count=5,accepted_count=1,residual_fallback_count=2,stale_fallback_count=2,tile_health_action=1
maintenance_calibration_done_serves,path=0,reason=11,value=32,last_fallback_tile=19,fallback_count=5,accepted_count=1,residual_fallback_count=2,stale_fallback_count=2,tile_health_action=0
PASS aimc_micro_tile_controller_tb
```

Current generated tile-service scheduler simulation excerpt:

```text
token_17_requested_tile_serves,tile_actions=0013,busy=0000,budget=0,decision=1,selected_tile=1,reason=2
token_18_recalibrate_before_probe,tile_actions=0213,busy=1100,budget=1,decision=2,selected_tile=2,reason=4
token_19_probe_disabled_tile,tile_actions=0203,busy=1110,budget=1,decision=3,selected_tile=3,reason=5
token_23_all_tiles_unusable_or_busy,tile_actions=0202,busy=1111,budget=1,decision=0,selected_tile=3,reason=7
token_24_requested_tile_serves,tile_actions=0202,busy=0000,budget=1,decision=1,selected_tile=0,reason=2
PASS aimc_tile_service_scheduler_tb
```

Current generated error-budget governor simulation result:

```text
PASS generated_error_budget_governor_trace
cases 32
```

Current generated model-impact governor simulation result:

```text
PASS generated_model_impact_governor_trace
cases 5
```

These five cases are not synthetic threshold examples. They come from the measured tile transformer-impact report. The analog lab first measures how the selected tile residual affects fixed projections, stressed projections, attention scores, and logits. Then `model_impact_governor_requests.py` compresses that model behavior into `residual_q8`, `sensitivity_q8`, and `cumulative_error_q8`. This checker proves the Verilog governor makes the same accept/refuse decision from those compressed fields.

Current integrated scheduler/governor simulation result:

```text
PASS generated_integrated_scheduler_governor_trace
cases 36
```

Current pipelined scheduler/governor simulation result:

```text
PASS generated_pipelined_scheduler_governor_trace
cases 36
```

The pipelined version is checked against the same generated CSV rows as the combinational integrated block. The expected decision is identical; only the hardware timing boundary changes. The testbench drives one case, waits for the registered input stage and registered output stage, and then compares the final decision, selected tile, reason code, and next cumulative error.

Current pipelined scheduler/governor synthesis result:

```text
aimc_scheduler_governor_pipelined: 184 cells, 92 flip-flops
integrated hierarchy total: 689 cells, 92 flip-flops
```

The extra storage is the cost of making the policy a timed object. The earlier pure integrated policy synthesized as a combinational object. That was useful for checking meaning, but it did not create a clocked boundary. The corrected pipelined block adds a middle register between the child scheduler/governor outputs and final arbitration, so the physical flow can time the child policy and the final decision as separate stages.

## Failure Mode

The failure mode is treating the scheduler as prose around the accelerator. If the chip needs a serving policy, that policy must eventually become logic, firmware, or both. A block diagram is not enough. The decision must be encoded, simulated, and checked against the same first-principles constraints used in the architecture article.

The second failure mode is treating every transformer operation as the same kind of arithmetic. The operation partition prevents that. It does not allow the analog array to own masks, softmax, cache addressing, normalization, or token sampling simply because those operations sit near matrix multiplies in the model graph.

The third failure mode is treating ADC output as model output. It is not. It is a measurement that must pass through offset removal, gain correction, bias correction, saturation checks, residual checks, and calibration-age checks before the digital system lets it affect the model state.

The fourth failure mode is accepting analog output in the same conceptual step as choosing analog placement. Placement is permission to try the tile. It is not permission to use the tile result. The readout boundary must still accept or reject the measured value.

The fifth failure mode is treating error budget as a single threshold. The governor separates four reasons to refuse analog service: the local projection residual is too high, calibration is too old, the model path is sensitive, or the cumulative model-state budget has already been spent. Those are different faults and should not be hidden behind one vague safe/unsafe bit.

The sixth failure mode is letting either runtime block pretend to be the whole system. The scheduler can find an available tile that the governor should still reject. The governor can approve an error spend when no tile is actually serviceable. The integrated block is the first hardware object that makes both statements true at the same time.

The seventh failure mode is treating pipelining as a performance label. A pipeline only means something when the same policy is checked after the added latency and the extra registers show up in synthesis. Otherwise it is only a diagram. The pipelined scheduler/governor test and synthesis report make the cost visible.

The higher-level concept page `Analog Compute Needs A Trust Boundary` explains why this RTL split is the core system rule. The controller is not only routing work. It is protecting model state from measured analog outputs that fail correction, residual, saturation, calibration, or tile-health checks.

The research page `Mixed-Signal Trust Boundary Spec` names the interface implemented by `aimc_tile_readout`: raw ADC code, zero correction, gain, bias, residual, calibration age, tile enable, corrected value, valid/fallback bits, and reason code. The RTL is intentionally small, but it now has a clear contract to grow against.

The latest controller extension adds `tile_id`, `last_fallback_tile_id`, `fallback_count`, `accepted_count`, `residual_fallback_count`, `stale_fallback_count`, and registered `tile_health_action`. It also adds four recovery controls: `calibration_done`, `probe_request`, `probe_passed`, and `probe_failed`. This is not a full monitor yet. It is the first hardware-visible accounting and policy hook: when an analog readout fails, the controller remembers which tile failed and increments a fallback counter; when readout succeeds, it increments an accepted counter; when the failure reason is residual or stale calibration, it increments the matching reason counter. One stale-calibration fallback moves the tile to recalibrate. Repeated residual fallback moves it to disable, because correction is no longer making the tile trustworthy. A disabled tile can move only into probe, and it returns to service only after an explicit probe pass. A recalibrating tile returns to service only after an explicit calibration-done pulse.

The micro-tile controller cases are generated by the analog lab script `generate_micro_tile_rtl_vectors.py` into `generated_micro_tile_cases.vh`. The `check_generated_micro_tile_trace.py` script regenerates those vectors, runs the Verilog simulation, and compares the simulation trace against the generated CSV row by row. That keeps the Python trace and the Verilog testbench tied to the same sequence: fixed-weight analog acceptance, residual fallback, stale-calibration fallback, disabled-tile fallback, hybrid attention review, digital softmax, missing weights, and repeated residual failure that disables analog service. The manually written maintenance cases then prove the other side of the lifecycle: disabled to probe, failed probe back to disabled, passed probe back to service, stale fallback to recalibrate, and calibration done back to service.

The tile-service scheduler is intentionally combinational. It does not remember tile history; the tile controllers already own that evidence. Its job is to arbitrate the visible health states. That separation matters. If the scheduler also invented health, then recovery would become a second hidden policy. Here the scheduler only spends the evidence it is given.

The analog lab script `multi_tile_scheduler_runtime.py` runs the same policy idea over a token stream and writes `multi-tile-scheduler-runtime.csv`, `multi-tile-scheduler-runtime.md`, and `generated_tile_scheduler_cases.vh`. The `check_generated_scheduler_trace.py` script regenerates those files, runs the Verilog scheduler testbench, parses the hardware trace, and compares every token row against the CSV. That trace shows why the scheduler exists: individual tile health actions become a sequence of service, recalibration, probe, and digital fallback decisions under a maintenance budget.
