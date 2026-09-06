# Real-data hybrid inference demonstrator

This experiment starts the real-workload portion of the
[shared execution plan](../../../../analog-digital-chip-design-eda/docs/roadmaps/rigorous-hybrid-inference-execution-plan.md).
It complements the ongoing converter repair; hardware acceptance remains open.

The task is classification of 8x8 handwritten digit features. Data attribution:
Alpaydin, E. and Kaynak, C. (1998), Optical Recognition of Handwritten Digits,
UCI Machine Learning Repository, [DOI: 10.24432/C50P49](https://doi.org/10.24432/C50P49).
UCI lists the dataset under CC BY 4.0. Its original training/test populations
use different writers. Downloaded source files are preserved unchanged and
pinned in `dataset-lock.json`; preprocessing divides the feature counts by 16.

`contract.json` was written before model training. It declares a fixed
64–32–10 ReLU MLP, first-layer analog candidacy, digital output/control path,
accuracy and comparative benefit targets, and remaining hardware requirements.
These are engineering targets for a demonstrator, not customer requirements.

The first run is `runs/20260906T195549986562Z/`. A seeded per-class split of the
official training file produces 3,062 training and 761 calibration rows.
The fixed final-epoch model reaches 96.98% calibration accuracy; ONNX and NumPy
calibration outputs agree. **The official test set has not been evaluated.**
Calibration accuracy cannot establish the preregistered test-accuracy target.

From `software-architecture/backend`, reproduce preparation with:

```bash
.venv/bin/python scripts/prepare_optdigits_demonstrator.py
.venv/bin/python scripts/check_optdigits_backend_handoff.py ../experiments/optdigits-v1/runs/20260906T195549986562Z
```

Preparation creates a new run, verifies dataset hashes, trains without using
test data, exports ONNX, and checks its numerical behavior against NumPy.
The backend handoff uses existing graph analysis and placement functions.
Its estimated costs do not establish latency or energy performance.

The shared compiler now has an executable, all-digital fallback for this frozen
graph. From `analog-digital-chip-design-eda`, reproduce it with:

```bash
../analog-in-memory-ai-inference/software-architecture/backend/.venv/bin/python scripts/run_optdigits_compiled_fallback.py ../analog-in-memory-ai-inference/software-architecture/experiments/optdigits-v1/runs/20260906T195750363771Z
```

It validates five review commands and 1,408 SRAM bytes, preserving all 761
calibration classifications against ONNX. NumPy performs the operations with
host-resident weights; no firmware or physical hardware is exercised. Analog
fallback remains 100% because extracted-latch qualification fails. Run results
include source/package hashes and the physical gate's evidence hash.

Next: freeze the circuit-derived operating/error profile, lower the first
projection under the explicit contract, calibrate only on calibration rows,
and bind both digital and hybrid evaluators to the identical model and test
population. Keep hardware execution gated until converter and array evidence
meet the applicable acceptance requirements.
