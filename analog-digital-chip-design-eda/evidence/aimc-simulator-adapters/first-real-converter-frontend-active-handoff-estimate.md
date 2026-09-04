# First Real Converter Frontend Active Handoff Estimate

- status: `frontend_active_handoff_estimate_ready_not_same_deck_or_strict_evidence`
- candidate id: `aimc_readout_candidate_001`
- run id: `aimc_readout_candidate_001_frontend_active_handoff_estimate_run001`
- source frontend evidence: `evidence/aimc-simulator-adapters/sky130-ultra-sense-frontend-candidate.json`
- source input-stage evidence: `evidence/aimc-simulator-adapters/sky130-comparator-input-stage-ngspice.json`
- minimum measured input-stage gain V/V: `9.201769`
- minimum frontend sense diff V: `6.700000000e-05`
- minimum estimated output diff V: `6.165185271e-04`
- estimated polarity pass count: `4` of `4`
- uses same-deck simulation: `False`
- uses same extracted layout netlist: `False`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/first-real-converter-frontend-active-handoff-estimate.csv`

## First Principle

A small voltage difference is useful only if the next circuit can make it larger without flipping its sign. The extracted frontend gives the small voltage. The transistor input-stage run gives a measured small-signal gain. Multiplying them answers one limited question: if the input stage behaved the same way at the frontend output, how large would the next electrical state become?

This is not a new circuit simulation. It is a consistency check between two measured local artifacts. It says the passive frontend's roughly 67 microvolt sense signal would become about 0.62 millivolt after the measured input-stage gain. That is enough to justify building a real combined frontend-plus-input-stage deck. It is not enough to accept the converter.

## Result

| reset mode | frontend sense diff uV | estimated output diff mV | estimated polarity correct |
|---|---:|---:|---|
| `quiet_vcm` | `-67.000000` | `-0.616519` | `True` |
| `quiet_vcm` | `67.000000` | `0.616519` | `True` |
| `reset_pulse` | `-67.000000` | `-0.616519` | `True` |
| `reset_pulse` | `67.000000` | `0.616519` | `True` |

## Strict Blockers

- The frontend and active input stage are still separate evidence artifacts, not one extracted netlist simulated in one deck.
- The estimate multiplies measured frontend sense voltage by separately measured input-stage gain; it does not replace a direct transistor-level handoff run.
- There is no clocked latch resolution, kickback, mismatch, noise, SAR loop, supply-current integration, DRC/LVS area, or same-run break-even payload.

## Refused Claim

does not prove same-deck active handoff, full comparator behavior, full converter behavior, accepted post-layout evidence, or replacement economics
