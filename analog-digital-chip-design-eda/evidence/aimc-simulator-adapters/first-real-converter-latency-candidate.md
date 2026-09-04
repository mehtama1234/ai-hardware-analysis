# First Real Converter Latency Candidate

- status: `b3_latency_candidate_written_not_strict_extracted_timing`
- candidate id: `aimc_readout_candidate_001`
- run id: `aimc_readout_candidate_001_simple_load_latency_run001`
- measurement artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-latency.json`
- source netlist: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice`
- settling time: `4.0` ns
- conversion time: `12.0` ns
- total time before digital value: `16.0` ns
- strict payload ready: `False`

## First Principle

Latency is the wait between asking the analog path for a value and having a digital value that can be used. For this converter path, that wait has two parts: the row/sample voltage must settle, then the readout must make its timed decisions.

This candidate binds the local 4 ns settling window and 12 ns readout window to the same named converter object used by B1 and B2. It is useful because the system can now talk about object, energy, and time using the same candidate name.

## Why This Is Not Strict Yet

- the timing windows come from simple source/load SPICE decks
- the conversion timing was not measured through the assembled extracted candidate netlist
- comparator metastability, reference settling, clocking, and full SAR control timing are still absent

## Refused Claim

does not replace extracted converter timing, does not fill the strict payload, and does not write accepted post-layout evidence
