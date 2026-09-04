# Analog-To-Digital-To-Model Error Flow

This page explains how a physical readout error becomes a model decision.

The converter does not produce a model value directly. It produces a code. The digital system must turn that code into a corrected value, compare the remaining error against a budget, and decide whether the model is allowed to use it.

The flow is:

```text
analog voltage error
  -> ADC code error
  -> corrected digital value error
  -> residual
  -> layer or state error
  -> accept or fallback
```

## The Simple Question

The simple question is:

When the converter is imperfect, does the error stay small enough for this model operation?

That question cannot be answered by the converter alone. A converter can be electrically imperfect but still good enough for a tolerant layer. It can also look electrically reasonable and still be too risky near a fragile model decision.

## An ADC Code Is Not A Model Value

The analog array produces a physical result: current, charge, or voltage. The ADC turns that result into a code.

That raw code is not yet the number the model expects.

The code still contains:

- zero offset
- gain error
- bias error
- quantization error
- noise
- saturation
- drift since calibration

That is why the digital trust boundary does not simply forward `adc_code`.

It first forms:

```text
centered_adc = adc_code - zero_code
scaled = centered_adc * gain
corrected_value = scaled + bias
```

Then it checks whether the remaining error is small enough:

```text
residual_abs <= residual_budget
```

Only then can the value enter model state.

## What Residual Means

Residual is the part of the error that remains after known correction.

If a column is always shifted by the same amount, calibration can measure that shift and the digital side can subtract it. If a column has a stable gain error, calibration can measure the scale and the digital side can correct it.

After that correction, some error remains. That remaining error is the residual.

In simple terms:

```text
raw error = the whole difference from ideal
corrected error = what remains after zero, gain, and bias repair
residual = the corrected error the model still has to tolerate
```

Residual matters more than raw error because the model receives the corrected value, not the raw ADC code.

## Why The Same Circuit Error Can Matter Differently

The same voltage or code error does not have the same model meaning everywhere.

A hidden projection may tolerate small residuals because later operations mix, normalize, or partially cancel the error.

A close attention score may be fragile because a small score movement can change which token receives weight.

A final logit can be fragile because a small change can alter the selected token.

A residual stream can carry repeated bias forward across many layers.

That is why the placement decision cannot say "MatMul always goes analog." It must ask whether this operation, in this location, with this residual, is safe enough.

## Where AIHWKIT And CrossSim Fit

AIHWKIT and CrossSim do not prove the Sky130 converter. They estimate how analog-array errors affect a model-shaped computation.

Their useful role is:

```text
given this analog error model
and this model subgraph
how large is the residual?
```

That residual can feed the governor only if the payload is accepted by the strict importer. A simulator run that finishes but exceeds the residual threshold is still useful evidence, but it cannot support positive analog placement.

That is the current split:

- CrossSim calibrated payloads can support selected fixed-weight MatMul analog service in the current fixtures.
- AIHWKIT calibrated payloads ran, but the current residuals are too high for positive analog permission in those same larger fixtures.

The reason is not brand preference. The reason is the residual boundary.

## Where Sky130 Converter Evidence Fits

Sky130 converter evidence asks a different question:

```text
can the physical readout produce a trustworthy code?
```

The frontend and comparator pages are working on the path from sampled voltage to digital decision. That path must eventually produce measured converter values:

- output noise
- input-referred noise
- offset
- settling time
- conversion time
- energy
- area
- sharing rule

Once those values exist, they must feed back into the simulator and placement logic. Otherwise the model-side decision would still be based on old assumptions.

## The Digital Governor's Job

The digital governor is the point where model safety becomes hardware behavior.

It receives a measurement packet:

```text
adc_code
zero_code
gain
bias
residual_abs
residual_budget
calibration_age
tile_enabled
```

It returns:

```text
corrected_value
output_valid
fallback
reason
```

That means analog placement and analog acceptance are separate.

Placement says:

```text
this operation is allowed to try analog
```

Acceptance says:

```text
this measured analog result is safe to use now
```

If acceptance fails, the digital path must supply the value.

## Why Fallback Is Part Of The Design

Fallback is not an apology. It is how the system protects model state.

A tile can be structurally suitable and still be refused for this cycle because:

- residual is too high
- calibration is stale
- the tile is disabled
- the corrected value saturates
- the converter did not produce a valid code
- the operation is more sensitive than expected

The model should not receive a value just because the analog path was attempted. It should receive the value only when the trust boundary says the measurement passed.

## The Full Error Path

The full path is:

```text
1. model graph names an operation
2. placement marks it analog-candidate or digital-only
3. analog simulator estimates residual for matching operation families
4. physical converter evidence supplies real noise, offset, timing, energy, and area
5. digital correction maps ADC code to corrected value
6. governor compares residual against the operation budget
7. accepted values enter model state
8. refused values trigger digital fallback
9. placement and break-even are updated with the measured evidence
```

This is the point of the combined repo. It is not only circuit design and not only model simulation. It is the chain between them.

## What Must Be True Before The Claim Upgrades

The claim can upgrade only when all three layers agree:

| layer | required evidence | why |
|---|---|---|
| circuit | extracted or measured converter values for noise, offset, timing, energy, area, and sharing | the readout must produce a trustworthy code |
| model | residual stays inside the operation budget for the actual model object | the model must tolerate the remaining error |
| system | break-even and placement rerun with the same measured converter values | the analog path must still be worth using |

If any layer is missing, the correct result is needs-review or fallback.

## Claim Boundary

This page supports one claim:

The project now has a clear explanation of how converter error becomes model residual and why the digital governor must accept or refuse each measured analog result.

This page refuses stronger claims:

It does not prove the Sky130 converter, does not prove full-model accuracy, does not prove measured silicon, does not prove board latency or power, does not rerun placement with accepted post-layout converter values, and does not create accepted post-layout converter evidence.

## Where This Fits In The Flow

Read this page after:

- `Converter Evidence Ladder`
- `Mixed-Signal Trust Boundary Spec`
- `Residual-Aware Placement Decisions`

Read it before:

- `Final Accepted Converter Gate`

The converter ladder explains what evidence is strong enough. This page explains how that evidence changes the model decision.
