# Mixed-Signal Trust Boundary Spec

This spec defines the interface between an analog in-memory compute tile and the digital controller that decides whether a foundation-model value can be used.

The object is the readout boundary. Before the boundary, the result is physical: row voltage, conductance, column current, and ADC code. After the boundary, the result is digital model state or a digital fallback request.

The constraint is that a transformer layer cannot trust a value only because the scheduler chose an analog tile. It can trust the value only after the measured readout has been corrected and checked.

## Boundary Contract

The analog side does not hand the model a value. It hands the digital controller a measurement packet:

```text
sample_valid
tile_id
tile_enabled
adc_code
zero_code
gain_q6
bias
residual_abs
residual_budget
calibration_age
```

The digital side returns a trust decision:

```text
corrected_value
output_valid
fallback
reason
last_fallback_tile_id
fallback_count
accepted_count
residual_fallback_count
stale_fallback_count
tile_health_action
```

That is the minimum contract for the current project. It is not a production mixed-signal interface yet. It is the smallest interface that makes the trust boundary explicit enough to simulate, synthesize, and place.

The concept article `Analog Foundation Models Need A Digital Referee` explains the system role of this packet: the analog tile proposes a measured value, and the digital side accepts it, refuses it, asks for recalibration, or removes the tile from analog service.

## Input Fields

`sample_valid` says a measured ADC sample is present for this cycle. Without it, the controller should not update the trust decision.

`tile_id` says which physical tile produced the measurement. It must be latched when the analog read starts, because the request bus may move on before the next-cycle accept-or-fallback decision is made.

`tile_enabled` says the tile is allowed to serve model traffic. A disabled tile must not produce accepted model state even if its ADC code looks reasonable.

`adc_code` is the raw output code from the converter. It is not a model value. It is the measurement that starts the digital trust decision.

`zero_code` is the converter or tile code corresponding to zero input or zero current. Removing it turns a raw code into a centered code.

`gain_q6` is the measured scale correction. In the current RTL it is a signed fixed-point gain with six fractional bits.

`bias` is the measured offset correction. It repairs stable output shift after centering and gain correction.

`residual_abs` is the remaining error estimate after correction. It represents the part of the analog output that calibration did not explain.

`residual_budget` is the maximum residual this layer or operation is willing to accept.

`calibration_age` says how long the tile has run since the correction values were refreshed. Old correction data is treated as weaker evidence.

## Output Fields

`corrected_value` is the centered, scaled, biased, and clamped digital value. This value is allowed to enter model state only when `output_valid` is true.

`output_valid` means the measured analog result passed the trust boundary.

`fallback` means the measured analog result should be refused and the digital path should provide the projection.

`reason` records why the decision was made. A reason code is not decoration. It is how debugging, runtime policy, calibration, and later EDA tests know which boundary failed.

`last_fallback_tile_id` records the most recent tile whose measured readout was refused by the integrated controller.

`fallback_count` records how many analog readout attempts have fallen back since reset. In the current RTL it is a saturating counter, not a full histogram.

`accepted_count` records how many analog readout attempts have been accepted since reset. It is the matching numerator for understanding whether the analog path is mostly useful or mostly being refused.

`residual_fallback_count` records readout refusals caused by residual error after correction. This counter points to tiles whose analog behavior is not being repaired well enough by the current correction values.

`stale_fallback_count` records readout refusals caused by old calibration evidence. This counter points to tiles that may become useful again after recalibration.

`tile_health_action` is the first hardware-visible runtime policy bitfield. In the current controller, `0` means keep serving the tile, `1` means recalibrate before trusting it again, `2` means disable the tile from analog service, and `3` means run a controlled probe. This is a registered action, not a live combinational summary. Readout evidence can move a serving tile toward recalibration or disablement. Recovery evidence can move it back: `calibration_done` returns a recalibrating tile to service, while `probe_request`, `probe_passed`, and `probe_failed` let a disabled tile enter a narrow probe path and return to service only after the probe passes. A stale-calibration fallback asks for recalibration. Repeated residual fallbacks ask for disablement, because the tile is failing after correction rather than merely running on old correction data.

## Current RTL Mapping

The current Verilog module `aimc_tile_readout` implements this contract directly.

Implemented input fields:

- `sample_valid`
- `tile_enabled`
- `adc_code`
- `zero_code`
- `gain_q6`
- `bias`
- `residual_abs`
- `residual_budget`
- `calibration_age`
- `calibration_done`
- `probe_request`
- `probe_passed`
- `probe_failed`

Implemented output fields:

- `corrected_value`
- `output_valid`
- `fallback`
- `reason`

The integrated controller also implements the first accounting fields around the readout block:

- `tile_id`
- `last_fallback_tile_id`
- `fallback_count`
- `accepted_count`
- `residual_fallback_count`
- `stale_fallback_count`
- `tile_health_action`

