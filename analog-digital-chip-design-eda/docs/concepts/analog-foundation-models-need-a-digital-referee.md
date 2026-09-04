# Analog Foundation Models Need A Digital Referee

An analog foundation-model accelerator needs more than analog arrays and digital glue.

It needs a digital referee.

The referee is the part of the system that decides whether a measured analog result is allowed to change the model state. It does not decide this from hope, average accuracy, or the fact that the scheduler chose an analog tile. It decides from evidence that exists after the physical computation has happened.

That evidence includes the corrected value, whether the tile was enabled, whether the ADC saturated, whether calibration is old, whether residual error is inside budget, and whether the same tile keeps failing for the same reason.

## The Object

The object is a proposed model-state update.

The analog array does not directly produce model state. It produces a physical measurement that may become model state:

```text
conductance and voltage
-> column current
-> ADC code
-> corrected digital value
-> accepted model update
```

The referee controls the final arrow.

That final arrow is the most important one. If the value is accepted, the next transformer operation depends on it. If the value is refused, a digital fallback must provide the result or the request must move to a safer path.

This is why the controller should not expose only a numeric output. It should expose a decision:

```text
corrected_value
valid_or_fallback
reason
tile_id
running counters
health action
```

The number alone is incomplete. A number without a reason code cannot tell the runtime whether the tile should keep serving, be recalibrated, or be disabled.

## The Constraint

The hard constraint is that the array can be a good choice before execution and still produce a bad result during execution.

Before execution, the scheduler can know useful facts:

```text
operation class
resident weights
tile availability
calibration age
estimated state error
cache pressure
```

These facts can say that Q/K/V projection or an MLP projection is a reasonable analog candidate.

But the scheduler has not yet seen the current. It has not yet seen the ADC code. It has not yet seen saturation. It does not know whether this request hit a damaged column, a stale correction value, or a residual larger than the model can tolerate.

So the first decision is only permission to try:

```text
try analog
```

The second decision is permission to use:

```text
accept measured analog result
```

The digital referee exists because those are different decisions.

## The Mathematical Shape

The clean mathematical target is:

```text
y = W x
```

The analog tile produces a measured code:

```text
adc_code = ADC(column_current)
```

The digital side turns that code into a candidate value:

```text
centered = adc_code - zero_code
scaled = centered * gain
corrected = scaled + bias
```

Then the referee applies a predicate:

```text
accept =
    tile_enabled
    and not saturated
    and calibration_age < max_age
    and residual_abs <= residual_budget
```

That predicate is the design. The array is only useful when this predicate lets enough work through to pay for the analog machinery.

The next layer should never see:

```text
adc_code
```

It should see either:

```text
accepted corrected value
```

or:

```text
digital fallback value
```

The important mathematical object is therefore not just a matrix multiply. It is a guarded state update:

```text
state_next =
    f(corrected_value) if accept
    f(digital_fallback_value) otherwise
```

## Why Counters Matter

A single fallback protects one operation.

Counters protect the future.

If a tile falls back once because calibration is stale, the right action is not necessarily to disable it. Old calibration evidence can often be refreshed. The better action is:

```text
recalibrate
```

If a tile repeatedly falls back because residual error remains too large after correction, the problem is different. The tile is not merely using old correction data. It is producing outputs that correction is not repairing well enough. The better action is:

```text
disable analog service
```

This is why the controller tracks reason-specific counts:

```text
fallback_count
accepted_count
residual_fallback_count
stale_fallback_count
```

The counts are not debug decoration. They are runtime evidence. They let the system distinguish a tile that is useful but stale from a tile that is persistently untrustworthy.

The health action is the first compressed policy:

```text
0: serve
1: recalibrate
2: disable
3: probe
```

That is still a small policy, but it changes the system type. The accelerator is no longer only running analog operations. It is learning whether the analog path should keep being offered.

