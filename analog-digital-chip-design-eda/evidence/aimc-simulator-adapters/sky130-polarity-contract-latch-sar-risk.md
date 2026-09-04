# Sky130 Polarity Contract Latch/SAR Risk

- status: `polarity_contract_ready_for_isolated_latch_design_not_strict`
- polarity contract: `converter_positive_input_is_negative_raw_preamp_output_diff`
- best transistor setting: `medium_iso_pair_8ua`
- best polarity-corrected output diff V: `7.932000000e-04`
- output margin target V: `5.000000000e-04`
- output margin over target x: `1.586400`
- latch half LSB 12b V: `2.197265625e-04`
- best latch kickback V: `6.578530000e-04`
- best latch kickback over half LSB x: `2.993962`
- transistor output margin over best kickback x: `1.205740`
- latch resolves ideal sample-hold: `True`
- kickback still blocks SAR contract: `True`
- accepted post-layout written: `False`

## First Principle

The transistor handoff now has a named sign: positive model value is the negative raw preamp output difference. That is enough for a schematic sign-map, but it is not enough for a converter.

A latch is allowed to decide only if it reads the signed voltage without changing the stored value too much. The existing latch evidence resolves direction, but its clock pushes charge back into the sampled nodes. That kickback is larger than the half-LSB line for a 12-bit decision.

So the next converter question is not only whether the latch output flips to rail. It is whether the latch can decide after the polarity contract while keeping the sampled value inside the error budget that the model will see.

## Evidence Join

| object | measured fact | reading |
|---|---:|---|
| transistor handoff | `7.932000000e-04` V corrected output | enough schematic margin after named polarity contract |
| latch size sweep | `6.578530000e-04` V best kickback | still `2.994x` above half-LSB |
| latch resolution | `True` | direction can resolve in the older sample-hold fixture |

## Next Circuit Target

The next circuit target is `polarity_named_isolated_latch_input`.

It must preserve:
- converter polarity contract
- both input signs
- at least 0.5 mV corrected preamp margin before latch decision
- full latch output resolution

It must reduce:
- sampled-node differential kickback from 6.578530000e-04 V to <= 2.197265625e-04 V
- at least 2.994x additional kickback reduction from the best width-only latch result

It must measure next:
- input-referred offset
- output noise RMS
- kickback after polarity-corrected transistor handoff
- decision time
- wrong-code risk at the SAR threshold

## Blockers

- `latch_kickback_above_half_lsb`
- `no_noise_measurement`
- `no_offset_statistics`
- `no_sar_bit_cycle`
- `no_extracted_layout`

## Boundary

does not prove a latch connected to the transistor handoff, does not simulate SAR bit cycling, does not measure noise or offset, and does not create accepted post-layout converter evidence
