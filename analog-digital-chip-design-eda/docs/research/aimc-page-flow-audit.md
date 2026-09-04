# AIMC Page Flow Audit

This audit defines the rewrite target for the combined analog in-memory compute workbench.

The problem is not that the project lacks pages. It has many pages. The problem is that the reader can still feel jumps between architecture, frontend, backend, analog simulation, RTL, EDA, evidence import, and claim readiness.

The fix is to make every important page behave like one link in the same chain.

## The Chain

```text
model graph
  -> placement boundary
  -> analog measurement chain
  -> model sensitivity
  -> digital governor rule
  -> RTL trace
  -> synthesis and physical-flow evidence
  -> backend evidence import
  -> frontend claim readiness
```

Each page should make one part of that chain clearer. If a page does not say what enters it and what leaves it, it is not yet seamless.

## Page Contract

Every page that belongs to the combined workflow should state four things near the top or near the first concrete example.

```text
Consumes: the artifact, decision, or measurement this page starts from.
Produces: the artifact, decision, or measurement this page emits.
Supports: the strongest claim the page can honestly support.
Refuses: the stronger claim the page must not make yet.
```

This is not formatting decoration. It is the way to keep the writing first-principles. A page becomes vague when it names a topic instead of naming the object that changes.

## Current Strong Pages

### Combined AIMC Workbench End-To-End Goal

Status: strong system spine.

Consumes: the old workbench, the new lab, and the live backend package.

Produces: the shared end-to-end goal and the standard for future pages.

Supports: the repos are connected by a real prototype loop.

Refuses: production chip readiness, measured board performance, measured energy, analog macro layout, package reliability, and tapeout readiness.

Needed improvement: keep it as the main written goal, but add a small page-by-page tracker after the next rewrite pass so the reader can see which pages were upgraded.

### AIMC Evidence Ledger

Status: strong proof ledger.

Consumes: generated analog, model-impact, RTL, synthesis, OpenLane, export, and backend-import artifacts.

Produces: the human-readable evidence map and the backend-compatible evidence batch.

Supports: local lab evidence can support narrow placement and accuracy claims.

Refuses: measured latency, measured energy, silicon behavior, and production readiness.

Needed improvement: add a compact table that lists every evidence JSON file, its claim level, and the backend claim it affects. The board and power upgrade path is now covered by `board-and-power-measurement-boundary.md`.

### Cross-Repo AIMC Loop Proof

Status: strong executable proof endpoint.

Consumes: backend health, backend hardware placement, lab import script, governor generator, RTL checker, evidence exporter, backend import endpoint, and claim-readiness endpoint.

Produces: `cross-repo-loop-proof.json` and `cross-repo-loop-proof.md`.

Supports: the old backend and new lab are wired into one runnable loop.

Refuses: any claim that requires measured board traces, measured power, calibrated silicon, physical analog macro integration, or signoff.

Needed improvement: surface this report more visibly from the old frontend and the current-lab site index.

### AI Hardware Architecture To Working Lab Bridge

Status: strong bridge, but some now-stale "missing build" lines should be tightened.

Consumes: old architecture pages and current hardware-lab artifacts.

Produces: the mapping from architecture requirements to implemented lab proofs.

Supports: the new lab is the proof extension of the old workbench.

Refuses: full AIHWKIT/CrossSim agreement, production tapeout, full model compiler, and board-level proof.

Needed improvement: update the "Missing build" items that have since become partially done: backend ONNX/operator output now reaches lab placement rows; evidence export/import now exists; the cross-repo proof now exists.

### Board And Power Measurement Boundary

Status: new measurement contract.

Consumes: package ID, board/runtime setup, governor trace, voltage/current samples, thermal setup, workload ID, and host-overhead boundary.

Produces: the required fields for measured board runtime and measured power/thermal evidence.

Supports: a clear upgrade path for `C2` latency and `C3` energy claims.

Refuses: treating local RTL runtime, OpenLane-derived estimates, or unsynchronized traces as measured hardware evidence.

Needed improvement: when real board or instrumented runtime data exists, add an importer that enforces this page's required fields.

### Mixed-Signal Trust Boundary Spec

Status: conceptually deep and close to the desired first-principles style.

Consumes: analog readout fields and tile health state.

Produces: corrected value, valid/fallback decision, reason code, counters, and tile-health action.

Supports: analog placement and analog acceptance are separate hardware decisions.

Refuses: trust before measurement, trust from average accuracy alone, and any claim that a scheduler choice proves the analog value was usable.

Needed improvement: add a small handoff note to the backend hardware-placement artifact and the generated model-impact governor rows.

### Hybrid AIMC System Architecture

Status: strong architecture page.

Consumes: request metadata, model phase, tile health, calibration state, and error budget.

Produces: a system block model that separates analog arrays, converters, SRAM/cache, correction, scheduler, and digital control.

Supports: AIMC is a mixed system where analog arrays are only one resource.

Refuses: the idea that analog matrix multiply alone proves foundation-model acceleration.

Needed improvement: connect each block in the diagram to an existing lab artifact or mark it as missing.

## Pages That Need A Richer Handoff

### Old Frontend Workbench

Page: `ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/index.html`

Current strength: it already shows packages, evidence, claim readiness, hardware-lab import, and hardware placement.

