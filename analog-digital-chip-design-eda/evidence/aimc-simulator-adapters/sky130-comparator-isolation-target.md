# Sky130 Comparator Isolation Target

This page turns the latch kickback failure into the next circuit target. It does not claim a new circuit works. It says how much isolation the next circuit must add before the sampled-node result can support a 12-bit decision.

- status: `sky130_comparator_isolation_target_defined_not_circuit_proof`
- baseline coupled kickback V: `1.203400000e-02`
- best tested input width um: `0.5`
- best measured kickback V: `6.578530000e-04`
- half LSB 12b V: `2.197265625e-04`
- observed width reduction x: `18.293`
- additional reduction needed to reach half LSB x: `2.994`
- recommended additional reduction for half-LSB margin x: `5.988`
- recommended kickback target V: `1.098632813e-04`
- candidate post-layout written: `False`
- accepted post-layout written: `False`

## First Principle

The sampled capacitor stores the decision voltage as charge. The latch should read that charge, but its input devices also connect capacitance to fast clocked internal nodes. When those internal nodes move, some charge returns to the sampled nodes. That is kickback.

The width sweep showed the direction clearly. Smaller latch input devices reduce kickback because they reduce the capacitance coupled to the sampled nodes. But the best tested width still moved the differential sampled voltage by more than the half-LSB line. This means sizing alone is not enough. The next circuit needs an isolation mechanism.

The hard line is 2.197265625e-04 V. The best measured width still has 6.578530000e-04 V of kickback, so the next circuit needs at least 2.994x more reduction. A practical target is half the half-LSB line, 1.098632813e-04 V, which needs about 5.988x more reduction from the best tested width.

## Candidate Isolation Moves

| move | purpose | risk |
|---|---|---|
| `source_follower_or_preamp_buffer` | make the sampled capacitor drive a small gate instead of the latch input pair directly | adds offset, gain error, bias current, bandwidth limits, and its own input capacitance |
| `sampled_comparator_input_capacitor` | copy the held voltage onto a small internal decision capacitor before the latch clock moves | adds a second sampling error and needs careful clock order |
| `bottom_plate_or_delayed_latch_clock` | separate sampling switch turn-off from the latch regenerative edge | can reduce one kickback path while increasing another if timing is wrong |
| `tiny_input_pair_plus_preamplification` | keep latch input capacitance low while restoring enough signal before regeneration | the preamp may spend more energy and introduce input-referred offset |

## Next Acceptance Tests

| test | requirement |
|---|---|
| `kickback_margin` | worst sampled differential kickback <= 1.098632813e-04 V target and must be below 2.197265625e-04 V hard line |
| `resolution_preserved` | both positive and negative target-edge cases still resolve with correct polarity |
| `budget_connection` | target-edge input difference remains tied to 0.1530 mV, with 0.1567 mV as the hard comparator budget |
| `no_post_layout_claim` | candidate_post_layout_written=false and accepted_post_layout_written=false |

## Refused Claim

does not prove an isolated comparator, comparator noise, mismatch, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
