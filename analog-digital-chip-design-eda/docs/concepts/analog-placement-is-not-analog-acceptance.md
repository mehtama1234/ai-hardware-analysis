# Analog Placement Is Not Analog Acceptance

The object is a two-step hardware decision. First the system decides whether an operation is allowed to try analog compute. Then, after the analog tile has been measured, the system decides whether the measured result is allowed to enter model state.

Those are not the same decision.

Analog placement answers:

```text
Should this operation run on the analog path?
```

Analog acceptance answers:

```text
Is this particular measured result trustworthy enough to use?
```

The distinction matters because analog compute is a physical measurement. A conductance array can be the right place for a dense projection and still produce a bad output on a particular request. The tile may be disabled. Calibration may be stale. A column may have drifted. The ADC code may saturate. A residual check may say the corrected value is outside the budget.

## The Constraint

The constraint is that permission to use a resource is weaker than evidence that the resource worked.

A scheduler can inspect stable facts before execution:

```text
operation class
resident weights
tile health
calibration age
estimated state error
attention selection risk
token choice risk
```

From those facts it can say:

```text
digital
analog
hybrid
```

But this still happens before the tile has produced the current, before the ADC has returned a code, and before correction has checked the result. The placement decision can only say that analog is worth attempting.

The acceptance decision needs later evidence:

```text
ADC code
zero code
gain correction
bias correction
residual magnitude
residual budget
saturation check
calibration age at readout
tile enable state
```

This is why a serious hybrid accelerator needs at least two control boundaries. One boundary chooses where the operation should execute. A later boundary checks whether the result can be used.

## The Mathematical Shape

A placement rule is a predicate over the request and tile state:

```text
place_analog = fixed_weight_operation
             and resident_weights
             and state_error <= state_error_budget
             and attention_flip_rate <= attention_flip_budget
             and token_flip_rate <= token_flip_budget
             and not stale_weak_tile_state
```

That predicate does not contain the actual measured output. It cannot, because the output does not exist yet.

The acceptance rule is a predicate over the measured value:

```text
centered = adc_code - zero_code
scaled = centered * gain
corrected = scaled + bias

accept = tile_enabled
      and residual_abs <= residual_budget
      and calibration_age < max_calibration_age
      and lower_bound <= corrected <= upper_bound
```

Only the second rule protects the model from this tile's actual measured behavior. The first rule protects the model from choosing obviously wrong work. The second rule protects the model from using an analog result that failed after the work was attempted.

## The Concrete Design Move

The concrete design move is to encode placement and acceptance as separate hardware events.

In the current RTL, `aimc_operation_partition` chooses:

```text
digital
analog
hybrid
```

It does this from operation class, resident weights, model-error budget, attention-risk budget, token-risk budget, calibration age, and weak-tile count.

The `aimc_tile_readout` block then checks the measured tile output:

```text
ADC code -> zero removal -> gain correction -> bias correction -> clamp -> valid or fallback
```

The `aimc_micro_tile_controller` composes the two:

```text
analog placement -> start readout
next cycle valid readout -> accept corrected analog value
next cycle failed readout -> digital fallback
```

The one-cycle wait is the important hardware fact. The controller cannot honestly accept analog on the same conceptual step where it merely chose analog. It must wait for the measurement boundary.

## Measurement

The measurement is a trace that includes both decisions:

```text
operation, placement, readout_result, final_execution_path, reason
```

A useful test must include at least these cases:

- fixed Q/K/V projection is allowed to try analog and accepted after valid readout
- fixed projection is allowed to try analog but falls back when residual is too high
- fixed projection is allowed by operation class but falls back when the tile is disabled
- attention score work goes to hybrid review instead of direct analog acceptance
- softmax stays digital before any tile readout is attempted
- missing resident weights force digital before any analog work begins

The current integrated RTL test has exactly that shape:

```text
qkv_analog_readout_accepted,path=1,reason=1,value=32
qkv_residual_forces_fallback,path=0,reason=10,value=32
qkv_disabled_tile_fallback,path=0,reason=9,value=32
attention_score_hybrid_review,path=2,reason=2,value=32
softmax_partition_digital,path=0,reason=0,value=32
missing_weights_partition_digital,path=0,reason=3,value=32
```

The physical-flow evidence also matters. The integrated controller has been synthesized and run through a no-CTS OpenLane flow. That does not prove clock-tree signoff, but it does show that this two-step decision can become placed and routed digital logic with GDS, LEF, Liberty, SDF, and SPICE outputs.

## Failure Mode

The failure mode is saying "the model uses analog for Q/K/V" as if that single sentence is a hardware guarantee. It is only a routing intention. The measured tile output can still be unsafe.

Another failure mode is hiding acceptance inside software prose. If a chip depends on fallback, then fallback must have an object: a residual threshold, calibration age, saturation check, tile enable bit, reason code, and clocked decision point.

The first-principles claim is simple: analog placement is permission to try a physical resource. Analog acceptance is evidence that the measured result survived the physical boundary. A hybrid foundation-model accelerator needs both.
