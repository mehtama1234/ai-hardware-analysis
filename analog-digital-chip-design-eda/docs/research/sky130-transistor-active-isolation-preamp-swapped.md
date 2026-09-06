# Sky130 Transistor Active-Isolation Preamp With Explicit Polarity

The first transistor active-isolation run had adequate corrected amplitude in
two settings but the output polarity was inverted relative to the declared
preamp contract. This rerun explicitly swaps the two isolation outputs at the
preamp inputs instead of hiding the inversion in the evaluator.

The generated evidence is
`evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-swapped.json`.

| result | value |
|---|---:|
| transient cases measured | `6/6` |
| settings passing both signs | `2/3` |
| smallest passing corrected output | `0.6242 mV` |
| best corrected output margin | `0.7932 mV` |
| best setting | `medium_iso_pair_8ua` |

The passing settings use the extracted frontend netlist, a Sky130 transistor
differential isolation pair, a Sky130 transistor preamp, and measured
zero-input offset subtraction. This clears the schematic handoff experiment:
the transistor stage can preserve both input signs while exceeding the current
`0.5 mV` preamp-margin target.

The first physical-cell handoff is now also runnable. Magic extracts
`layout-workbench/cells/sky130_transistor_active_isolation_pair.mag` into the
two-device subcircuit used by the runner. The corrected mirrored routing has
no extracted source/drain short, and the extracted run measures `6/6` cases
with `2/2` polarity decisions for every setting. Its best corrected output is
`0.2383 mV`, however, below the `0.5 mV` margin target. The layout therefore
preserves sign but fails the amplitude handoff; the next revision must reduce
extracted loading or increase effective isolation/preamp gain.

The extracted result is recorded in
`evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-extracted-swapped-v4.json`.

An external-bias probe increased the isolation load to `300 kOhm` at `4 uA`.
It preserved both signs but produced only `0.2015 mV`. Increasing the second
preamp load to `300 kOhm` collapsed its operating point to approximately zero
differential output. These controls reject resistor-only gain tuning; the
next physical revision must reduce the isolation cell's parasitic loading or
change its transistor topology/bias while retaining the symmetric source and
drain connectivity.

The compact physical revision then reduced the extracted diffusion width to
`1.2 um` and used the `560 kOhm / 4 uA` isolation operating point. The full
extracted handoff measured both polarities and passed the current corrected
margin on both sides: `-0.5091 mV` and `+0.5168 mV`. Its evidence is
`evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-compact3-560k4ua.json`.
This closes the extracted frontend-to-preamp amplitude experiment, but not
the converter: PVT, mismatch/noise, latch kickback, SAR cycling, and full
layout signoff are still required.

This is not yet an accepted converter. The isolation pair still needs a drawn
layout optimization and a passing extracted margin, DRC/LVS, process/temperature/supply coverage, mismatch
and noise trials, latch kickback testing, and integration into the physical
SAR sequence. Offset subtraction here is a diagnostic calibration, not a
statistical production calibration.

## Corner Boundary

The compact extracted cell was also run at two operating extremes using the
same `560 kOhm / 4 uA` point. The `ss / -20 C / 1.62 V` case preserved both
signs and passed the margin (`0.5114..0.5185 mV`). The `ff / 85 C / 1.98 V`
case also converged and preserved both signs, but its margin fell to
`0.4750..0.4875 mV`. This is a useful PVT boundary: the handoff is not yet
robust enough for analog enablement, and the next work is corner-aware bias or
gain design followed by mismatch/noise and latch testing.

A `650 kOhm` corner-specific isolation load was tested at that fast/hot/high
corner. It preserved both signs, but only the positive side crossed the target
(`+0.5009 mV` versus `-0.4881 mV`). Increasing the load alone is therefore
not a robust PVT repair; it creates a directional margin imbalance.

## Deterministic Mismatch Probe

The extracted runner now supports an equal-and-opposite isolation-load
mismatch perturbation. At nominal conditions, the `+/-2%` probe passes both
signs and margin with corrected outputs of `-0.7942 mV` and `+0.8552 mV`; the
measured zero-input offset is approximately `60.1 mV`. A `+/-5%` probe also
passes, with `-0.7569 mV` and `+0.8763 mV`, while the zero-input offset grows
to approximately `130.0 mV`.

These are deterministic sensitivity probes of the extracted handoff, not a
Monte Carlo mismatch or noise-yield result. They establish that zero-input
offset must be measured and corrected per operating instance, and that the
remaining acceptance work is statistical device mismatch, noise, latch
kickback, and SAR wrong-code testing.

## Connected Latch Boundary

The extracted isolation pair and preamp were then connected to the transistor
latch through
`labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_extracted_isolation_preamp_frontend.spice`.
The latch test uses a `1 um` input pair and `4 um` tail, and checks both input
signs at the declared `1.8 V / 4096 / 2` sampled-node kickback limit.

Artifact: `evidence/aimc-simulator-adapters/sky130-extracted-balanced-isolation-preamp-latch-kickback-v9.json`.
All three simulations (negative, zero, and positive input) completed and
sampled-node kickback was zero in this ideal transient setup. The raw latch
output was positive for both signal signs (`1/2` raw polarity decisions),
with a zero-input baseline of approximately `+0.99656 V`. Subtracting that
baseline gives only `-27 uV/+27 uV` at the latch output. The calibrated signs
are therefore directionally correct, but the latch does not resolve the
required decision amplitude.

This leaves a concrete integration blocker: implement physical offset
cancellation or more extracted preamp gain before claiming a connected analog
decision stage. The test does not claim latch, SAR, mismatch/noise, or
converter acceptance.

A controlled sensitivity sweep on the calibrated two-stage handoff bounds the
required improvement. At `10x` the declared target differential, only `1/2`
polarity decisions passed; at `50x`, both passed with approximately
`-1.7965 V/+1.7981 V` latch separation; and at `100x`, both also passed.
This is a diagnostic gain requirement, not permission to scale the input in
the converter: the physical design must create comparable differential drive
or reduce the effective input-referred offset at the nominal target edge.
The `50x` and `100x` artifacts are
`sky130-two-stage-preamp-latch-handoff-scale50.json` and
`sky130-two-stage-preamp-latch-handoff-scale100.json`.

The lower-loading preamp input pair (`pre_w=4 um`) closes the deterministic
three-corner handoff with the compact `1.2 um` isolation cell and `560 kOhm /
4 uA` isolation bias. Both polarities pass the corrected `0.5 mV` margin in
all cases:

| corner | corrected output range |
|---|---:|
| `tt / 27 C / 1.8 V` | `0.8077..0.8124 mV` |
| `ss / -20 C / 1.62 V` | `0.8150..0.8612 mV` |
| `ff / 85 C / 1.98 V` | `0.7230..0.7299 mV` |

The three artifacts are `sky130-transistor-active-isolation-preamp-compact3-tt-pre4.json`,
`sky130-transistor-active-isolation-preamp-compact3-ss-pre4.json`, and
`sky130-transistor-active-isolation-preamp-compact3-ff-pre4.json`. This closes deterministic corner
margin for the handoff, not statistical mismatch/noise, latch, SAR, or
converter acceptance.
