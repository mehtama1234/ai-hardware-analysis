# Hybrid Analog Digital Accelerators Need A Control Plane

The object is not an analog array by itself. The object is a request moving through a chip that contains analog tiles, digital cores, SRAM, converters, calibration logic, and a fallback path. A foundation-model token is useful only if the whole path returns a bounded next state.

The constraint is that every useful analog step creates another control question. Which weights are resident in which tiles? Which tile is healthy enough to use today? Which phase is running: prefill or decode? How many requests can be batched without breaking latency? Is the KV cache now larger than the projection work? Is calibration fresh enough? Can the digital path correct the analog error, or should this request skip the array?

This is why a hybrid accelerator needs a control plane. The control plane is the part of the machine that chooses, schedules, checks, and sometimes refuses analog execution. It is not optional management software. It is part of the compute method.

## Why The Control Plane Exists

Analog in-memory compute makes one narrow operation physically attractive:

```text
fixed conductance weights + row voltages -> summed column currents
```

That operation is powerful when the weights are reused many times. Foundation models have many such fixed projections. But the model does not stop at current sums. The output must pass through ADCs, digital accumulation, correction, residual paths, normalization, attention, cache reads, sampling, and the next layer.

So the first-principles machine is:

```text
request -> phase classifier -> scheduler -> tile choice -> analog projection
        -> ADC -> digital accumulation -> correction -> state check
        -> digital operation or fallback -> next token state
```

The array computes. The control plane decides whether that computation should happen and whether the result should be trusted.

## The Mathematical Boundary

For each request phase, the controller needs two estimates.

First, the cost estimate:

```text
analog_path =
  DAC work
+ array work
+ ADC work
+ digital partial sums
+ correction
+ cache movement
+ calibration work due now

digital_path =
  digital projection work
+ cache movement
+ digital control work
```

Second, the state-error estimate:

```text
state_error =
  converter_error
+ conductance_error
+ drift_error_since_last_calibration
+ tile_health_penalty
+ residual_error_after_digital_correction
+ attention_or_mlp_sensitivity
```

Analog execution is allowed only when:

```text
analog_path < digital_path by enough margin
and state_error < request_error_budget
and the needed tiles are available
```

This turns architecture into a set of explicit inequalities. It is not a story about analog being faster. It is a decision rule over a concrete request.

## Concrete Design Move

The concrete design move is a request-level execution record. For every served phase, write down:

- phase: prefill, decode, or batched decode
- prompt tokens and generated tokens
- active context length
- batch size
- projection work
- KV-cache movement
- selected tiles
- tile health
- calibration age
- ADC and DAC precision
- estimated state error
- expected analog cost
- expected digital cost
- chosen path
- reason for the choice

This record makes the control plane testable. If the chip uses analog for long-context single-request decode, the record must show why cache movement and boundary cost did not dominate. If the chip refuses analog during prefill, the record must show whether the cause was tile health, stale calibration, or a missing resident weight block.

## Scheduler And Fallback

The scheduler has three jobs.

First, it finds resident weight blocks. A projection can use analog only when the needed block is already programmed or can be loaded without destroying the latency and energy gain.

Second, it assigns work to healthy tiles. A tile with high column error can still be useful for tolerant layers, small adapters, or low-priority batches. It should not silently receive a sensitive projection whose output drives many later layers.

Third, it keeps a digital fallback path. Fallback is not failure. It is the condition that makes the analog path honest. If the state-error estimate is too high, if calibration is stale, or if the cache dominates the step, digital execution is the correct path.

## Measurement

The measurement is a trace, not a single speedup number.

For a small workload suite, measure:

- percent of projection work sent to analog
- percent of requests kept digital
- analog energy saved after ADC, DAC, accumulation, correction, and calibration are counted
- p95 latency by phase
- state error after correction
- fallback rate by cause
- tile-health distribution
- calibration work per generated token

A useful result might say: prefill uses analog often, batched decode uses analog when tile health is good, long-context single-request decode stays digital, and unhealthy tiles are bypassed until recalibration. That is a stronger claim than one average accelerator speedup because it explains where the hardware is actually being used.

## Failure Mode

The failure mode is to draw analog and digital blocks without the decision logic between them. A block diagram can make the system look complete while hiding the most important question: who decides that this request should enter the array now?

Another failure mode is to treat fallback as an admission that analog failed. In a real hybrid machine, fallback is part of correctness. It protects the model state when the physical array is not the right tool for the current request.

The first-principles claim is simple: analog arrays are compute resources, not universal replacement engines. Foundation-model hardware becomes credible when the chip can prove when analog is used, when it is refused, what error was expected, and what measurement made the decision defensible.
