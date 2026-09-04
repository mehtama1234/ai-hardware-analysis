# Digital Control Logic Makes Analog Compute Checkable

The object is a hardware decision that must happen at a clock edge. An analog foundation-model accelerator can have useful arrays, but the chip still needs digital logic to decide which request enters those arrays and which request stays on the digital path.

The constraint is that the decision cannot remain a paragraph in an architecture note. It must become a stable symbolic output. A scheduler, firmware loop, or RTL controller must encode the same facts the architecture depends on: request phase, batch size, context length, resident weights, tile health, calibration age, expected error, and fallback reason.

## Why Digital Control Is Needed

Analog compute produces approximate values. Digital control chooses when those approximate values are allowed to affect model state.

The important separation is:

```text
analog array: produces current sums
digital control: decides whether those sums are used
```

If the control decision is vague, the whole accelerator claim becomes vague. A paper can say analog helps prefill, but the chip must decide whether this request is prefill, whether the needed weights are resident, whether enough tiles are healthy, and whether the estimated error is below the allowed bound.

## The Concrete State

The control logic does not need the whole model in hardware. It needs a compact state description:

```text
phase_decode
batch_size
active_context
resident_weights
healthy_tiles
weak_tiles
calibration_age
estimated_error
error_budget
```

From that state it can produce:

```text
path = digital | analog | analog_batched_decode
reason = ok | missing_weights | too_few_tiles | error_high
       | stale_calibration | cache_dominates | batch_reuse
```

This is a concrete design move because it converts a system argument into a testable interface. The output can be checked in a testbench. Later it can be synthesized, timed, and connected to firmware or a larger scheduler.

## Priority Matters

The decision order is part of the design.

The controller should first reject unsafe or impossible analog work:

```text
missing resident weights
too few healthy tiles
estimated state error too high
stale calibration with weak tiles
```

Only after those checks should it choose a performance path:

```text
long-context single-request decode -> digital
batched decode -> analog batched decode
otherwise -> analog
```

This ordering prevents a common mistake. A system can have a batch large enough to amortize converters, but still be wrong to use analog if the tile state is unhealthy. Correctness checks must come before speed checks.

## Measurement

The measurement is a simulation trace:

```text
case, path, reason, expected_path, expected_reason
```

A good testbench should include at least these cases:

- prompt batch with healthy resident tiles chooses analog
- batched decode chooses the batched analog path
- long-context single-request decode falls back because cache movement dominates
- stale calibration with weak tiles falls back
- estimated error above budget falls back
- missing resident weights falls back

The measurement is small, but it changes the character of the project. The analog/digital boundary is no longer only a concept. It has a digital decision circuit that can be run and checked.

## Failure Mode

The failure mode is claiming an adaptive hybrid accelerator without implementing the adaptation. If the chip should sometimes use analog and sometimes use digital, there must be a visible decision object somewhere. Otherwise the architecture hides the most important part of the method.

Another failure mode is placing performance checks before safety checks. That can make the controller choose analog because batch reuse is high even when calibration is stale or error is above budget.

The first-principles claim is that digital control logic is what makes analog compute checkable. It turns physical approximation into a bounded system decision.
