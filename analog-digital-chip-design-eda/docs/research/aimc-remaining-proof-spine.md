# AIMC Remaining Proof Spine

This page ties the current Sky130 circuit work back to the larger analog in-memory compute goal.

The goal is not to collect circuit demos. The goal is to decide, with evidence, whether a model operation can safely use analog hardware instead of staying digital.

The chain is:

```text
model operation
  -> simulator target
  -> analog array signal
  -> sampled voltage
  -> isolated latch decision
  -> converter code
  -> digital correction and fallback
  -> model placement decision
```

Every step moves a different object. Every step has a different way to fail. The remaining work is to prove each step without pretending that an earlier step proves a later one.

## Model Operation

The first object is the model operation, not the chip. A dense projection, MLP matmul, attention score, normalization, and logit step do not tolerate error in the same way. A small analog error may be harmless in one hidden projection and harmful near a final choice.

The model-side question is simple: can this operation accept a bounded numeric error without changing the model behavior we care about?

What remains:

- connect accepted converter numbers back into the placement decision
- rerun the model residual decision with real converter noise, timing, and energy
- keep fallback active for operations whose residual budget is too small

## Simulator Target

The simulator target says what the hardware would need to look like for analog execution to be useful. The useful output is not "analog works." The useful output is a boundary: input precision, output precision, output noise budget, residual budget, calibration assumption, and fallback rule.

The current simulator evidence points toward a stronger converter boundary than the early local tile boundary. That is why the circuit work is focused on a 10-bit input and 12-bit output style target.

What remains:

- replace ideal converter assumptions with measured circuit numbers
- rerun break-even with same-run energy, latency, area, and noise
- reject simulator settings that the physical converter cannot support

## Analog Array Signal

An analog array does not produce a normal number. It produces a physical signal.

The weight is conductance. The input is voltage. The column output is current or charge. That signal can be moved, loaded, delayed, distorted, or buried by noise.

The circuit proof asks: can the physical signal reach the converter boundary with the right sign and enough margin?

What remains:

- keep the frontend-to-latch polarity contract explicit
- avoid treating ideal gain blocks as transistor proof
- carry the measured frontend boundary into the final converter object

## Sampled Voltage

The sampled voltage is the value the converter is trying to read. It is a small stored charge difference. If the readout circuit moves that charge too much, the act of reading changes the answer.

The direct latch connection failed this test. It moved the sampled differential by about `12 mV`, far larger than the 12-bit half-LSB line.

The tiny capacitive isolation branch is the first branch that passes this narrow schematic gate:

- `0.1 fF` and `0.2 fF` coupling capacitors
- both input signs
- target edge, `2x`, and `5x` input range
- `12/12` measured and passing cases
- worst sampled-node kickback about `202 uV`
- 12-bit half-LSB about `220 uV`

That means the sampled value can survive one nominal isolated-latch read in schematic ngspice.

What remains:

- clock-timing stress
- offset stress
- noise stress
- extracted parasitic stress

## Isolated Latch Decision

A latch turns a tiny analog difference into two rail voltages. But a latch does not automatically define a digital bit.

The measured clocked-latch rails match the source polarity contract when the output is interpreted as:

```text
digital sign = outp - outn
```

That convention must now be carried everywhere.

What remains:

- stress latch clock timing while preserving `outp - outn`
- measure decision time near the smallest accepted input
- measure whether marginal inputs become metastable
- keep the sign convention in the converter payload

## Converter Code

The model does not consume latch rails. It consumes a code.

A converter proof must show how repeated decisions become a bounded digital output. A single latch decision is not a SAR ADC. It is one comparison event.

What remains:

- define the SAR comparison sequence that uses this comparator
- measure or estimate reference movement
- measure comparison time
- measure per-decision energy
- connect comparison error to output-code error
- show the result stays inside the simulator output-noise budget

## Digital Correction And Fallback

Analog hardware should not be trusted blindly. The digital side needs the raw code, zero point, gain, bias, residual estimate, residual budget, calibration age, and tile health. It then decides whether the value is safe or whether execution should fall back to digital.

The rule is:

```text
analog proposes a value
digital checks the evidence boundary
model state changes only if the check passes
```

What remains:

- feed the final converter residual into the governor fields
- keep fallback points attached to the model graph
- refuse analog execution when calibration age, residual, or tile health breaks the contract

## Layout And Extraction

Schematic ngspice is not layout proof. Layout adds parasitic capacitance, parasitic resistance, placement effects, routing asymmetry, area, and extraction risk.

The next claim upgrade must therefore use one named physical object:

- layout cell
- extracted netlist
- model include files
- simulation command
- DRC result
- LVS result
- area record

What remains:

- create or identify the isolated comparator/converter layout object
- extract the parasitics
- rerun the same latch, kickback, and timing tests on the extracted object
- keep schematic numbers out of the strict post-layout payload

## Strict Accepted Payload

The accepted payload is the gate that stops overclaiming. It must contain one same-run package: run id, physical object identity, extracted netlist, model files, simulation command, energy, latency, noise, area, sharing rule, break-even rerun, and DRC/LVS status.

The current strict preflight still rejects the candidate payload with `22` issues. That is correct. The new schematic evidence helps choose a candidate, but it must not be copied into accepted post-layout evidence.

What remains:

- fill the missing same-run extracted measurements
- pass strict preflight
- pass submission preview
- write accepted evidence only through the strict submitter

## System Decision

Only after accepted converter evidence exists can the project update the big system claim.

The final decision is not "analog is good." The final decision is: for this model operation, this analog boundary, this converter, this calibration state, this energy and latency, and this fallback rule, analog execution is allowed or refused.

## Current Honest State

The project currently has a promising schematic converter-readout branch:

```text
sampled voltage
  -> tiny capacitive latch-input isolation
  -> corrected outp-minus-outn latch decision
```

It passes nominal target-edge and range stress in schematic ngspice.

It does not yet prove:

- clock timing margin
- offset
- noise
- decision energy
- SAR conversion
- extracted layout
- DRC/LVS
- accepted post-layout converter evidence
- model-level analog placement upgrade

The next work should therefore be:

```text
clock stress
  -> offset/noise stress
  -> energy/timing measurement
  -> SAR connection
  -> extracted layout
  -> strict payload
  -> model placement rerun
```

That is how the circuit work ties back to the larger AIMC goal.
