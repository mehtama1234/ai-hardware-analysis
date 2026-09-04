# First Real Converter Break-Even Candidate

- status: `b6_break_even_candidate_written_not_strict_replacement`
- candidate id: `aimc_readout_candidate_001`
- run id: `aimc_readout_candidate_001_candidate_break_even_run001`
- rerun artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/aimc_readout_candidate_001_break_even_rerun.json`
- combined converter energy: `4.176737e-12` J
- default target beats digital: `True`
- default margin vs digital per output: `3.1495393750000004e-13` J
- replacement decision: `candidate_would_replace_under_sharing_rule`
- claim ready to replace break-even: `False`

## First Principle

Break-even asks whether the analog path still saves enough work after paying for the converter. The array can be cheap and the converter can still erase the benefit. Sharing matters because one conversion cost can be paid by one output or spread across many useful outputs.

This candidate rerun uses the same candidate object, energy, latency, noise, area, and sharing rule collected in B1 through B5. It is the first end-to-end economic loop for this named candidate, but it is not the final loop because those values are not strict extracted measurements from one accepted run.

## Refused Claim

does not use strict extracted energy, latency, noise, and area; does not fill the strict payload; does not write accepted post-layout evidence
