# Sky130 Comparator Acceptance Fixture Spec

This page turns the measured sample-and-hold result into the next comparator test. It does not claim that the comparator exists yet. It says what the comparator must prove before it is allowed to sit behind the passing differential dummy sample-and-hold candidate.

- status: `sky130_comparator_acceptance_fixture_spec_ready_not_comparator_proof`
- half LSB 12b V: `2.197265625e-04`
- worst measured sample-hold error V: `6.300000000e-05`
- remaining comparator offset or noise budget mV: `0.1567`
- target combined offset/noise mV: `0.1530`
- first known failing combined offset/noise mV: `0.1581`
- candidate post-layout written: `False`
- accepted post-layout written: `False`

## First Principle

The sample-and-hold does not produce a final answer. It leaves a small voltage difference for the next circuit to decide. That next circuit is the comparator.

A comparator can fail even when the sampled voltage is good. Its internal mismatch can move the decision boundary. Its noise can make the same input produce different decisions. Its clock edge can kick charge back into the held node. These are not separate bookkeeping problems. They all spend the same voltage budget between the held decision voltage and the nearest wrong ADC code.

The current measured sample-and-hold candidate spends 0.0630 mV of a 0.2197 mV half-LSB budget. That leaves about 0.1567 mV for comparator offset, comparator noise, and comparator loading. The stress table shows that 0.1530 mV still passes, while 0.1581 mV starts to fail. The next transistor deck should therefore aim below 0.1530 mV and treat 0.1567 mV as the hard line unless the sample-and-hold improves.

## Required Measurements

| measurement | method | acceptance |
|---|---|---|
| `input_referred_static_offset_mv` | sweep a small differential input around zero and find the sign-change point | absolute offset <= 0.1530 mV target and below 0.1567 mV hard budget |
| `decision_noise_rms_mv` | run repeated transient decisions with the same input and measure output-code spread as input-referred voltage | combine with static offset by root-sum-square before comparing with the budget |
| `kickback_on_held_decision_node_v` | measure differential held-node movement when the comparator input is connected and clocked | sample-hold movement plus input-referred decision uncertainty remains below 2.197265625e-04 V |
| `metastability_resolution_ns` | measure how long the latch output takes to reach a valid logic level near the smallest accepted input | resolves inside the SAR comparison time used by the converter estimate |
| `supply_energy_per_decision_j` | integrate supply current during one comparison event | record the value, but do not use it for break-even until the full extracted converter payload exists |

## Stimulus Cases

| case | input | purpose |
|---|---|---|
| `zero_crossing_offset_sweep` | small signed differential inputs around zero | find whether the comparator decision boundary is shifted away from zero |
| `budget_edge_pass_case` | differential input at 0.1530 mV plus the measured sample-hold error | check the strongest already-passing budget point |
| `budget_edge_fail_guard` | differential input at 0.1581 mV plus the measured sample-hold error | prove the fixture can detect when the known budget is exceeded |
| `low_mid_high_sampled_inputs` | reuse the low, mid, and high common-mode cases from the candidate input sweep | make sure comparator loading does not destroy the sample-and-hold result that already passed |
| `controlled_width_mismatch_cases` | reuse the matched and +/-1% and +/-2% sample-switch width cases | keep the current mismatch regression gate alive after the comparator is attached |

## Build Order

- start with a clocked differential latch or preamp-latch deck in Sky130 ngspice
- drive it from the existing differential dummy sample-and-hold candidate instead of an ideal voltage source only
- measure offset first, because a noisy comparator with unknown static offset cannot be interpreted
- measure kickback before SAR integration, because kickback spends the same voltage budget as hold error
- add repeated-noise or corner-style sweeps only after the nominal transient deck is numerically stable
- keep the output as candidate schematic evidence; do not write accepted post-layout evidence

## Refused Claim

does not simulate comparator transistors, prove comparator noise, prove SAR conversion, prove extracted layout, or replace converter economics
