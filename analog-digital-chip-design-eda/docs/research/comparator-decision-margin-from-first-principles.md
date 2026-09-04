# Comparator Decision Margin From First Principles

This page explains what a comparator must prove before the analog frontend can be treated as a real digital readout.

The object is not an abstract number. The object is two physical nodes. One node should be slightly higher than the other. The comparator has to turn that small difference into a full digital decision before the rest of the model is allowed to use it.

## The Simple Question

The simple question is:

Does the comparator receive enough voltage difference to decide correctly after all physical disturbances are counted?

That is stricter than asking whether the sign is right. A sign can be right in a quiet measurement and still be too weak for a real clocked decision. A comparator needs margin.

Margin means the useful input difference is larger than the things that can move the decision boundary or disturb the sampled nodes.

## What A Comparator Actually Does

A comparator starts with two nearby voltages:

```text
vin_p - vin_n = small analog difference
```

It must produce a large digital result:

```text
out_p high, out_n low
or
out_p low, out_n high
```

That jump is made by positive feedback. Positive feedback is useful because a tiny starting difference can grow into a full logic-level separation. It is also dangerous because the circuit is most fragile at the start, when the difference is still small.

If offset, noise, or kickback is comparable to the input difference, the latch can grow the wrong answer.

## The Margin Equation

The useful mental model is:

```text
available input difference
  > static offset
  + random decision noise
  + sampled-node movement from kickback
  + settling error
  + mismatch not already calibrated out
```

This is not a perfect circuit equation. It is the right design rule for the proof. Every term spends the same small voltage budget. If one term grows, the allowed room for the other terms shrinks.

The current 12-bit half-LSB line is:

```text
0.2197 mV
```

The measured sample-and-hold already spends:

```text
0.0630 mV
```

That leaves about:

```text
0.1567 mV
```

for comparator offset, comparator noise, and comparator loading. The comparator target is therefore about:

```text
0.1530 mV
```

That number is small. It is why the project cannot accept vague comparator claims.

## What Existing Evidence Says

The clocked latch proxy passed when driven from ideal voltage sources at the target-edge input:

```text
input difference: about 0.153 mV
correct polarity: 2/2 cases
```

That proves a narrow fact: a simple Sky130 latch proxy can resolve the target sign when the input source is ideal.

It does not prove the real frontend, because ideal sources do not move when the latch clock kicks charge back into them.

The coupled sample-hold plus latch fixture exposed that problem:

```text
resolved correct polarity: 2/2 cases
kickback below half LSB: 0/2 cases
worst sampled differential kickback: about 12.034 mV
```

That is much larger than the half-LSB budget. The latch could decide, but it also disturbed the sampled voltage too much.

The later capacitive-isolation and balanced-frontend work then tried to protect the sampled signal from the latch. That repaired the sign path, but the extracted sense voltage became too small.

The balanced frontend gave only:

```text
minimum sense differential: 0.0150 mV
sense-to-latch target ratio: 0.098058
```

The strong and ultra frontends improved this. The current best ultra transfer is:

```text
minimum sample-to-sense transfer: 0.437908
remaining improvement to target: about 2.28x
```

So the current state is precise:

```text
ideal latch can resolve the target input
directly coupled latch disturbs the sampled node too much
isolated extracted frontend preserves sign
isolated extracted frontend is still below the latch input target
```

## Why Sign Preservation Is Not Enough

Sign preservation asks:

```text
is sense_p higher than sense_n when it should be?
```

Comparator proof asks:

```text
is sense_p higher by enough voltage that the comparator still decides correctly after offset, noise, kickback, and timing?
```

Those are different claims.

A one-microvolt sign can be correct on a printed table. It may still be useless if the comparator has ten microvolts of noise or if the latch clock injects more charge than the signal itself.

The project therefore needs both checks:

- sign check: did the frontend preserve direction?
- margin check: is the direction strong enough to survive the comparator?

The first check is now passing for the extracted frontend candidates. The second check is still open.

## What The Next Comparator Page Must Prove

The next proof should use the extracted frontend output as the comparator input, not an ideal voltage source.

It should measure five things:

| measurement | what it asks | why it matters |
|---|---|---|
| input-referred offset | where the comparator switches when the true input is swept around zero | offset moves the decision boundary |
| repeated decision spread | how much the decision varies for the same input | noise can flip small inputs |
| latch kickback | how much the clocked comparator moves the sampled or sense nodes | the reader can damage the value it reads |
| resolution time | how long the output takes to become a valid logic value | SAR conversion needs a decision before the next bit |
| wrong-polarity count | whether either sign fails near the target edge | both signs must work |

The accepted condition should be simple:

```text
both signs resolve correctly
input-referred offset plus noise stays below the remaining budget
kickback does not erase the sampled decision voltage
decision finishes within the comparison time
all measurements come from the same named circuit setup
```

## Passive Isolation Versus Active Gain

The current design fork is now clear.

A passive frontend protects the sampled node by weakening the direct path from the latch back to the sample. That helps kickback, but it can also make the useful sense voltage smaller.

An active preamp or buffer can increase the small sense voltage before the latch. That may solve the margin problem, but it costs power, area, bias current, and its own offset and noise.

So the next design should not be judged by one number. It should be judged by the full margin:

```text
larger comparator input
minus added offset
minus added noise
minus added kickback
minus added energy and delay
```

If active gain buys more margin than it costs, it is useful. If it amplifies error or burns too much energy, it is not.

## Claim Boundary

This page supports one claim:

The project now knows why the comparator proof is still open. The current extracted frontend preserves sign and improves transfer, but accepted readout evidence requires decision margin against offset, noise, kickback, and timing.

This page refuses stronger claims:

It does not prove latch resolution from the extracted frontend, does not prove comparator noise, does not prove comparator offset, does not prove SAR conversion, does not prove DRC/LVS, and does not create accepted post-layout converter evidence.

## Where This Fits In The Flow

Read this page after:

- `Sky130 Frontend Sense Efficiency Audit`
- `Sky130 Ultra Sense Frontend Candidate`
- `Sky130 Balanced Frontend Latch Decision`

Read it before:

- `Passive Frontend vs Active Preamp`
- `Converter Evidence Ladder`
- `Final Accepted Converter Gate`

The sense-efficiency audit explains why the voltage is still too small. This page explains what "large enough" means for a comparator. The next page should choose whether the project tries to win that margin passively or spends active circuit power to amplify the signal.
