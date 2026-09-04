# Converter Supply Energy SPICE Evidence

This file turns the fourth converter SPICE handoff test into evidence. It checks one narrow energy claim: the simple converter load model now has named rail energy for row drive, ADC-reference charging, and shared-mux charging.

- status: `converter_supply_energy_spice_complete_simple_load`
- cases: `3`
- all cases have positive integrated energy: `True`
- worst case: `high_conversion`
- worst total energy: `4.273039299999999e-12` J
- worst DAC energy: `1.88637e-13` J
- worst ADC energy: `3.9881e-12` J
- worst mux energy: `9.63023e-14` J
- rail: `1.0` V
- SPICE deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/converter_supply_energy.sp`
- measurement CSV: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/converter-supply-energy-spice.csv`

## First-Principles Reading

A converter can pass a voltage-error test and still fail as hardware if the signal costs too much energy to create and read. Energy accounting asks how much charge each source moves through the rail during the same timing window used by the accuracy checks.

This is the missing accounting link after row-DAC settling, SAR readout, and shared loading. The result gives a circuit-derived scale for the clean load model. It still cannot replace break-even by itself, because a real replacement needs post-layout parasitics or measured silicon.

## Remaining Converter SPICE Work

- none; all four executable handoff tests now have local SPICE evidence

## Refused Claim

does not prove extracted converter energy, bias current, clock power, leakage, comparator short-circuit current, measured board power, post-layout behavior, or measured silicon
