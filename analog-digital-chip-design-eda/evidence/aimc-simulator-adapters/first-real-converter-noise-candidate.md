# First Real Converter Noise Candidate

- status: `b4_noise_candidate_written_not_strict_extracted_noise`
- candidate id: `aimc_readout_candidate_001`
- run id: `aimc_readout_candidate_001_behavioral_noise_run001`
- measurement artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-noise.json`
- source netlist: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice`
- output noise RMS: `0.000851121`
- input-referred noise: `0.000531011`
- output noise budget: `0.004`
- meets output noise budget: `True`
- strict payload ready: `False`

## First Principle

Noise is uncertainty in the value handed to the digital side. A converter can settle on time and still be unusable if the uncertainty is large enough to change the code or push the model state outside its error budget.

This candidate binds the existing behavioral noise estimate to the same named converter object used by B1, B2, and B3. It keeps the useful number visible while refusing to call it extracted noise.

## Why This Is Not Strict Yet

- the noise comes from a deterministic behavioral estimate
- the noise was not simulated through the assembled extracted candidate netlist
- device noise spectra, comparator offset distribution, mismatch, and clock feedthrough statistics are still absent

## Refused Claim

does not replace extracted converter noise, does not fill the strict payload, and does not write accepted post-layout evidence
