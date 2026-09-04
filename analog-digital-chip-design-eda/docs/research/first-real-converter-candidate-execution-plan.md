# First Real Converter Candidate Execution Plan

This page states the next practical work.

The repo can already reject a bad converter package. It can already run a starter extracted-RC macro. It can already show that the current candidate folder is not ready. The next step is to build one candidate package that is good enough to be judged.

The goal is not to make a big claim. The goal is to make one honest candidate.

## The Current State

The current candidate is blocked.

The strict preflight says:

```text
status: not_ready_for_strict_submission
issue count: 22
```

The blocker ledger says:

```text
status: blocked_on_real_post_layout_evidence
template only: True
blocker count: 45
```

The real-artifact discovery now sees two partial candidate files:

```text
candidate non-scaffold files: 2
current candidate strict issue count: 22
```

That means the folder has some useful pieces, but not a complete converter package.

## What We Can Prove Today

The extracted-RC starter macro runs in ngspice.

The measured row-drive result is:

```text
row_final_v = 1.800000000
row_90_when_s = 1.199360e-10
row_99_when_s = 1.243690e-10
```

This proves a narrow thing.

It proves that Magic-extracted capacitance can be put into an ngspice transient deck and driven as a physical load. It does not prove that the converter works. It does not prove a 10-bit DAC. It does not prove a 12-bit SAR readout. It does not prove comparator noise. It does not prove a replacement decision.

## The Candidate Object

The first real candidate should be one named readout object:

```text
row drive
  -> sampled column/sense node
  -> readout frontend
  -> comparator or SAR decision path
  -> digital output boundary
```

The current repo has pieces of this object:

| piece | current evidence | what it is missing |
|---|---|---|
| row DAC boundary | row-DAC settling SPICE passes simple half-LSB load | extracted full row DAC with real energy and area |
| SAR readout boundary | SAR readout SPICE passes simple half-LSB load | transistor-level SAR loop or measured readout path |
| shared mux boundary | shared loading SPICE passes simple half-LSB load | extracted mux path tied to same converter run |
| frontend boundary | ultra sense frontend preserves sign and reaches transfer 0.437908 | latch-level decision margin still below target |
| macro RC boundary | extracted-RC macro reaches row final 1.8 V | no transistor converter behavior |

The honest first candidate is therefore not "accepted converter." It is:

```text
first post-layout candidate attempt for the readout boundary
```

## The Exact Work Order

### 1. Choose One Converter Id

Pick one id and use it everywhere:

```text
aimc_readout_candidate_001
```

This id should name the physical object, not the whole project.

### 2. Choose One Run Id

Pick one run id and use it for every field:

```text
aimc_readout_candidate_001_sky130_tt_1p8v_27c_run001
```

Energy, latency, noise, area, simulation, provenance, and break-even rerun must all use this same id.

### 3. Put The Netlist In The Candidate Folder

The payload needs this file to exist:

```text
evidence/aimc-simulator-adapters/candidate-post-layout/netlist/...
```

For a real accepted attempt, this should be the extracted netlist for the converter/readout object being claimed. A starter RC macro can be copied there for rehearsal, but then the claim boundary must say it is only an RC starter and not accepted converter evidence.

### 4. Put The Model File In The Candidate Folder

The payload needs a model or measurement setup file:

```text
evidence/aimc-simulator-adapters/candidate-post-layout/models/...
```

For post-layout simulation, this should name the Sky130 model include and corner. For measured silicon, it should name the measurement setup instead.

### 5. Measure Energy

The payload needs two positive numbers:

```text
energy.adc_energy_per_conversion
energy.dac_energy_per_row_drive
```

First principle: energy is not a label. It is current drawn from a supply over time:

```text
energy = integral(voltage * current) over the conversion window
```

The row-drive number should come from the row drive event. The readout number should come from the ADC or comparator decision event. If the deck has only passive capacitors and ideal sources, the energy number must be labeled as a fixture estimate, not transistor converter energy.

### 6. Measure Latency

