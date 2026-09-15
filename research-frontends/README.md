# Standalone research frontends

Two independent static sites with a shared build implementation:

- `../analog-in-memory-ai-inference/studio/index.html`: Inference Studio.
- `../analog-digital-chip-design-eda/workbench/index.html`: Silicon Workbench.

Each contains six individually addressable HTML pages and its own stylesheet,
JavaScript, and embedded evidence snapshot. Open from disk or serve the workspace
root to preserve cross-project links. No backend, model run, Colab allocation,
or hardware job is triggered by browsing.

Run `python3 research-frontends/build.py` from `ai-hardware-analysis` after
updating source artifacts or frontend assets. The builder copies local evidence
and records SHA-256 provenance. The frozen 2026-09-09 decision package is an
explicit case study; the EDA experiment inventory comes from the saved system
state. Neither surface claims live telemetry.

Inference Studio uses the existing project's dark slate and warm analog accent,
serif editorial headings, a 144-tile selectable matrix, numerical profile
comparisons and the digital decision chain. Silicon Workbench retains the EDA
site's light technical surface with separate converter, physical-verification,
experiment inventory and hardware handoff pages.

The JSON source links preserve qualification scope. A tile map is a logical
matrix mapping, not a physical floorplan. Numerical agreement is not task
acceptance. DRC and scoped LVS are not full electrical qualification. Every
experiment retains its saved status without reclassifying `available` as pass.

Existing model-fit and verification applications remain linked from these
frontends, as do the original research libraries and DeepSeek integration.
