# First Real Converter Candidate Loop Strict Readiness

- status: `candidate_loop_complete_not_strict_accepted_evidence`
- candidate id: `aimc_readout_candidate_001`
- same candidate: `True`
- candidate loop complete: `True`
- same run: `False`
- strict ready: `False`
- accepted post-layout ready: `False`

## First Principle

An end-to-end candidate loop is not the same as accepted evidence. The candidate loop answers whether every required kind of fact has a place: object, energy, latency, noise, area, and break-even. Accepted evidence asks a harder question: did those facts come from one real extracted or measured run of the same converter?

The current loop is useful because all six facts point to one candidate name. It is not final because the facts do not yet come from one strict extracted run.

## Run IDs

- `energy`: `aimc_readout_candidate_001_simple_load_energy_run001`
- `latency`: `aimc_readout_candidate_001_simple_load_latency_run001`
- `noise`: `aimc_readout_candidate_001_behavioral_noise_run001`
- `area`: `aimc_readout_candidate_001_starter_area_run001`
- `break_even`: `aimc_readout_candidate_001_candidate_break_even_run001`

## Strict Blockers

- B2-B6 do not share one run id.
- B2 energy is simple-load SPICE tied to the candidate, not extracted candidate supply integration.
- B3 latency is simple-load timing tied to the candidate, not extracted full-candidate timing.
- B4 noise is behavioral circuit noise tied to the candidate, not extracted or silicon noise.
- B5 area is a starter boundary estimate tied to the candidate, not DRC/LVS-clean extracted signoff area.
- B6 uses those mixed-level candidate values, so it cannot replace the accepted break-even result.

## Next Real Work

- Run one extracted candidate deck that measures energy through the assembled netlist.
- Measure full conversion latency through the same extracted candidate run.
- Measure readout noise or input-referred noise for that same run.
- Compute area from the same candidate layout boundary with DRC/LVS status recorded.
- Rerun break-even from those same-run extracted values.
- Only then build and submit the canonical strict payload.

## Refused Claim

does not fill the canonical strict payload, does not submit evidence, and does not write accepted post-layout evidence
