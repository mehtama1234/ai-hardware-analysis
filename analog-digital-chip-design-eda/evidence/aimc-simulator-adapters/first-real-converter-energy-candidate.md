# First Real Converter Energy Candidate

- status: `b2_energy_candidate_written_not_strict_extracted_energy`
- candidate id: `aimc_readout_candidate_001`
- run id: `aimc_readout_candidate_001_simple_load_energy_run001`
- measurement artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-energy.json`
- source netlist: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice`
- ADC energy per conversion: `3.9881e-12` J
- DAC energy per row drive: `1.88637e-13` J
- mux energy per conversion: `9.63023e-14` J
- total energy per conversion: `4.273039299999999e-12` J
- strict payload ready: `False`

## First Principle

Energy is charge moved through a voltage. For this converter path, the useful question is not only whether a voltage settles. The useful question is how much supply work is spent to create the row voltage, charge the readout reference, and move the muxed sample.

This file binds the existing simple-load SPICE energy run to the named candidate object. That makes the energy discussion point at the same converter candidate as B1. It still does not become accepted energy, because accepted energy must be integrated through the extracted candidate path itself.

## Why This Is Not Strict Yet

- the source energy deck is a simple switched-capacitance load model
- the energy was not integrated through the assembled extracted candidate netlist
- bias current, leakage, clock power, and comparator short-circuit current are still absent

## Refused Claim

does not replace extracted converter energy, does not fill the strict payload, and does not write accepted post-layout evidence
