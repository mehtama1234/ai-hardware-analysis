# Analog Compute Needs A Trust Boundary

Analog in-memory compute is useful only if the digital system can decide when the analog result is allowed to become model state.

That is the central problem.

A conductance array can multiply many inputs by many stored weights at once. That is the attractive part. But a foundation model does not consume currents. It consumes numbers that must remain meaningful after many layers, residual paths, normalizations, attention choices, and token decisions. The analog array gives a measured physical result. The digital system must decide whether that measurement is good enough to use.

The trust boundary is the place where a physical measurement becomes a digital value that the model is allowed to depend on.

## The Object

The object is not the crossbar by itself. The object is a value crossing from physics into model state:

```text
programmed conductance
-> row voltage
-> column current
-> ADC code
-> corrected digital value
-> transformer hidden state
```

Every step changes the object.

A weight number becomes device conductance. An activation code becomes voltage. A multiply becomes current. A sum becomes a column current. A current becomes an ADC code. A code becomes a corrected integer or fixed-point value. Only then can the transformer use it as part of Q, K, V, an output projection, or an MLP projection.

The trust boundary says: do not confuse any earlier form with the final value. A clean current equation is not yet a safe model value.

## Why The Boundary Exists

The constraint is that an analog accelerator produces a measured value, while the model needs a bounded value. The hardware must prove the measurement is inside the allowed boundary before the next model operation depends on it.

The boundary exists because analog compute is a measurement, not a symbolic operation.

In digital logic, a gate output is interpreted as one of two symbols after timing and noise margins are satisfied. The exact voltage is not the value. The value is the accepted symbol. Analog compute is different. The size of the voltage or current is the information, so small physical changes can become numerical error.

The array can be wrong for several different reasons:

- a programmed cell lands at the wrong conductance
- a row DAC drives a slightly wrong voltage
- a long wire drops voltage before the far cells see it
- a column ADC maps nearby currents to the same code
- a tile drifts after calibration
- one column has a stable gain or offset error
- the corrected value saturates
- a residual check says this output is outside its error budget

These are not all the same error. Some are stable and can be corrected. Some are random and must be budgeted. Some are rare and should trigger fallback. Some are small in RMS but large enough to change an attention winner or token ranking.

The trust boundary is the system's way of saying which kind happened this time.

## The Mathematical Shape

The ideal model wants:

```text
y = W x
```

The analog machine produces something closer to:

```text
adc = quantize_adc(sum_columns((G_target + delta_G) * dac(x + delta_x)) + noise)
```

Then the digital side tries to recover a usable value:

```text
centered = adc - zero_code
scaled = centered * gain
corrected = scaled + bias
```

The trust decision is a predicate over that corrected result and the health of the tile:

```text
accept = tile_enabled
      and calibration_age < max_age
      and residual_abs <= residual_budget
      and lower_bound <= corrected <= upper_bound
```

This is more important than the slogan that analog does matrix multiplication. The equation that matters to a foundation-model accelerator is not only `y = Wx`. It is:

```text
model_state_next = f(corrected_value)
```

where `corrected_value` exists only if the measured analog result passed the trust boundary.

## Placement Is Before Trust

A scheduler can decide that Q/K/V projection is a good analog candidate. That decision is useful, but it is not evidence that the current request produced a safe value.

Placement uses facts known before execution:

```text
operation class
resident weights
tile health summary
calibration age
estimated state error
attention selection risk
token choice risk
```

From those facts the control plane can choose:

```text
digital
analog
hybrid review
```

But a placement decision cannot inspect the current that has not yet been produced. It cannot know whether this ADC code saturated, whether this residual check failed, or whether this tile was disabled by a later health flag. Placement is permission to try the physical resource. Trust is permission to use the measured result.

That separation is the difference between an architecture diagram and a checkable machine.

## What Should Stay Digital

The trust boundary also explains why a transformer should not be described as simply running on analog hardware.

Dense trained projections are plausible analog candidates because their weights are fixed during inference and heavily reused:

```text
Q = X Wq
K = X Wk
V = X Wv
MLP_up = X Wup
MLP_down = H Wdown
```

These are weight-heavy operations. A resident conductance array can help if conversion, correction, and tile movement do not erase the gain.

Other operations are different:

- softmax is a range and normalization decision
- attention selection is a comparison among changing memories
- KV-cache access is addressable memory movement
- residual addition is model-state preservation
- normalization is scale control
- sampling is a discrete control decision

Those operations may interact with analog results, but they should not be handed to analog just because a nearby dot product exists. They either remain digital or need a different proof.

## The Evidence Chain

A serious AIMC foundation-model design needs evidence at five levels.

First, circuit evidence: the tile must show how conductance, voltage, current, noise, drift, DAC error, and ADC error create the measured value.

Second, correction evidence: the digital side must show that gain, bias, zero-code removal, saturation checks, and residual checks reduce the error that matters.

Third, model evidence: the system must measure hidden-state drift, attention winner changes, probability movement, token-rank changes, and accumulated bias across layers.

Fourth, control evidence: the scheduler must produce explicit path and reason bits. A request should say why it went analog, why it stayed digital, or why it entered hybrid review.

Fifth, physical-design evidence: the control logic must survive synthesis and layout checks. A Verilog idea is not yet a chip object. It becomes more real when it has gates, placement, routing, timing reports, DRC, LVS, and generated layout artifacts.

The project now has pieces of all five. The analog Python models expose physical and correction errors. The transformer partition simulator exposes model-level consequences. The RTL exposes path and reason bits. The micro-tile controller connects analog placement to readout acceptance. The no-CTS OpenLane run gives routed physical evidence for the digital controller, while leaving CTS as an honest remaining toolchain boundary.

## The Design Rule

The design rule is:

```text
Never let an analog result enter model state without an explicit trust decision.
```

The concrete design move is to make trust a visible interface, not a hidden assumption. The tile should return a corrected value and enough status bits for the controller to accept it, reject it, or send the request to a digital fallback path.

That rule has practical consequences.

The analog tile should not output only a number. It should output a number plus evidence:

```text
corrected_value
valid
fallback
reason
residual_abs
calibration_age
saturation_flag
tile_health
```

The model runtime should not record only that an operation used analog. It should record:

```text
operation
placement_reason
readout_reason
final_path
accepted_or_fallback
```

The chip controller should not collapse scheduling and acceptance into one state. It should have at least two steps:

```text
choose analog candidate
wait for measured readout
accept corrected value or fall back
```

This is why the integrated micro-tile controller matters. It turns a conceptual warning into a clocked behavior.

## The Failure Boundary

The failure mode is an accelerator claim that stops at the crossbar.

Saying that a tile computes `Wx` is not enough. The useful question is whether the value that comes out of the ADC, after correction, can be trusted by the next transformer operation. If the answer depends on calibration age, residual error, saturation, tile health, or token-rank sensitivity, those checks must be part of the design.

Another failure mode is averaging away the wrong thing. Mean numerical error can be small while a stable bias accumulates across layers. RMS score error can be small while the top attention target flips when two scores are close. A logit error can be small while the first and second token trade places. The trust boundary must therefore use model-facing evidence, not only circuit-facing error.

The first-principles claim is simple: analog compute is not trustworthy because it is analog, and it is not useless because it is imperfect. It becomes useful when the digital system measures its output, corrects what can be corrected, rejects what cannot be trusted, and records why.
