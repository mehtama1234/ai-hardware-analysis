# Sky130 Transistor Handoff Probe Ladder

- status: `probe_ladder_measured_partial_cause`
- probe count: `4`
- measured probe count: `1`
- timed-out probe count: `3`
- full handoff status: `transistor_handoff_failed_or_timed_out`
- strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-transistor-handoff-probe-ladder.csv`

## First Principle

The full handoff fails where too many things are joined at once. This probe ladder breaks the problem into smaller electrical questions: can the transistor stage run in transient, can it run with frontend-sized capacitance, can the extracted frontend survive gate-like capacitance, and can the extracted frontend touch isolated real transistor gates.

## Probe Results

| probe | measured | timed out | sense sign | gate sign | output sign | output diff mV |
|---|---|---|---|---|---|---:|
| `standalone_transistor_transient` | `False` | `True` | `` | `` | `` | `` |
| `measured_sense_with_equivalent_cap_load` | `False` | `True` | `` | `` | `` | `` |
| `extracted_frontend_with_gate_cap_only` | `True` | `False` | `True` | `` | `` | `` |
| `extracted_frontend_with_isolated_real_transistor_gates` | `False` | `True` | `` | `` | `` | `` |

## Refused Claim

does not replace the full four-case transistor handoff, does not prove latch or SAR behavior, and does not create accepted post-layout converter evidence