Flow gap: the page should more directly tell the reviewer: "This is where the answer lands." It should show the current proof chain in one compact panel and link to the new proof report.

Rewrite target:

- show backend hardware placement as the model-to-chip handoff
- show hardware-lab evidence import as the chip-to-claim handoff
- show claim readiness as the final answer
- show blocked production readiness as a correct refusal, not a failure

### Old Master Review Path

Page: `ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/master-review-path.html`

Current strength: it gives the reading order and claim ladder.

Flow gap: each card mostly says "Produces", but not "Consumes", "Supports", and "Refuses".

Rewrite target:

- add the full page contract to each major review step
- point step 10 through 12 to the generated cross-repo proof report
- make the review path start at the frontend and end at claim readiness

### Old Combined Workflow

Page: `ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/combined-system-end-to-end-workflow.html`

Current strength: it explains why the two repos are one system.

Flow gap: it needs a more concrete artifact table, not only a conceptual chain.

Rewrite target:

- table of old artifact, new artifact, and claim affected
- explicit link to backend `hardware_placement`
- explicit link to evidence import endpoint
- explicit link to `cross-repo-loop-proof.md`

### Hardware Lab Bridge

Page: `docs/research/ai-hardware-architecture-to-working-lab-bridge.md`

Current strength: it maps old architecture needs to new lab artifacts.

Flow gap: several "missing build" items are no longer fully missing, because the backend placement import, evidence exporter, backend import, and cross-repo proof now exist.

Rewrite target:

- change missing items into `done`, `partial`, and `still missing`
- name exact files and commands for each done item
- avoid claiming full compiler or measured silicon

### Toolchain Map

Page: `docs/research/toolchain-map.md`

Current strength: it names tools.

Flow gap: tool pages can become shopping lists. The richer version should say what each tool proves and what it cannot prove.

Rewrite target:

- AIHWKIT: model-level analog noise and drift simulation, not silicon proof
- CrossSim-style work: array/interconnect risk, not full macro signoff
- Yosys: RTL-to-gates proof, not routing
- OpenLane/OpenROAD: educational physical-flow evidence, not production signoff
- backend package: claim bookkeeping, not physics

### Lab README Pages

Pages:

- `labs/analog/analog-in-memory-foundation-model-hardware/README.md`
- `labs/digital/aimc-control-plane-rtl/README.md`
- `labs/digital/aimc-control-plane-synthesis/README.md`
- `labs/eda/README.md`
- OpenLane prep READMEs

Current strength: they explain local commands and outputs.

Flow gap: they should each say how their local output enters the global proof chain.

Rewrite target:

- analog lab produces physical-error and model-impact rows
- digital RTL lab consumes those rows and produces checked reason bits
- synthesis lab proves the controller lowers to gates
- EDA lab proves selected blocks can enter physical flow under recorded constraints
- evidence exporter turns those artifacts into backend package evidence

## First Rewrite Batch

The first batch should update pages that carry the main review experience:

1. Current-lab `aimc-evidence-ledger.md`
2. Current-lab `ai-hardware-architecture-to-working-lab-bridge.md`
3. Current-lab `toolchain-map.md`
4. Current-lab analog AIMC lab README
5. Current-lab digital RTL README
6. Current-lab EDA README
7. Old `master-review-path.html`
8. Old `combined-system-end-to-end-workflow.html`
9. Old frontend hardware-lab panel in `index.html`

Done means each page has the contract, links to the next page or artifact, and refuses unsupported claims in plain words.

## Second Rewrite Batch

The second batch should deepen pages that explain why the workflow is shaped this way:

1. `hybrid-aimc-system-architecture.md`
2. `transformer-operation-partition-for-hybrid-aimc.md`
3. `mixed-signal-trust-boundary-spec.md`
4. `analog-compute-needs-a-trust-boundary.md`
5. `analog-foundation-models-need-a-digital-referee.md`
6. `analog-placement-is-not-analog-acceptance.md`
7. `where-analog-compute-actually-helps.md`
8. `analog-serving-policy-decides-when-to-use-the-array.md`
9. `eda-is-constraint-solving.md`

Done means these pages do not merely explain principles. They point to the exact artifact in this repo that embodies the principle.

## Third Rewrite Batch

The third batch should add missing pages only if the first two batches reveal true gaps.

Likely missing pages:

- Board and power measurement plan that separates local estimates from measured traces.

The backend hardware placement page now exists as `backend-hardware-placement-first-principles.md`.
The evidence import and claim-readiness page now exists as `evidence-import-and-claim-readiness-first-principles.md`.
The AIHWKIT and CrossSim adapter boundary page now exists as `aihwkit-crosssim-adapter-boundary.md`.

No new page should be added unless it has a clear place in the chain.

## Acceptance Criteria

The seamless version is done when:

- the old review path and the new research pages point to the same cross-repo proof
- the frontend, backend, lab, evidence, and EDA pages share the same vocabulary
- every important page states consumes, produces, supports, and refuses
- each claim is tied to a file, command, endpoint, or generated report
- the site build passes
- the project validator passes
- the 31-step AIMC bridge check passes

Until then, the project is connected technically, but not fully connected as a reviewable body of writing.
