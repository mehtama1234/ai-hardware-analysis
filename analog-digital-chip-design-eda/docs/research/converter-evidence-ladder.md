# Converter Evidence Ladder

This page explains what each converter evidence level proves.

The project has many useful artifacts: SPICE decks, Magic extraction files, ngspice reports, layout starters, payload templates, strict validators, and temporary submission proofs. They are not the same kind of evidence. The ladder keeps them separate.

The simple rule is:

```text
a stronger artifact proves a stronger claim only when it measures the same physical object the claim is about
```

## The Simple Question

The simple question is:

What evidence is strong enough to let the converter replace the current break-even assumptions?

The answer is not "any post-layout-looking file." The answer is a complete same-run package: extracted circuit, simulation setup, energy, latency, noise, area, sharing rule, and break-even rerun all tied to the same converter run.

## Why A Ladder Is Needed

An analog converter claim can be overstated easily.

A schematic can look correct while layout parasitics break timing. An extracted netlist can exist while the wrong model files were used. A simulation can show low energy while leaving out reference or mux loading. A payload can have the right fields while pointing to placeholder files. A temporary self-test can prove the validator works without proving the converter.

The ladder prevents those mistakes by asking one question at each level:

```text
what object did this artifact actually measure?
```

## Evidence Levels

| level | what it proves | what it refuses |
|---|---|---|
| concept target | the needed DAC/ADC precision, noise budget, and sharing assumption are named | does not prove a circuit exists |
| schematic SPICE | the intended circuit equations work under chosen models and loads | does not prove layout parasitics, DRC/LVS, or physical area |
| behavioral/load SPICE | the target can pass simplified settling, loading, or energy checks | does not prove transistor implementation or extracted layout |
| layout starter | named Magic cells and source files exist | does not prove the cells implement the intended converter correctly |
| extracted RC | geometry produced parasitic capacitance or resistance that can affect equations | does not prove all devices, references, comparator behavior, or DRC/LVS |
| extracted transistor netlist | physical devices and parasitics are in the simulated circuit | does not by itself prove offset, noise, all corners, or system value |
| DRC | the layout follows selected process design rules | does not prove the circuit matches the schematic or works electrically |
| LVS | the extracted layout matches the intended schematic topology | does not prove timing, energy, noise, or model usefulness |
| post-layout simulation | the extracted physical circuit meets measured electrical targets in a named setup | does not prove measured silicon or production yield |
| measured silicon | a fabricated or measured object produced the reported values | does not prove the system should use it unless the values rerun the placement/break-even decision |
| accepted evidence | strict validation and same-run break-even rerun passed | still only supports the claim named by the payload boundary |

## The Important Separation

The strongest common mistake is to confuse these two statements:

```text
we extracted a file
```

and:

```text
the extracted converter is good enough to replace the system model
```

The first statement is about file existence and physical geometry. The second statement is about measured behavior and system cost.

To replace break-even assumptions, the project needs numbers from the extracted or measured converter:

- ADC energy per conversion
- DAC energy per row drive
- conversion time
- settling time
- output noise
- input-referred noise
- ADC area
- DAC area
- sharing rule
- replacement decision after rerun

Those numbers must describe the same run. If energy comes from one setup, noise from another, area from a placeholder, and sharing from an old estimate, the package is not evidence.

## The Same-Run Rule

The converter payload schema requires these fields to share one run identity:

```text
provenance.run_id
simulation.run_id
energy.run_id
latency.run_id
noise.run_id
area.run_id
break_even_rerun.run_id
```

That rule is not bookkeeping. It protects the claim.

A converter is a coupled object. Changing layout can change capacitance. Capacitance can change settling time. Settling time can change energy. Device size can change offset, noise, area, and kickback. Sharing can change load. If the values come from different runs, they may describe different converters.

## What Accepted Evidence Means Here

Accepted evidence means the payload passed the strict gate and the system reran the cost decision with the extracted or measured values.

The payload must contain:

- `measurement_level`: `post_layout_simulation` or `measured_silicon`
- extracted netlist and parasitic format
- row DAC, SAR readout, mux, reference, and sample-path inclusion flags
- simulator, command, process corner, voltage, temperature, and model files
- ADC and DAC energy values
- ADC comparison count, conversion time, and settling time
- output noise and input-referred noise
- ADC and DAC area
- replication or sharing rule
- break-even rerun artifact
- claim boundary

The accepted result is not just a better number. It is a number tied to the physical object and then used by the system decision.

## How To Read Current Pages

The current pages sit at different levels of the ladder.

`Converter Circuit-Simulation Estimate` is useful because it checks the target with explicit settling, quantization, noise, latency, energy, and sharing terms. It is still pre-layout.

`Row-DAC Settling SPICE Evidence`, `SAR Readout SPICE Evidence`, `Shared Converter Loading SPICE Evidence`, and `Converter Supply Energy SPICE Evidence` are stronger than prose because they run circuit checks. They still use simplified or non-final physical objects.

`Converter Starter Layout Smoke` and `Converter Starter Extracted RC Ngspice` prove the local layout and extraction path can produce physical artifacts. They do not prove the final converter.

`Sky130 Frontend Sense Efficiency Audit` and `Comparator Decision Margin From First Principles` explain why the readout frontend is still blocking the converter proof.

`Converter Post-Layout Evidence Contract`, `Converter Post-Layout Strict Intake`, and `Converter Post-Layout Payload Validator` define the accepted evidence gate. They do not themselves supply the missing evidence.

`Converter Post-Layout Temporary Submission Proof` proves the mechanical submission path can work in a temporary directory. It does not create canonical accepted evidence and does not prove a real converter.

## Why The Current Goal Is Still Open

The project has many real pieces, but the accepted converter package is still missing.

The current frontend evidence says:

```text
sign preserved
transfer improved
transfer still below target
comparator margin still open
```

The current post-layout payload path says:

```text
schema exists
strict validator exists
temporary positive path exists
real accepted payload is not present
```

So the honest state is:

```text
the workflow can reject weak evidence
the workflow can accept a complete temporary fixture
the workflow still needs a real extracted or measured converter package
```

## What The Next Evidence Must Look Like

The next accepted candidate must be one package, not a collection of nice-looking files.

It should say:

```text
this converter id
this run id
this extracted netlist
this model setup
this energy
this latency
this noise
this area
this sharing rule
this break-even rerun
this claim boundary
```

If any of those are missing, the correct result is not failure of the project. The correct result is refusal to upgrade the claim.

## Claim Boundary

This page supports one claim:

The evidence levels are now explicit. A reader can tell what schematic SPICE, extracted RC, DRC, LVS, post-layout simulation, measured silicon, and accepted evidence each prove.

This page refuses stronger claims:

It does not provide a real extracted converter payload, does not prove DRC/LVS, does not prove post-layout simulation, does not prove measured silicon, does not rerun break-even with real converter values, and does not create accepted post-layout converter evidence.

## Where This Fits In The Flow

Read this page after:

- `Comparator Decision Margin From First Principles`
- `Passive Frontend Vs Active Preamp`

Read it before:

- `Analog-To-Digital-To-Model Error Flow`
- `Final Accepted Converter Gate`

The earlier pages explain why the circuit is not ready. This page explains what kind of evidence would make it ready.
