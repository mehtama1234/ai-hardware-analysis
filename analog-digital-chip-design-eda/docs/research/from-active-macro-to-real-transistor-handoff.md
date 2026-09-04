# From Active Macro To Real Transistor Handoff

This page explains the current AIMC converter gap in simple physical terms.

The project has already shown one useful thing: the extracted Sky130 frontend can hand its small signed voltage to an active gain block in one transient deck. That active block is still a macro. It behaves like a clean gain element. It does not behave like real transistors sitting on the frontend nodes.

The next proof is harder:

```text
extracted frontend sense voltage
  -> real Sky130 transistor input pair
  -> larger differential output
  -> latch decision
```

The current transistor handoff candidate does not pass yet. That is not a writing problem. It is the current circuit problem.

## The Simple Question

The simple question is:

Can the tiny frontend voltage drive real transistor gates without losing its sign, stalling the simulation, or becoming too small for the latch?

That question is different from the active-macro question.

The active macro asks:

```text
if a clean gain block receives this frontend signal, does the sign survive?
```

The real transistor handoff asks:

```text
when real Sky130 devices touch the frontend, does the signal still survive?
```

The second question includes loading, bias, operating point, offset, noise, and timing. The first question mostly avoids them.

## Why The Active Macro Was Useful

The active macro was not fake progress. It answered one bounded question.

Before that check, the project did not know whether the extracted frontend signal could be passed forward in a same-deck run at all. The frontend had already shown sign preservation, but sign preservation at the sense nodes is not the same as a usable input to the next stage.

The macro handoff showed this:

```text
frontend creates a signed sense voltage
same deck carries that voltage into a gain stage
the gained output keeps the right sign
```

That matters because it separates the proof into two smaller pieces.

One piece is signal direction:

```text
does the frontend still say positive when the input is positive?
```

The other piece is physical drive:

```text
can the next real circuit read that signal without damaging or erasing it?
```

The active macro helped with the first piece. It did not solve the second.

## Why The Macro Is Not Enough

A macro can be written to behave like the circuit we wish we had.

Real transistors do not do that. Real transistors bring their own physical costs:

- gate capacitance
- bias current
- limited input range
- finite transconductance
- body effect
- mismatch
- offset
- noise
- output loading
- startup behavior
- convergence problems in simulation

The frontend signal is already small. The current best measured transfer is `0.437908` against a pre-latch target of `1.0`. That means the signal is not arriving with spare margin. Any extra loading or offset can consume the remaining budget.

In plain words: the macro receives the signal gently. Real transistor gates pull on it.

## What Real Transistor Loading Means

The extracted frontend stores information as charge and voltage on small nodes.

A transistor input pair does not read those nodes without touching them. Its gates add capacitance. Its bias network chooses an operating point. Its drain and source devices need enough voltage room to stay useful.

The first-principles picture is:

```text
same stored charge spread over more capacitance = smaller voltage
```

So even before offset and noise, the transistor stage can shrink the useful input difference.

If the frontend gives a small voltage difference and the input pair adds too much capacitance, the stage may see the correct sign but too little magnitude. If the bias point is poor, one side may not amplify cleanly. If the transient deck is stiff or unstable, the run can time out before producing trustworthy measurements.

The newest assisted gate-startup run sharpens this. It no longer dies only as a timeout. It measures both reset-pulse polarities in a deck that contains the extracted frontend and real Sky130 input devices, but only one polarity keeps sign and output margin. A targeted passive gate-coupling sweep then finds no passing resistance setting. A bare source follower also fails because it collapses the tiny differential signal before the readout pair can use it. A direct extracted-frontend differential preamp times out. The same preamp bias also times out with measured sense-voltage sources, a small measured-source transient bias sweep finds no passing setting, and the first measured-source OP map also times out. Older input-stage evidence still shows the same primitive can pass, so the next circuit problem is now clearer: reproduce that primitive exactly before changing the preamp.

That is why a real transistor handoff must prove more than sign.

## The Handoff Acceptance Test

The next passing result must come from one named same-deck setup.

It must show:

- the extracted frontend is still the input object
- the active macro is not used
- the Sky130 transistor input stage is used
- all four frontend cases run to completion
- both input polarities preserve sign
- output margin is above the latch input target
- bias points are inspectable
- the run records energy and timing sources honestly
- accepted post-layout evidence is still not written unless the strict payload also passes

The key inequality is:

```text
transistor-stage output difference
  > latch input requirement
  + offset allowance
  + noise allowance
  + settling error
```

If that inequality does not pass, the transistor stage has not bought usable decision margin.

## Why Timeout Matters

A timeout is not just an inconvenience.

For this proof, a timeout means the project cannot inspect the same-run measurements. It cannot count the case as passed. It cannot infer margin from a partial trace. It cannot use a separate estimate as accepted physical evidence.

The correct treatment is:

```text
timed out run = failed handoff evidence
```

That is why the current page is useful even though it reports failure. It prevents the project from quietly replacing a hard circuit result with a softer estimate.

## What Comes After A Passing Transistor Handoff

A passing transistor handoff would not finish the converter.

It would unlock the next rung:

```text
real transistor input stage
  -> clocked latch
  -> bounded kickback
  -> correct decision
  -> SAR/code path
  -> strict same-run converter payload
```

The latch must then prove that it can resolve both signs without pushing enough charge back to corrupt the sampled value. The SAR or ADC code path must prove that the sequence of decisions becomes the right digital code. The strict payload must bind energy, latency, noise, area, sharing, netlist, model setup, and rerun evidence to the same physical object.

Only then can the model-side placement decision change.

## How This Fits The Whole System

The whole AIMC system is not trying to prove that analog compute is generally useful.

It is trying to prove this narrower chain:

```text
model has a MatMul-like operation
simulator says analog error is within budget
frontend preserves the physical signal
transistor readout turns it into a stronger signal
comparator turns it into a code
digital trust boundary checks residual risk
model state updates only if the check passes
```

The transistor handoff sits in the middle of that chain. If it fails, the backend may still have simulator evidence, and the frontend may still preserve sign, but the system cannot claim a trusted converter.

That is the current state.

## Claim Boundary

This page supports one claim:

The next physical gap is now well-defined. The project has a passing active-macro handoff, but the real Sky130 transistor input-stage handoff is still open and must pass before latch, SAR, strict payload, break-even, or placement claims can be upgraded.

This page refuses stronger claims:

It does not prove the transistor handoff, does not prove latch resolution, does not prove SAR conversion, does not prove converter energy or latency, does not prove DRC/LVS, and does not create accepted post-layout converter evidence.

## Where This Fits In The Flow

Read this page after:

- `Passive Frontend Vs Active Preamp`
- `Sky130 Frontend Input-Stage Handoff Candidate`

Read it before:

- `Sky130 Transistor Handoff Replacement Work Order`
- `Sky130 Extracted Frontend To Transistor Gate Startup`
- `Sky130 Extracted Frontend Gate Coupling Sweep`
- `Sky130 Extracted Frontend Source-Follower Handoff`
- `Sky130 Extracted Frontend Differential Preamp`
- `Sky130 Measured Sense Differential Preamp`
- `Sky130 Measured Sense Preamp Bias Sweep`
- `Sky130 Measured Sense Preamp OP Map`
- `Sky130 Preamp Known-Good Sanity Gap`
- `Sky130 Preamp Known-Good Reproduction`
- `Sky130 Frontend Transistor Input-Stage Handoff Candidate`
- `Final Accepted Converter Gate`

The previous pages explain why active gain is being considered and what the macro handoff proved. This page explains why replacing the macro with real Sky130 devices is the next hard proof step.
