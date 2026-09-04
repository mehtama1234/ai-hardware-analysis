# Sky130 Extracted Frontend Redesign Target

- status: `redesign_required_before_post_layout_acceptance`
- measured wrong-sign bias mV: `11.039000`
- target differential signal mV: `0.152971`
- bias-to-signal ratio: `72.16`
- required bias reduction factor: `144.33`
- accepted ready now: `False`

## First Principle

A comparator is only useful after its input nodes carry the thing we want to compare. The latch input must first be a balanced measuring node, then it can become a decision node. If the layout moves both latch inputs in one preferred direction, the latch is no longer measuring the sampled voltage difference. It is mostly reading the layout's own imbalance.

The extracted frontend failed in that exact way. The negative input case should make `gp - gn` negative, but the extracted cell made it positive by about 11 mV. The actual target signal is only about 0.153 mV. That means the unwanted physical bias is roughly 72 times larger than the signal we are trying to preserve.

Adding more ideal sample-to-gate capacitance did not fix both signs. That tells us the next move is not a small sizing patch. The front end needs a different physical handoff: balanced latch-gate loading, controlled common-mode reset, symmetric shielding, and a separated sampling phase before regeneration.

## Concrete Redesign Target

| target | value | reason |
|---|---:|---|
| maximum wrong-sign gate bias before latch fire | `0.076485 mV` | leaves half of the target signal as usable sign margin |
| required reduction from current extracted bias | `144.33x` | current wrong-sign bias is much larger than the target differential signal |
| minimum sign cases | `2` | both positive and negative target-edge inputs must preserve sign |
| accepted extracted evidence | `same extracted physical cell passes both-polarity sign preservation, kickback, offset/noise, DRC, and LVS` | the same physical cell must pass extraction, rerun, DRC/LVS, and offset/noise record |

## Required Topology Changes

- make each latch-gate input see the same total capacitance to clock, supply, ground, substrate, and sample nodes
- add a reset or precharge phase that forces both latch-gate inputs to the same common-mode before the sampled signal is handed off
- shield or distance the latch-gate nodes so clock and supply movement cannot create a one-direction gate difference larger than the sampled signal
- separate the sampling phase from the regenerative latch phase so the latch cannot push charge back into the held sample while the sign is being formed
- rerun the extracted physical cell after layout, not an ideal overlay, before any accepted evidence is written

## Refused Claim

does not claim a working comparator, does not modify layout, does not replace DRC/LVS, and does not prove accepted post-layout converter evidence
