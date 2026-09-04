# First Real Converter Area Candidate

- status: `b5_area_candidate_written_not_strict_extracted_area`
- candidate id: `aimc_readout_candidate_001`
- run id: `aimc_readout_candidate_001_starter_area_run001`
- measurement artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-area.json`
- source netlist: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice`
- ADC area: `1200.0` um2
- DAC area: `700.0` um2
- total readout area: `1900.0` um2
- strict payload ready: `False`

## First Principle

Area is chip space. A converter can look good in energy or timing and still be a bad system choice if the physical cells consume too much repeated space near every array or column group.

This candidate binds the starter layout area estimate to the same named converter object used by B1 through B4. It is useful for the system discussion because object, energy, latency, noise, and area now point to one candidate name.

## Why This Is Not Strict Yet

- the source area is a starter macro boundary estimate
- the candidate does not carry DRC/LVS-clean physical area records
- the area was not recomputed from the assembled candidate layout boundary

## Refused Claim

does not replace extracted signoff area, does not fill the strict payload, and does not write accepted post-layout evidence