The fourth state matters because a real tile should not be restored by hope. A disabled tile enters service again only through a controlled probe. The digital side can request the probe, observe whether it passes or fails, and then update the serving action. A recalibrating tile also needs explicit evidence before it returns: `calibration_done` is the pulse that says the correction data has been refreshed. The rule is simple: analog failure can remove permission, but only digital evidence can restore it.

## The Concrete Design Move

The concrete design move is to split the analog path into four visible decisions:

```text
placement decision
readout trust decision
tile health action
tile service scheduling
```

The placement decision answers:

```text
Should this operation try analog compute?
```

The readout trust decision answers:

```text
Did this measured value pass correction and safety checks?
```

The tile health action answers:

```text
Should this tile keep serving future analog requests?
```

The tile service scheduler answers:

```text
Given all visible tile states and the maintenance budget, should this cycle use analog, recalibrate, probe, or fall back to digital?
```

Keeping those decisions separate prevents one common mistake. A scheduler can be right that Q/K/V projection is a good analog candidate, while the readout referee is also right that this particular tile output must be refused. Those are not contradictory facts. They happen at different times and control different objects.

The current RTL makes that split visible with path bits, reason bits, counters, `tile_health_action`, and a tile-service scheduler that arbitrates four tile states under a maintenance budget.

## What The RTL Proves

The current micro-tile controller proves a narrow point.

It does not prove a production chip. It does not prove the analog array is accurate. It does not prove clock-tree signoff.

It proves that the referee rule can become hardware-visible behavior.

The Verilog test sequence checks these cases:

```text
fixed projection accepted by analog readout
residual error forces fallback
stale calibration forces fallback and requests recalibration
disabled tile forces fallback
attention score goes to hybrid review
softmax stays digital
missing resident weights stay digital
repeated residual failure disables analog service
disabled tile enters probe only by request
failed probe returns to disabled
passed probe restores service
calibration done restores service after stale-calibration repair
requested healthy tile serves
unhealthy requested tile can be replaced by a healthy spare
recalibration is chosen before probe when no tile can serve
zero maintenance budget forces digital fallback
```

The generated vector flow matters because the cases are not only handwritten Verilog. A Python model emits the expected cases as:

```text
generated_micro_tile_cases.vh
generated-micro-tile-rtl-vectors.csv
generated-micro-tile-rtl-vectors.md
```

Then the checker runs the Verilog simulation and compares the printed hardware trace against the generated CSV row by row.

This is the right shape of evidence. The analog-side assumption, the human-readable table, the RTL test vector, and the simulation output all have to agree.

## What The Physical Flow Proves

The no-CTS OpenLane run adds a different kind of evidence.

Synthesis says the referee is not only prose. It lowers to gates. The latest synthesized micro-tile controller has:

```text
Number of cells: 2990
flip-flop bits: 110
```

The no-CTS physical run says the health-action controller can pass this exploratory physical path:

```text
synthesis
floorplan
placement
routing
extraction
GDS generation
DRC
LVS
antenna checks
```

It also states what is not done:

```text
clock-tree signoff
slew cleanup
fanout cleanup
one max-capacitance violation
```

That boundary is part of the learning. A chip-design claim becomes more useful when it says exactly where the evidence stops.

## The Failure Mode

The failure mode is to call the digital side overhead.

For an analog foundation-model accelerator, the digital side is not just overhead. It is the part that turns a physical measurement into a safe model update.

Without the referee, the system has no disciplined way to answer basic questions:

- Was this analog value accepted or refused?
- Which tile produced the refused value?
- Was the problem residual error, stale calibration, saturation, or tile disablement?
- Should the tile keep serving?
- Should it be recalibrated?
- Should it be removed from analog service?
- Did the hardware trace match the analog model's expected trace?
- Did the controller survive synthesis and physical-flow checks?

The first-principles rule is simple:

```text
An analog accelerator becomes useful only when the digital system can refuse it.
```

Refusal is not pessimism. Refusal is control. It is what lets the chip use analog work where the measurement is good enough, repair the path when calibration is stale, and fall back when the physical result should not be trusted by the model.
