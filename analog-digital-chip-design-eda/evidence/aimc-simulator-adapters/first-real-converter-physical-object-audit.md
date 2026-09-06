# First Real Converter Physical Object Audit

- status: `b1_physical_object_ready_not_accepted_evidence`
- candidate id: `aimc_readout_candidate_001`
- workspace: `evidence/aimc-simulator-adapters/candidate-post-layout`
- expected extracted netlist: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice`
- expected extracted netlist exists: `True`
- candidate file count: `15`
- netlist file count: `5`
- ready for B1: `True`

## First Principle

A converter claim starts with an object. Before energy, latency, noise, or area can mean anything, the project must point to one physical circuit that turns an analog row result into a digital value.

If the named extracted converter object exists and contains every required part, B1 is ready. The later blockers still need measured energy, latency, noise, area, and a break-even rerun on the same object.

## Required Parts

- `references`: present
- `row_dac`: present
- `sample_path`: present
- `sar_readout`: present
- `shared_mux`: present

## Candidate Files

- `evidence/aimc-simulator-adapters/candidate-post-layout/README.md`: 825 bytes; matched parts: none
- `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-area.json`: 1141 bytes; matched parts: none
- `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-energy.json`: 1287 bytes; matched parts: none
- `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-latency.json`: 1354 bytes; matched parts: none
- `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-noise.json`: 1532 bytes; matched parts: none
- `evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-capacitive-isolation-ngspice.includes`: 229 bytes; matched parts: none
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_converter_macro_extracted.sp`: 799 bytes; matched parts: sample_path
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice`: 3721 bytes; matched parts: row_dac, sar_readout, shared_mux, references, sample_path
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_manifest.json`: 1285 bytes; matched parts: none
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/row_dac_extracted.sp`: 256 bytes; matched parts: row_dac
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/sar_readout_extracted.sp`: 262 bytes; matched parts: sar_readout, sample_path
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/shared_converter_mux_extracted.sp`: 246 bytes; matched parts: shared_mux
- `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`: 3290 bytes; matched parts: none
- `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/aimc_readout_candidate_001_break_even_rerun.json`: 3056 bytes; matched parts: none
- `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/sky130-capacitive-isolation-post-layout-both-polarity.json`: 3003 bytes; matched parts: none

## What Would Close B1

Create `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice` and make it contain or reference row DAC, SAR/readout, shared mux, references, and sample path behavior for the same candidate.

## Refused Claim

does not measure energy, latency, noise, or area, does not fill the candidate payload, and does not write accepted post-layout evidence
