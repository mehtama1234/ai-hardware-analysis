# Final Accepted Converter Gate

This page defines what closes the current analog readout goal.

The project is not done when a schematic simulates, when a layout file exists, or when a payload has the right shape. The project is done for the converter only when one real extracted or measured converter package passes strict intake and reruns the system decision it wants to change.

The simple rule is:

```text
one converter
one run
one physical evidence package
one break-even rerun
one claim boundary
```

## The Simple Question

The simple question is:

What exact evidence lets us say the converter is accepted?

The answer is a package that ties the converter result to the physical object that produced it. The package must let a reviewer inspect the extracted netlist or measured setup, the model files, the energy, the latency, the noise, the area, the sharing rule, and the rerun decision.

## What Must Be In The Package

The accepted package must contain these things:

| object | why it is required |
|---|---|
| converter id | names the converter being judged |
| run id | ties all values to the same simulation or measurement |
| target boundary | states the DAC bits, ADC bits, noise budget, rows, columns, and sharing target |
| extracted netlist or measured setup | proves the values come from a physical object, not only a planning estimate |
| model files or measurement setup files | states the electrical world used for the result |
| simulation command or measurement procedure | lets the result be repeated or inspected |
| energy values | tells the system what conversion costs |
| latency values | tells the system how long conversion takes |
| noise and offset values | tells the model how much uncertainty enters the value |
| area values | tells the system what physical cost was paid |
| sharing rule | tells the system how many rows, columns, outputs, and converter instances share the cost |
| break-even rerun | proves the system decision was recomputed with these values |
| claim boundary | states exactly what this package supports and refuses |

If any of these are missing, the correct state is not accepted.

## Required Fixed Target

The current target boundary is:

```text
10-bit DAC input
12-bit ADC output
output noise budget <= 0.004
64 rows served
4 columns served
16 outputs per conversion cost
4 converter instances
```

If a candidate uses a different boundary, it must say so. It cannot silently replace the target while claiming to close the same proof.

## Same-Run Requirement

These fields must carry the same run id:

```text
provenance.run_id
simulation.run_id
energy.run_id
latency.run_id
noise.run_id
area.run_id
break_even_rerun.run_id
```

This protects the result.

Energy from one run, noise from another run, and area from a placeholder do not describe one converter. The system cannot make a replacement decision from mixed evidence.

## The Acceptance Path

The final accepted path is:

```text
fill real payload
  -> validate required fields
  -> validate referenced files exist
  -> check same-run identity
  -> check numeric boundaries
  -> check noise budget
  -> rerun break-even with extracted or measured values
  -> write accepted break-even rerun
  -> write accepted submission report
  -> update placement and claim readiness
```

The command path already exists:

```bash
python3 scripts/submit_converter_post_layout_payload.py REAL_PAYLOAD.json
```

That command should write accepted evidence only after strict validation and rerun both pass.

## What Happens After It Passes

Passing the converter gate does not mean the whole foundation model is proven.

It means the project may replace old converter assumptions with measured or extracted converter values.

After the gate passes, the system must do four follow-up actions:

1. rerun converter break-even with the accepted energy, latency, noise, area, and sharing rule
2. rerun placement or layout-risk decisions that depend on converter precision and cost
3. rerun model residual checks if the accepted noise or quantization differs from the simulator assumptions
4. update frontend/backend claim readiness so supported, needs-review, and blocked claims are visible

That is the point of accepted evidence. It changes downstream decisions. If no downstream decision changes or gets rerun, the package is only an archive.

## What The Current Repo Can Already Do

The current repo can already do several important things:

- define the post-layout payload schema
- reject placeholder payloads
- reject missing referenced files
- require same-run consistency
- run a temporary complete fixture through the acceptance path
- avoid writing temporary proof files into canonical accepted evidence
- show the current blocker ledger

That means the gate is mechanically ready.

## What Is Still Missing

The real evidence is still missing.

The current blocker ledger reports:

```text
status: blocked_on_real_post_layout_evidence
preflight status: not_ready_for_strict_submission
template only: True
blocker count: 45
```

The missing pieces include:

- real converter id
- real shared run id
- extracted netlist file
- model or measurement setup files
- real simulation command or measurement procedure
- positive ADC and DAC energy numbers
- positive conversion and settling time
- output noise at or below budget
- input-referred noise
- positive ADC and DAC area
- real break-even rerun artifact
- claim boundary that does not overstate the evidence

Until those exist, the project should keep refusing accepted converter claims.

## How This Fits The Whole AIMC Flow

The full flow is:

```text
model graph
  -> analog candidate placement
  -> simulator residual evidence
  -> Sky130 frontend and comparator evidence
  -> accepted converter package
  -> break-even rerun
  -> residual-aware placement update
  -> backend claim readiness update
  -> frontend review page
```

The final converter gate sits in the middle. It is the point where local circuit evidence becomes system evidence.

Without this gate, the project can say:

```text
we have simulator evidence, RTL evidence, OpenLane evidence, and partial Sky130 readout evidence
```

With this gate, the project can say:

```text
this named converter package passed the strict post-layout or measured-silicon intake and its values were used to rerun the system decision
```

Those are different claims.

## Done Means Done

For the converter, done means:

```text
the payload is real
the referenced files exist
the values are numeric and inside required boundaries
the run ids match
the noise budget passes
the break-even rerun uses the accepted values
accepted evidence is written by the strict submitter
the downstream placement and claim pages are updated
```

Anything less is progress, not completion.

## Claim Boundary

This page supports one claim:

The final accepted converter gate is now stated clearly enough that a reviewer can tell what remains and what proof would close the current converter goal.

This page refuses stronger claims:

It does not provide the real extracted converter payload, does not prove DRC/LVS, does not prove post-layout simulation, does not prove measured silicon, does not rerun break-even with real converter values, does not update placement with accepted converter values, and does not create accepted post-layout converter evidence.

## Where This Fits In The Flow

Read this page after:

- `Converter Evidence Ladder`
- `Analog-To-Digital-To-Model Error Flow`
- `Converter Post-Layout Evidence Contract`
- `Converter Post-Layout Submission Path`

This is the final written gate. The next work after this is not more wording unless the review path is unclear. The next proof work is to produce the real converter package or build the next frontend/preamp evidence needed to make that package pass.
