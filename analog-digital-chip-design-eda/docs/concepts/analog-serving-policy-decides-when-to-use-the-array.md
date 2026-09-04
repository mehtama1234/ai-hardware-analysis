# Analog Serving Policy Decides When To Use The Array

The object is a request running through a shared accelerator. A chip can contain analog tiles and still choose not to use them for every token. Hardware is useful only when it matches the runtime shape of the work.

Foundation-model serving has different regimes. A long prompt gives many tokens at once. One-token decode gives little work per step. Batched decode gives more work but may add scheduling delay. Long context grows the KV cache. Calibration and health probes spend measurement time. The constraint is that the serving policy must choose the cheapest correct path for each phase.

The decision is not:

```text
analog accelerator exists -> use analog
```

The decision is:

```text
if reuse and error budget are high enough, use analog
if boundary cost or cache pressure dominates, stay digital
```

## Why Policy Matters

Analog in-memory compute has fixed costs around each use. Inputs must be converted by DACs. Column currents must be read by ADCs. Partial sums must be accumulated. Output correction must be applied. Tiles must be scheduled. Calibration may be due.

These costs can be worth paying for prefill because many prompt tokens reuse the same projection weights. They may be too expensive for single-token decode with small batch. Batched decode can make analog attractive again, but only if batching delay is acceptable.

So the analog array is not a universal engine. It is a resource that should be dispatched when the request has enough dense repeated work.

## The Mathematical Boundary

For a phase, define:

```text
analog_total = analog_projection + converter + accumulation + correction + calibration_due + cache_cost
digital_total = digital_projection + cache_cost
```

Then the policy can compute:

```text
speed_or_energy_ratio = analog_total / digital_total
```

Use analog only when:

```text
speed_or_energy_ratio < target_ratio
and estimated_error < error_budget
and tile_health is acceptable
```

The RTL scheduler makes the last line more precise. A tile is not simply good or bad. It can be serving, waiting for recalibration, disabled, or waiting for probe. The serving policy therefore has two jobs. First, it should use a healthy requested tile when it can. Second, when the requested tile is not usable, it should decide whether a spare healthy tile is available or whether the cycle should be spent on maintenance instead of analog service.

The same request can make different choices by phase:

```text
prefill: analog
decode: digital
batched_decode: analog if batch is large enough
long_context_decode: maybe digital because KV cache dominates
```

## Concrete Design Move

The concrete design move is to make serving decisions explicit:

- prompt length
- generated length
- batch size
- active attention window
- ADC and DAC precision
- calibration overhead due now
- tile health score
- expected state error
- analog versus digital cost
- chosen execution path
- selected tile
- service decision
- maintenance budget

This turns a hardware claim into a runtime controller. The accelerator does not only contain arrays. It contains a policy that says when the arrays are worth using.

## Measurement

The measurement is a decision table:

```text
phase, prompt_tokens, generated_tokens, batch, context, analog_ratio, cache_ratio, decision
```

The table should reveal four cases:

- prefill is usually analog-friendly because reuse is high
- single-token decode can be digital-friendly because boundary cost is exposed
- batched decode can become analog-friendly if latency budget allows batching
- long-context decode can be cache-limited even if projections are cheap

The policy should also show when it refuses analog because calibration is overdue or tile health is poor.

The new `aimc_tile_service_scheduler` RTL is the smallest version of that policy. It looks at four visible tile-health actions, tile busy bits, the requested tile id, and the maintenance budget. It emits one decision: digital fallback, analog service, recalibration, or probe. It does not invent health. It only spends the health evidence produced by the lower tile controller.

## Failure Mode

The failure mode is to report one accelerator speedup as if all requests have the same shape. A chat request with a short prompt and long decode is not the same as batch prompt processing. A retrieval-augmented request with long context is not the same as a short interactive completion.

The first-principles claim is that hybrid analog/digital foundation-model hardware needs a serving policy. The array should be used when it saves more than it costs and when the model can tolerate the error. Otherwise the digital path is the correct path, even on a chip that contains analog compute.