Implemented reason cases:

```text
0: ok
1: tile_disabled
2: residual_high
3: calibration_stale
4: saturated_high
5: saturated_low
```

Integrated controller health actions:

```text
0: serve
1: recalibrate
2: disable
```

The concrete design move is that correction and refusal are in clocked hardware, not only in prose. The readout block first forms:

```text
centered_adc = adc_code - zero_code
scaled = centered_adc * gain_q6
corrected = scaled >> 6 + bias
```

Then it checks:

```text
tile_enabled
residual_abs <= residual_budget
calibration_age < max_calibration_age
corrected inside signed output range
```

If those checks pass, `output_valid` is asserted. If any check fails, `fallback` is asserted and `reason` names the failed boundary.

## Controller Mapping

The current `aimc_micro_tile_controller` composes operation placement with readout trust.

The operation partition block decides whether the operation should be:

```text
digital
analog
hybrid
```

The readout block decides whether an analog result should be:

```text
accepted
refused
```

The controller waits one cycle after analog placement before accepting the readout result. That wait matters. It prevents a false design where analog placement and analog acceptance are treated as one decision.

Current execution paths:

```text
0: digital
1: analog accepted
2: hybrid review
```

The current `aimc_tile_service_scheduler` sits one level above that controller. It does not inspect ADC codes. It inspects already-visible tile actions:

```text
0: serve
1: recalibrate
2: disable
3: probe
```

It chooses one system action for the cycle:

```text
0: digital fallback
1: analog service
2: recalibration
3: probe
```

The priority is intentionally plain. Serve the requested healthy tile. If that tile cannot serve, use a healthy spare. If no tile can serve and maintenance budget exists, recalibrate before probing. If there is no budget or every useful tile is disabled or busy, fall back to digital. The scheduler is not a hidden second health model. It is a budgeted dispatcher over health states produced elsewhere.

The current fallback reason is formed by combining the controller-level fallback marker with the readout reason. That makes the final path explain both levels:

```text
operation was allowed to try analog
readout boundary refused the measured result
```

## What Is Still Missing

The current interface is enough for the learning project, but several production-facing fields are still missing.

Missing analog-quality fields:

- ADC overflow before correction
- ADC underflow before correction
- converter ready or timeout
- row-driver settled flag
- temperature or voltage-domain warning
- per-column health rank
- tile or bank identifier

Missing model-facing fields:

- operation identifier
- layer identifier
- tensor block identifier
- state-error budget selected by the runtime
- attention-rank risk selected by the runtime
- token-rank risk selected by the runtime

Missing accounting fields:

- calibration samples consumed
- time since last full calibration sweep
- full reason histogram for runtime policy

These are not optional if the design becomes a larger accelerator. Without identifiers and counters, the system cannot learn which tiles are weak, which layers are fragile, or which request phases should stop using analog.

## Why This Interface Is The Right First Object

This boundary is narrow enough to build and rich enough to teach the real issue.

It avoids a fake analog claim. The array is not treated as a magic matrix unit. Its output has to pass through ADC, correction, residual checking, age checking, saturation checking, and fallback.

It avoids a fake digital claim. The digital controller does not pretend to know the result before the analog measurement exists. It waits for the readout boundary and then decides.

It gives EDA something real to lower. The trust decision is Boolean and arithmetic logic with registers, comparators, adders, multipliers, muxes, and reason bits. That is why the project can synthesize it and run it through OpenLane as a digital control object.

## Evidence Required

The boundary is correct only if several tests keep passing.

Simulation evidence:

- accepted readout produces `output_valid`
- disabled tile produces fallback
- high residual produces fallback
- stale calibration produces fallback
- high and low saturation clamp the value and produce fallback
- analog placement waits for readout before reporting analog accepted

Synthesis evidence:

- the readout block lowers to gates
- the integrated controller lowers to gates
- no unintended memories or unsynthesizable processes remain
- signed correction arithmetic has stable width handling

Physical-flow evidence:

- the integrated controller can be placed and routed
- generated GDS, LEF, Liberty, SDF, and SPICE artifacts exist
- DRC and LVS are clean for the completed no-CTS flow
- CTS remains tracked as a separate unresolved toolchain boundary

Model evidence:

- the transformer-layer trust trace records per-operation accept/fallback
- the error-budget ledger shows which error source moves hidden state
- fallback reduces final hidden-state error when the worst projections are refused

Runtime telemetry evidence:

- accepted and fallback counters are tracked by tile
- residual fallback and stale-calibration fallback are separated
- mostly accepted tiles remain in service
- stale tiles are recalibrated before being trusted again
- repeated residual-failure tiles are removed from the primary analog path

The first-principles claim is that this interface is where analog compute becomes a system. Before it, there is a physical measurement. After it, there is either a bounded model value or a digital fallback.
