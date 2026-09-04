# Sky130 Polarity-Named Isolated Latch Work Order

- status: `polarity_named_isolated_latch_work_order_ready_not_circuit_proof`
- polarity contract: `converter_positive_input_is_negative_raw_preamp_output_diff`
- best transistor setting: `medium_iso_pair_8ua`
- best polarity-corrected output diff V: `7.932000000e-04`
- output margin over target x: `1.586400`
- best existing latch kickback V: `6.578530000e-04`
- half LSB 12b V: `2.197265625e-04`
- recommended kickback target V: `1.098632813e-04`
- additional reduction to half LSB x: `2.993962`
- additional reduction to design target x: `5.987924`
- accepted post-layout written: `False`

## First Principle

The next latch cannot be judged only by whether it produces a digital one or zero. It must read the same signed analog quantity that the transistor handoff produced.

That means two things have to be true at once. First, the sign convention must remain explicit: positive model value is the negative raw preamp output difference. Second, the latch clock must not push enough charge back into the sampled nodes to change the value being judged.

The current transistor handoff has enough schematic margin. The current latch family resolves direction, but its best kickback is still above the half-LSB line. The next design is therefore an isolation problem: let the latch see the value without letting the latch clock rewrite the value.

## Candidate Moves

| move | what changes | why it might work | main risk |
|---|---|---|---|
| `source_follower_input_buffer` | the transistor handoff drives a small buffer gate; the latch reads the buffer output | the held analog node sees less clocked latch capacitance | buffer offset and bias current can eat the 0.5 mV margin |
| `sampled_internal_decision_capacitor` | copy the polarity-corrected preamp value onto a small internal capacitor, then disconnect the frontend before latch regeneration | kickback lands mostly on the internal decision node instead of the frontend sense node | the extra sampling action adds charge injection and timing error |
| `two_phase_preamp_then_latch` | first amplify the polarity-named signal, then enable the latch after the preamp output is settled | the latch sees a larger internal difference and can use smaller input devices | preamp noise, offset, and energy become part of the converter budget |
| `delayed_or_bottom_plate_latch_clock` | delay the regenerative clock edge until the sampled handoff nodes are isolated | clock feedthrough is separated from the moment when the analog value is being stored | timing can hide kickback in a later phase unless both before and after values are measured |

## Acceptance Tests

| test | requirement |
|---|---|
| `polarity_contract_preserved` | positive model value must still mean `converter_positive_input_is_negative_raw_preamp_output_diff` at the latch/SAR boundary |
| `both_signs_resolve` | positive and negative target-edge cases must both resolve to full latch output with the contracted sign |
| `kickback_hard_line` | worst sampled-node differential kickback must be <= 2.197265625e-04 V |
| `kickback_design_target` | preferred target is <= 1.098632813e-04 V, giving half-LSB slack for offset and noise |
| `margin_survives_isolation` | corrected pre-latch output must stay >= 5.000000000e-04 V for both signs after isolation is added |
| `wrong_code_proxy` | the measured sign at the SAR threshold must not flip after applying offset, noise, and kickback budgets |
| `no_strict_claim` | candidate_post_layout_written=false and accepted_post_layout_written=false until extracted same-run evidence exists |

## Next Executable Step

build a small ngspice fixture that inserts one isolation move between the polarity-corrected transistor preamp output and the clocked latch input

## Boundary

does not prove the isolated latch circuit, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
