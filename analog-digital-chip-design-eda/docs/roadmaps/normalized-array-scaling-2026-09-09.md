# Model-derived array scaling

The selected GPT-2 profile now has a model-specific electrical scaling map.
Under an ideal linear differential-array assumption with a common conductance
span and DAC full scale, the 144 tiles require a **9.6758:1 relative gain span**.
The equivalent fixed-gain option requires ADC references from **10.3351% to
100%** of a shared maximum reference. These are derived ratios, not demonstrated
circuit capabilities or assigned voltages.

Use `evidence/aimc-hardware-lab/calibrated-array-scaling/20260909-v2/`.
Version v1 is superseded: v2 includes exact DAC codes and an analytic bound for
both input and weight code-to-float rounding.

## Exact model binding

The checkpoint tensor `h.0.mlp.c_fc.weight` corresponds to runtime module
`transformer.h.0.mlp.c_fc`. Its file hash matches the held-out evaluation.
All 2,359,296 exported signed int8 weight codes reproduce the frozen float32
quantized weights exactly when decoded with the original quantizer arithmetic.
All 144 table entries also match the controller descriptor coordinates, bounds
and frozen-plan hash.

The weight profile specifies 255 signed codes, −127 through +127. Its assumed
differential representation requires 128 levels per branch:

```text
G_plus  = G_base + G_span * max(weight_code, 0) / 127
G_minus = G_base + G_span * max(-weight_code, 0) / 127
V_row   = V_drive_full_scale * DAC_code / 511
```

This is a requirement on a prospective device implementation. No device has
been shown to deliver those levels or cancel the shared baseline conductance.
Signed row drive, virtual-ground columns and differential subtraction are
also unqualified assumptions.

## Gain and reference choices

Let `A_eff = 511 * frozen_DAC_step`, `W_eff,t = 127 * frozen_weight_step,t`,
and `B_t` be the frozen calibrated partial-sum bound. Then:

```text
k_t = A_eff * W_eff,t / B_t
R_unit = V_ADC_full_scale / (V_drive_full_scale * G_span)
R_t = R_unit * k_t
```

The dimensionless multiplier `k_t` ranges from 0.680515 to 6.584518. The unknown
common factor `R_unit` prevents assigning an absolute transimpedance.
Alternatively, at fixed `R = R_unit * min(k)`, the normalized reference is
`V_ref,t / V_ref,max = min(k) / k_t`.

Conductance span/baseline, absolute drive/reference voltages and resistance
values remain null. Gain/reference code precision, noise, linearity, switching,
settling and controller implementation still need evaluation. The earlier
17–49× reduction from conservative ADC bounds is a different quantity from this
9.6758:1 inter-tile gain span; the latter accounts for each tile's weight scale.

## Verification scope

There were 576 numerical probe cases: four quantized training vectors per tile.
The largest code-level reconstruction difference was 1.05e−7 model units.
An analytic bound over all allowed DAC-code vectors is at most 5.83e−6 per tile
partial, below the declared 1e−5 rounding-check limit.

The bound compares real-valued products of equispaced codes with mathematical
dot products of the frozen float32 quantized operands. It excludes FP32 GEMM
accumulation, physical noise, wire/device effects, converter quantization and
saturation. It does not prove an analog operating range or whole-model physical
accuracy.

Verification checked five artifact hashes, every exported weight code, all
144 ratios and all per-tile analytic bounds. Four negative checks rejected
inverted gain/reference ratios, changed weight codes, understated error bounds
and unsupported physical authorization. The 144 entries were also checked
against the controller package.

From the EDA project:

```bash
python3 scripts/check_calibrated_array_scaling.py evidence/aimc-hardware-lab/calibrated-array-scaling/20260909-v2
```

The derivation script accepts the held-out package, its pinned safetensors
checkpoint and a new output directory. Source hashes and numerical-library
versions are recorded in the result.

The next implementation choice is a realizable gain or reference mechanism
with finite setting precision, followed by a matched physical noise/settling
profile. Digital fallback remains the only authorized execution route.

The [switched-reference follow-up](switched-reference-dac-checkpoint-2026-09-09.md)
now characterizes three nominal SKY130-switch DAC variants and freezes finite
reference codes for all 144 tiles. It exposes up to 1.51591% bound changes and
144 uncharacterized bank code transitions; model and physical qualification
remain open.
