# Sky130 Balanced Frontend Sense-Gain Target

- status: `sense_gain_target_ready_before_latch_rerun`
- minimum sense-to-latch-input ratio: `0.098058`
- required sense gain improvement: `10.20x`
- target sample-to-sense transfer ratio: `1.000000`
- current minimum sample-to-sense transfer ratio: `0.098058`
- accepted ready now: `False`

## First Principle

The balanced frontend fixed the direction problem. It did not yet fix the size problem. A latch cannot make a reliable digital decision from a sign that is present but too small.

The sample voltage difference is the thing we want to preserve. The sense-node voltage difference is what the latch actually receives. The useful design number is therefore simple: how much of the sample difference reaches the sense nodes before the latch is asked to decide.

The current extracted starter sends only about one tenth of the needed latch input. The next physical frontend must increase sample-to-sense transfer while keeping the two sides matched. That means larger intentional coupling, smaller wasted sense-node capacitance, or a preamp/buffer. Each choice has a cost: more kickback, more offset, more power, or more area.

## Design Target

| quantity | value | meaning |
|---|---:|---|
| current minimum sense signal | `1.500000000e-05 V` | smallest extracted sense difference across the four passing sign cases |
| latch proxy input target | `1.529705854e-04 V` | input size used by the earlier passing latch proxy |
| required gain improvement | `10.20x` | multiplier needed before rerunning latch from extracted sense nodes |
| sense capacitance delta | `0.000000 fF` | balance is good; the problem is transfer size, not first-order mismatch |

## Allowed Next Designs

- increase mirrored sample_p-to-sense_p and sample_n-to-sense_n coupling while keeping extracted sense_p and sense_n totals matched
- reduce non-signal capacitance on sense_p and sense_n so less sampled charge is wasted on clock, supply, ground, and substrate paths
- add a small differential preamp or source-follower buffer only if its offset, noise, and input capacitance are measured separately
- rerun extracted sign preservation after every physical edit before trying the latch again

## Acceptance Checks

- minimum sample-to-sense transfer ratio reaches the latch proxy target or a new bounded latch proof resolves from the smaller input
- both input signs preserve sign after extraction
- sense_p and sense_n total capacitance remain matched within the starter extraction balance rule
- sample-node kickback remains below the hard half-LSB comparator boundary
- accepted evidence remains false until latch resolution, offset/noise, DRC, and LVS are all available for the same physical candidate

## Refused Claim

does not modify layout, does not prove latch resolution, does not prove offset or noise, does not run DRC/LVS, and does not write accepted post-layout evidence
