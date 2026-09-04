# Passive Frontend Vs Active Preamp

This page explains the next design choice for the Sky130 analog readout path.

The project has a small differential signal that reaches the sense nodes with the correct sign. The signal is still not strong enough for accepted comparator evidence. The current best extracted transfer is `0.437908`; the target before latch proof is `1.0`.

The design now has two honest paths:

```text
make the passive frontend waste less signal
or
add active gain before the latch
```

Both can be right. They solve different physical problems and they create different evidence burdens.

## The Simple Question

The simple question is:

Should the circuit protect the tiny signal, or should it amplify the tiny signal?

A passive frontend tries to protect the signal. It uses layout, capacitance, matching, and isolation. It does not add bias current. It tries to move charge from the sampled node to the sense node without letting the latch push too much charge back.

An active preamp tries to amplify the signal. It uses transistors and bias current. It takes a small sense-node voltage and makes a larger voltage before the latch decides.

The choice is not about which one sounds more advanced. The choice is about which one creates more decision margin after its own costs are counted.

## What The Passive Path Means

The passive path says:

```text
do not add an amplifier yet
make the physical handoff cleaner
```

The useful object is charge. The sampled voltage difference stores a small charge difference. The frontend moves part of that charge onto the sense nodes. The comparator reads the sense-node voltage.

The passive design wins when:

```text
useful coupling goes up
wasted sense capacitance goes down
kickback path stays weak
matching stays symmetric
```

The recent evidence shows why this is hard. The ultra frontend increased direct sample-to-sense capacitance to `0.8 fF`, but the average sense-node capacitance also rose to `3.292970 fF`. The measured transfer improved to `0.437908`, but it did not reach `1.0`.

That means making everything larger is not enough. The next passive design must be more selective. It must keep the useful coupling while removing capacitance that does not carry signal.

## What The Active Path Means

The active path says:

```text
accept that the passive sense voltage is small
use transistor gain before the latch
```

A preamp can make the latch's job easier. If the sense node gives only part of the needed input voltage, a preamp can enlarge that difference before positive feedback starts.

But active gain is not free. A preamp adds:

- input capacitance
- static or switched bias current
- input-referred offset
- input-referred noise
- finite settling time
- output swing limits
- possible stability problems
- more area
- more layout matching burden

So the active path is useful only if the gained voltage is larger than the new errors it introduces.

The right test is:

```text
preamp output margin
  > preamp offset
  + preamp noise
  + added kickback
  + settling error
```

If that inequality passes, active gain bought real margin. If it fails, the preamp only made the circuit look more complex.

## Why This Choice Exists

The earlier direct-coupled latch showed one extreme. The latch resolved the sign, but it kicked the sampled nodes by about `12.034 mV`, far above the `0.2197 mV` half-LSB line.

That taught one lesson:

```text
the latch cannot be allowed to freely disturb the sampled value
```

The later isolated frontends showed the other extreme. They protected the sign path, but reduced the signal seen by the latch.

That taught the second lesson:

```text
isolation that protects too much can starve the comparator
```

The design is now between those two failures. Too much direct connection causes kickback. Too much isolation loses decision voltage.

## Decision Table

| path | what it improves | what it risks | proof needed |
|---|---|---|---|
| better passive frontend | preserves sampled charge with less wasted capacitance | still may not reach latch input target | extracted transfer near `1.0`, sign preserved, kickback still bounded |
| active preamp | enlarges sense voltage before latch decision | adds offset, noise, power, delay, and input capacitance | input-referred offset/noise below budget, output settles, latch resolves, energy recorded |
| direct latch connection | gives latch a strong input path | can damage sampled nodes through kickback | already failed the kickback gate |
| more passive plate area only | increases direct coupling | also increases total sense capacitance | current ultra result shows this is not enough |

## What We Should Do Next

The next measurable step should not be a full ADC. It should be a small fork test.

Build two candidate tests:

1. **Passive efficiency candidate**

   Keep the isolated frontend idea, but reduce wasted sense capacitance. The acceptance question is whether transfer moves closer to `1.0` without losing sign preservation.

2. **Active preamp candidate**

   Add a simple measured gain stage between the extracted sense nodes and the latch. The acceptance question is whether input-referred offset, noise, added kickback, and settling still leave positive decision margin.

The comparison should use the same input cases and the same target line. Otherwise the two paths cannot be compared honestly.

## The First-Principles Rule

The right path is the one that increases usable decision voltage per cost.

For the passive path, cost is mostly capacitance and kickback exposure:

```text
usable margin = transferred sense voltage - kickback risk
```

For the active path, cost is offset, noise, power, delay, and loading:

```text
usable margin = amplified voltage - offset - noise - kickback - settling error
```

The project should not prefer passive because it is simpler, and should not prefer active because it sounds stronger. It should prefer whichever path produces measured comparator margin from the extracted frontend.

## Claim Boundary

This page supports one claim:

The next design decision is now well-defined. The project must choose between a lower-capacitance passive frontend and an active preamp by measuring usable comparator margin, not by counting coupling capacitance alone.

This page refuses stronger claims:

It does not prove a passive frontend reaches the latch target, does not prove an active preamp works, does not prove comparator offset or noise, does not prove DRC/LVS, does not prove SAR conversion, and does not create accepted post-layout converter evidence.

## Where This Fits In The Flow

Read this page after:

- `Sky130 Frontend Sense Efficiency Audit`
- `Comparator Decision Margin From First Principles`

Read it before:

- `From Active Macro To Real Transistor Handoff`
- `Sky130 Frontend Input-Stage Handoff Candidate`
- `Converter Evidence Ladder`
- `Final Accepted Converter Gate`

The previous pages explain why the signal is too small and what margin the comparator needs. This page explains the design fork that led to the active-macro handoff and the still-open real-transistor handoff.
