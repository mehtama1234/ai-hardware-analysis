# First Real Converter Same-Candidate Extracted RC

- status: `same_candidate_extracted_rc_passed_not_strict_accepted_evidence`
- candidate id: `aimc_readout_candidate_001`
- run id: `aimc_readout_candidate_001_extracted_rc_run001`
- source netlist: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/aimc_readout_candidate_001_extracted_rc_measurement.sp`
- ngspice returncode: `0`
- row final V: `1.800000000`
- sense final V: `0.920000000`
- clock peak V: `1.800003000`
- digital peak V: `0.002110600`
- row 90 to 99 s: `1.161800e-11`
- sense delta V: `0.000000013`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/first-real-converter-same-candidate-extracted-rc.csv`

## First Principle

The first physical question is smaller than whether the converter is good. It is whether one named extracted object can be put into the circuit equations and driven through its pins. In this run, the candidate is not a set of disconnected estimates. The row pin, sense pin, clock pin, output pin, supplies, and references all belong to the same subcircuit instance.

What SPICE solves here is charge movement through extracted capacitance. A voltage source does not instantly set every internal node. The driver resistors limit current. The extracted capacitances store charge. The measured settling time is the time needed for those capacitors to move close to the requested voltage in this fixture.

That is useful because it closes one gap in the previous candidate loop: the physical object can be driven as one assembled netlist. It is still not enough to accept the converter. A real converter decision needs active devices, supply-current integration, comparator behavior, code error, signed area evidence, and a break-even rerun from the same accepted run.

## Strict Blockers

- The assembled candidate netlist contains extracted capacitances from starter cells, not transistor-level DAC, mux, sample path, comparator, SAR, and reference circuits.
- The run measures driven RC settling on the same candidate object, not supply current integration from active converter devices.
- The run has no comparator decision, no ADC code transition, no DAC linearity check, no DRC/LVS signoff area, and no same-run break-even replacement payload.

## Refused Claim

accepted post-layout converter evidence, transistor converter correctness, ADC/DAC accuracy, or replacement of the strict break-even payload