The payload needs:

```text
latency.conversion_time_ns
latency.settling_time_ns
```

First principle: latency is the time between asking the circuit for a value and having a value that the digital side can safely read.

For the current RC macro, row settling already has a narrow measurement:

```text
row_90_when_s = 1.199360e-10
row_99_when_s = 1.243690e-10
```

That is useful, but it is not the full conversion time. The full conversion time needs the readout decision path too.

### 7. Measure Noise And Offset

The payload needs:

```text
noise.output_noise_rms
noise.input_referred_noise
noise.meets_output_noise_budget
```

The current target is:

```text
output_noise_rms <= 0.004
```

First principle: the digital model does not see "noise" as a paragraph. It sees a wrong number or an uncertain number. The converter is acceptable only if that uncertainty stays inside the budget used by the model and placement logic.

### 8. Measure Area

The payload needs:

```text
area.adc_area_um2
area.dac_area_um2
```

First principle: area is the physical price paid for the circuit. The break-even calculation changes if the converter has to be repeated many times or placed far from the array.

Starter cell area can support planning. Accepted converter area needs the physical converter object being claimed.

### 9. Rerun Break-Even

After energy, latency, noise, area, and sharing are filled, rerun the break-even calculation with those values.

The rerun artifact must be placed under:

```text
evidence/aimc-simulator-adapters/candidate-post-layout/rerun/...
```

The payload must point to that artifact.

## What The Payload Should Say

The final candidate payload should stop being a template.

It should remove:

```text
template_only: True
replace-with-...
```

It should contain one coherent run:

```text
converter_id: aimc_readout_candidate_001
run_id: aimc_readout_candidate_001_sky130_tt_1p8v_27c_run001
measurement_level: post_layout_simulation
voltage_v: 1.8
temperature_c: 27
parasitic_format: extracted-spice
```

And it must keep the fixed target boundary:

```text
10-bit DAC input
12-bit ADC output
output noise budget <= 0.004
64 rows served
4 columns served
16 outputs per conversion cost
4 converter instances
```

## The Command Sequence

The clean sequence is:

```bash
python3 scripts/run_converter_starter_extracted_rc_ngspice.py
python3 scripts/run_converter_post_layout_candidate_readiness.py
python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json
python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json
```

The first command proves the current extracted-RC path still runs.

The second command shows whether the candidate is ready.

The third command explains any remaining blockers.

The fourth command must fail until the candidate is real. When it finally passes, it writes accepted evidence.

## What Passing Would Mean

Passing would mean:

```text
one converter id
one run id
real referenced files
positive energy
positive latency
noise inside budget
positive area
same sharing rule
break-even rerun written from the same values
strict submitter wrote accepted evidence
```

That would let the project replace converter assumptions in the break-even calculation.

It would not prove full chip performance, board power, production readiness, or measured silicon unless those were the actual evidence level.

## What Failing Would Mean

Failure is useful.

If energy is too high, the converter sharing rule or circuit topology is wrong.

If latency is too high, the analog path cannot feed the digital schedule as assumed.

If noise is too high, the model cannot trust the code without stronger correction or fallback.

If area is too high, the physical budget breaks even only under a narrower workload.

If the same-run check fails, the package is not one experiment.

## Next Local Development

The immediate local development is:

1. create a candidate netlist file from the best available extracted readout object
2. create a same-run measurement record for energy, latency, noise, and area
3. generate the candidate payload from that record
4. run preflight
5. let the failure list decide whether the next work is circuit design, measurement scripting, or payload wiring

This is the practical bridge from the written AIMC architecture to an inspectable converter claim.

## Claim Boundary

This page supports one claim:

The next converter proof step is now executable as an ordered candidate-build plan tied to the current evidence and strict payload blockers.

This page refuses stronger claims:

It does not create a real extracted converter payload, does not prove DRC/LVS, does not prove comparator noise, does not prove a 10-bit DAC or 12-bit SAR readout, does not write accepted post-layout evidence, and does not replace the converter break-even assumptions.
