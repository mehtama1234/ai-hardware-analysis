# Hybrid inference restart ledger

Updated 2026-09-06. Active goal: [execution plan](rigorous-hybrid-inference-execution-plan.md).

## User-requested project checkpoint and priority reset

Follow-up read-only inventory is recorded in
[hardware access requirements](hybrid-hardware-access-requirements.md).
No local analog board/instrument was identified; USB visibility is limited
(`lsusb` exit 1, no output), and remote/disconnected equipment is unknown.
Workload capability requirements are derived without choosing an array encoding
or purchasing anything. Hardware access still needs user input. No new circuit
experiment launched in this follow-up; do not interpret auto-continuation as
an answer to the pending hardware question.

See [project checkpoint](hybrid-inference-project-checkpoint.md). The user
interrupted sub-block work and requested a big-picture assessment. No new
simulation or layout experiment was launched during this checkpoint.

Recovery correction: the interrupted diffusion-extension build completed in
`capture-with-mim-layout/20260906T225029565233Z`: DRC 0, no layout-read errors,
unique LVS and all saved artifact hashes verified against current files.
The earlier statement that the latest revision still failed LVS is superseded.
This revision has no verified extracted transient or capacitance-export audit.
No relevant simulator/layout process remained live when checked.

Inspected the actual Optdigits contract and compiled-fallback result: real task
preparation/digital execution exist; memory technology, converter operating
envelope, target interface and hardware access remain unresolved. Installed
simulators are not hardware access. Common local USB/serial instrument paths
were absent, which does not rule out disconnected/networked/remote equipment.

Priority is now actual hardware inventory and M1 system closure. Further latch
optimization is not the default next action. One bounded latest-layout export/
transient check remains useful after this project-level decision. No purchasing,
fabrication, external deployment, held-out scoring or goal completion authorized
or claimed by this checkpoint.

## Capture internal-node and terminal coverage update

### First routed MIM revision: physical failures preserved

- Previous turn was progress: modeled four-cap integration reduced peaks and
  quantified timing/energy cost. Added `build_capture_with_mim_caps.py` to
  physically place four verified MIM cells, supply their bottom plates, and
  attempt contact access to the four floating diffusion nodes. Source layout
  and capacitor artifacts are hash-checked and never edited in place.
- First run `capture-with-mim-layout/20260906T224552753136Z` and revised
  route run `20260906T224627044615Z` fail LVS. Both reported DRC 0, but their
  logs reveal unrecognized `pdiffcont`/`ndiffcont` layer names, so those DRC
  results are not valid evidence of the intended geometry. The builder now
  uses native `pdiffc`/`ndiffc` and explicitly flags layout-read errors.
- Corrected run `20260906T224744923280Z` has no unrecognized-layer errors
  and DRC 0, but LVS still fails: 26 nets extracted versus 30 in the reference.
  Four capacitor devices and the original transistor dimensions are extracted,
  but capacitor top terminals attach to the wrong internal nets. No transient
  is authorized by these failing physical results.
- Read-only geometry inspection identifies preexisting local-interconnect
  crossings at all proposed contacts: local cell rectangles
  (517,438)-(688,472), (935,433)-(1062,467), (537,73)-(616,107), and
  (958,73)-(1062,107). Adding contacts merges floating diffusion nodes into
  the crossed nets. Earlier signal routing also crossed a capacitor bottom-
  plate access; elbow routing removes that separate mistake. An M1 escape
  was added for the low-node contact near the existing M2 data route.
- Next: redesign contact access by rerouting existing local interconnect or
  expanding/rebuilding the capture cell; do not keep adding vias atop crossed
  wires. Keep the known-good 40-device extraction and schematic MIM experiment
  separate. Current attempted layout is explicitly failing and must not replace
  the accepted physical source. No converter or hardware gate is closed.

### Four modeled MIM capacitors coupled to capture

- Previous turn classified as progress: established native capacitor geometry
  and nominal model. Run `latch-capture-integration/20260906T224013473263Z`
  now adds four installed 2x2 um MIM models (about 9.302 fF each nominal) and
  their model series resistances at the four internal stack nodes. This is
  schematic integration with the unchanged 40-device extraction, NOT a newly
  LVS-verified combined layout. Capacitor routing/substrate parasitics remain
  omitted. Both the source and modified netlist are retained and hashed.
- At 5 ps / reltol 1e-5, baseline clocks and external loads, all four D/Q
  logic windows pass. Targeted high-node maxima are 1.833627/1.827416 V;
  low-node minima -0.031873/-0.030928 V. Q still spans -0.050977 to 1.893715 V.
  The strict all-saved-node envelope still fails. Eight internal capacitor
  model nodes are also saved; no hidden reduction in observable coverage.
- Terminal audit `latch-terminal-audit/20260906T224244839483Z` covers all
  40 MOS devices and separately checks the four capacitor connections/count.
  Maximum gate-to-any-terminal voltage is 1.945235 V, but reverse-bias range
  flags persist. This scalar is not model or reliability qualification.
- Interpolated 50% capture-clock-to-Q delays for changing-output cycles 1/2/3
  are 0.279117/0.272244/0.279118 ns, versus baseline
  0.267341/0.262287/0.267342 ns. Whole retention windows also pass; this is
  nominal sampled timing, not setup/hold or PVT signoff.
- Energy comparison `latch-supply-energy/20260906T224250361580Z` uses
  matched baseline `20260906T222005025070Z`. Nonstartup VDCAP net energy
  increases 88.842 to 125.738 fJ/cycle. All independent ideal-source net
  energy increases 3347.239 to 3384.137 fJ/cycle; this excludes actual clock/
  bias-driver losses and is NOT hardware or total inference energy.
- All 33 latch tests passed after adding modeled capacitor vector selection;
  six terminal-auditor tests also pass. New runs now snapshot capacitor
  preflight metadata; the completed run predates that extra snapshot but
  records its source path and all included model hashes. Energy reports now
  carry nested solver and implementation-boundary metadata explicitly.
- Next: route four verified capacitor cells into a new combined layout with
  explicit substrate connectivity, then rerun DRC/LVS/extraction and these
  voltage/timing/energy checks. Residual Q/receiver excursions and physical
  clock/bias generation remain unresolved; converter and hardware gates open.

### Native MIM capacitor physical/model boundary

- Previous turn was progress: four ideal internal capacitors reduced targeted
  peaks. This turn establishes a drawable/model-backed part instead of
  assuming the ideal 1 fF component exists physically.
- `build_capture_charge_cap.py` uses the installed native MIM drawer. The
  preferred standalone result `capture-charge-cap/20260906T223826369432Z`
  has DRC 0 and unique LVS match to independently specified top/bottom ports
  and one `sky130_fd_pr__cap_mim_m3_1 l=2 w=2` device. Tool, setup, PDK,
  geometry, extraction and reference hashes are recorded. Earlier unlabeled
  probe `20260906T223531749389Z` was extraction-only; labeled source
  `20260906T223618590469Z` also passes DRC/LVS but has stale generic boundary
  prose saying no capacitor LVS. Use its actual LVS log/field; the preferred
  rerun corrects that prose and adds Netgen/setup provenance.
- `run_capture_charge_cap_model.py` verifies the labeled source and follows
  installed RC/model include dependencies recursively. Nominal 0-to-1 V
  charge probe result `capture-charge-cap-model/20260906T223811603512Z`
  measures 9.302259 fF, agreeing within 0.0001 fF with the inspected nominal
  area/perimeter/dimension-correction formula (9.302250 fF). This is a model
  simulation, not measured silicon, and includes the model's series resistors.
- The model probe uses the capacitor reference, not extracted parasitics.
  Standalone extraction additionally contains 0.46782 fF plate coupling and
  0.16967/0.76275 fF top/bottom-to-VSUBS terms. VSUBS is currently implicit
  and must be bound explicitly in any integrated simulation/layout.
- Next: test four such modeled capacitors at the internal stack nodes,
  preserving strict implementation labels, then assess decision delay, energy,
  all-node voltage and physical routing feasibility. The approximately 9.3 fF
  device cannot inherit results from the earlier ideal 1 fF experiment.
  Combined layout, full converter and end-to-end hardware gates remain open.

### Internal charge-cap schematic experiment

- Previous goal turn classified as progress: data-load intervention changed
  the internal peak without removing it. Added an opt-in schematic experiment
  with four 1 fF ideal capacitors: high internal stack nodes a_1561_36413# /
  a_1975_36413# to vdd_capture; low stack nodes a_1592_36047# /
  a_2017_36047# to vss. This is NOT an extracted-layout revision.
- Run `latch-capture-integration/20260906T223123390068Z` completes at 5 ps /
  reltol 1e-5, baseline 100 ps capture edges and 2 fF receiver load. All four
  D/Q logic windows pass; strict waveform envelope fails. High-node maxima
  become 1.958021 and 1.959223 V (first was 2.111209 V); low-node minima
  become -0.121585 and -0.116624 V. Q still spans -0.054725 to 1.900950 V.
  Thus added internal capacitance reduces the targeted excursion but leaves
  other failures and is not a complete solution.
- Exact source/deck comparison verifies the only electrical change is the
  four added capacitors. Source extraction is copied and hashed separately.
  `combined_layout_lvs_verified` is false for the modified circuit;
  `source_combined_layout_lvs_verified` records the unchanged source evidence.
  Terminal audit now carries the source implementation boundary explicitly.
- All 33 latch tests pass, including preservation of all transistor lines,
  exact cap terminals and rejection of duplicate/unsupported interventions.
  Simulation and audit completed.
- Physical feasibility is unresolved: the installed Magic PDK capacitor
  generator (`libs.tech/magic/sky130A.tcl`) gives MIM defaults/minima of
  2 by 2 micrometres and default value 8.0, with an explicit work-in-progress
  warning. Do not infer a realizable 1 fF MIM part from this ideal experiment.
  Next: evaluate a modeled, physically drawable capacitor or alternative
  charge-control topology, including delay/energy and all-node effects,
  then obtain new DRC/LVS/extraction before any physical claim.

### Controlled data-load intervention

- Previous turn classified as progress: clock-fall intervention separated one
  event from the remaining internal excursion. This turn varies only external
  CRXn from 2 to 20 fF; added load is lumped diagnostic capacitance, not a
  DRC/LVS-proven layout modification. The existing 40-device extraction is
  unchanged. Runner now records the explicit external load in its contract.
- Run `latch-capture-integration/20260906T222807181791Z` completes at 5 ps /
  reltol 1e-5, 100 ps capture rise/fall. Four D/Q windows pass, strict voltage
  envelope fails. Exact deck comparison confirms CRXn is the only changed
  electrical element versus `20260906T222005025070Z`; circuit hashes, models,
  solver and clocks match.
- New `analyze_capture_data_transition.py` retains all directional threshold
  crossings (rather than choosing a favorable edge), rejects unsupported
  profiles and verifies source/waveform hashes. Baseline report:
  `capture-data-transition/20260906T222857204579Z`; loaded report:
  `capture-data-transition/20260906T222906322192Z`.
- In cycle 2, the data fall 90-to-10% duration increases 0.530032 to
  0.787669 ns. Internal a_1561_36413# peak moves from 112.148866 to
  112.483851 ns and drops 2.111209 to 2.093649 V. Rising data transition
  duration increases approximately 0.921 to 1.598 ns. This supports a data-
  coupling contribution but does not isolate individual intrinsic capacitances
  or establish timing/reliability qualification. The load change is not a fix.
- All 32 latch unit tests pass, including directional interpolation and
  ringing/missing-edge handling. No acceptance thresholds changed.
- Next: evaluate an internal charge-control or capture-topology revision,
  explicitly separating exploratory schematic modifications from the current
  LVS-proven extraction. More external loading alone is not justified by the
  measured residual peak and slower data transition. Full converter, physical
  drivers, array/workload integration and hardware proof remain open.

### Controlled capture falling-edge intervention

- Previous turn was progress: numerical refinement reproduced voltage failures.
  Added independent `--capture-fall-ps` control that preserves rising/falling
  50% crossings at 20.05/25.15 ns. Tests check all nine rise/fall combinations.
- At unchanged 5 ps maximum step / reltol 1e-5 and identical extracted circuit,
  a 500 ps fall run `latch-capture-integration/20260906T222503952859Z` completes
  with all four D/Q logic windows passing and strict voltage envelope failing.
  Compare against 100 ps fall run `20260906T222005025070Z`, not a different
  solver profile.
- The largest gate-to-any-terminal bias drops from 1.958525 to 1.948427 V.
  Internal a_1466_36413# maximum drops 1.953579 to 1.917609 V. However,
  a_1561_36413# remains at 2.111209 V and Q extrema remain approximately
  [-0.054941, 1.900191] V. This intervention affects one clock-related event
  but does not remove the broader voltage issue or qualify any converter.
  Terminal audit: `latch-terminal-audit/20260906T222548874464Z`.
- Extended excursion localization to all saved nodes (opt-in): baseline 2.5 ps
  event report `latch-receiver-excursions/20260906T222535822143Z`.
  Coincident voltages remain observations, not causal proof.
- Controlled comparison artifact `capture-solver-comparison/20260906T222646017635Z`
  verifies unchanged source artifacts, models, solver settings and full deck
  except the explicitly checked capture pulse. A mixed-solver negative control
  is rejected. All 30 latch unit tests pass; simulations/audits completed.
- Next: investigate data-driven internal-node charge coupling independently
  of the falling clock. Do not claim overall voltage closure from the reduced
  maximum gate-terminal scalar; the remaining internal excursions are larger.

### Numerical refinement and event localization

- Previous goal turn classified as progress: new internal coverage exposed
  failures hidden by output logic checks. This turn adds time/phase and
  coincident control voltages to terminal peak evidence, plus timestamped
  bias extrema. Baseline event audit: `latch-terminal-audit/20260906T222059884186Z`.
- Same 40-device circuit and unchanged 100 ps capture clock: 5 ps maximum
  timestep / reltol 1e-5 run `latch-capture-integration/20260906T222005025070Z`
  and 2.5 ps / reltol 1e-5 run `20260906T222135875199Z` both completed.
  Both pass four D/Q logic windows and fail the unchanged voltage envelope.
  Q extrema are [-0.054941, 1.900191] V and [-0.057112, 1.904055] V;
  the a_1561_36413# peak is 2.111209 and 2.112226 V, respectively.
  Refinement reproduces the excursions, but is not a declared convergence
  or reliability qualification. Baseline-to-5 ps Q peak changed about 29 mV;
  5-to-2.5 ps changes about 3.9 mV.
- The 5 ps terminal audit `latch-terminal-audit/20260906T222124549689Z`
  places largest gate-to-any-terminal bias (X13, 1.958525 V) at 125.271 ns,
  cycle phase 25.271 ns, after the capture-clock fall. Separate internal
  rail excursions occur around phase 12 ns, before the capture rise.
  Timing correlation does not by itself establish a causal mechanism.
- `compare_capture_solver_runs.py` checks source hashes, waveform identity,
  unchanged models and normalized full decks before comparing extrema.
  Three-run evidence: `capture-solver-comparison/20260906T222349389414Z`.
  Negative control with changed capture rise is correctly rejected.
  All 29 latch unit tests pass. Numerical controls and timeout are now recorded
  in each new integration contract.
- Next engineering investigation: distinguish data-driven internal charge
  coupling from capture-clock-fall coupling, then implement/test physical
  driver or isolation changes. Do not relax voltage acceptance or promote
  this nominal logic diagnostic to converter qualification.

- Added all 11 extracted capture-internal voltage vectors to the 40-device
  integration runner. Instrumented 100 ps baseline
  `latch-capture-integration/20260906T221205894695Z` passes four D/Q logic
  windows, but internal nodes span approximately -0.233 to 2.106 V.
- Added a capture-rise control preserving the 20.05 ns rising 50% crossing
  and falling-edge start. The 500 ps experiment
  `latch-capture-integration/20260906T221352105767Z` also passes four D/Q
  windows. Q undershoot improves from -46.02 to -38.76 mV, while Q overshoot
  worsens from 1.87079 to 1.88471 V. Internal peak remains 2.10647 V.
  Neither profile passes the unchanged strict node envelope; do not adopt
  slower slew as a demonstrated fix.
- Extended terminal auditor to all 40 devices, with exact model-family counts,
  hierarchical internal-vector resolution, model-file hash checks, and verified
  installed special-NFET wrapper provenance. Retrieved the separate official
  HVT PMOS model-range source; these are model-validity diagnostics, not
  reliability limits or damage findings.
- Terminal audit snapshots `latch-terminal-audit/20260906T221826550652Z`
  (100 ps) and `20260906T221849600101Z` (500 ps) both retain range flags.
  Maximum absolute gate-to-any-terminal bias is about 1.95509 V in both.
  Full sampled terminal values, orientation-normalized diagnostics, durations,
  source documents and hashes are retained in each result.
- Terminal-auditor tests: 5/5 passing. Capture runner/layout tests previously
  passed after adding the new vector and phase-preserving slew controls.
  Both simulation processes and both audits completed; no jobs left running.
- Next: localize flagged terminal events to capture/reset phases and check
  numerical convergence before selecting a circuit/driver revision. Physical
  drivers, converter closure, broader PVT/mismatch and circuit-to-workload
  integration remain open. Held-out workload data remains unscored.

## Recovery

- Both user-designated folders are in the `ai-hardware-analysis` Git repository.
- Recovered HEAD: `3e873b3`; initial repository status counted 131 tracked changes
  and 1,823 untracked paths. These predate this plan and are preserved.
- No active `ngspice` or `run_sky130` process was found during recovery.
- Existing status prose mixes candidates and historical results. Use named
  evidence artifacts and run provenance rather than a page's broad pass label.
- Latest physical candidate is the eleven-device isolated frontend/active-load
  latch. Its saved report covers DRC/extraction, not integrated transient or LVS.

## Current work

M0 is active. The execution plan is written. The first fresh baseline is
`evidence/aimc-hardware-lab/recovery-baselines/20260906T192525327390Z/`.
It contains a scoped file/hash manifest, Git state, and individual check logs.
Portfolio and project validation, ngspice/Yosys version probes, and actual
AIHWKIT/CrossSim imports passed. The backend measured-evidence check failed on
a stale sibling path outside this repository; that path is now repaired.
Numerical workload and converter acceptance targets remain open under M1.
The full end-to-end goal is not complete.

After the path repair, baseline
`evidence/aimc-hardware-lab/recovery-baselines/20260906T192609283268Z/`
passes all six checks. Fresh probes report ngspice 36 and AIHWKIT 1.1.0;
CrossSim imports from the dedicated simulator virtual environment. This is
not a full software-regeneration run or a physical circuit rerun. The baseline
runner is `python3 scripts/capture_hybrid_inference_baseline.py`; it creates a
unique directory and never regenerates the existing physical evidence.

Netgen is installed at `/home/mehtama1/eda-tools/netgen-1.5/bin/netgen` even
though it is not on PATH. Do not infer tool absence solely from PATH probes.

## Critical recovered connectivity defect

Inspection of
`labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_isolated_frontend_active_load_latch_extracted.spice`
shows no distinct `out_p` or `out_n` subcircuit ports. Devices X1, X5, and X7
have drain/gate/source all on `tail`. This contradicts the implication of the
saved physical report's named-label checks: label presence and device count
do not prove electrical net separation. The eleven-device candidate is not
ready for meaningful transient qualification. Preserve the recovered netlist
and strengthen connectivity acceptance before repairing layout routing.

## Repaired v2 sub-block (2026-09-06)

The original candidate remains unchanged. A separate
`sky130_isolated_frontend_active_load_latch_v2` now has:

- the second isolation output connected to the actual x=2560 input gate,
  instead of the x=3560 feedback gate;
- separated metal4 handoff routes with a detour around existing feedback;
- the unused isolation-cell metal2 strip removed from this composition so
  the added vias cannot short its P/N outputs;
- physical substrate/precharge-well ties and an exposed active-load supply.

Fresh physical checking reports zero DRC errors, all eleven intended transistor
connections, and correct body ties. The checker now requires the terminal graph,
not merely `.ext` label presence. Five negative-control/unit cases pass,
including rejection of the original extracted candidate, a merged output,
a wrong gate, and a floating body, while allowing MOS source/drain reversal.

Netgen matches eleven devices and thirteen nets uniquely against the independently
written `spice/sky130_isolated_latch_v2_reference.spice` under the analog lab.
The retained run is
`evidence/aimc-simulator-adapters/isolated-latch-v2-lvs/20260906T193116440268Z/`.
It includes layout and original extracted-netlist snapshots, schematic, hashes,
setup hash, logs, and result. The LVS view omits parasitic capacitors only;
the original extraction retains them for transistor simulation. The first LVS
attempt with parasitic caps included is retained as a failed run, not discarded.

The first bounded full-Sky130 transient from that snapshot tested ±0.5 mV
inputs at 0.9 V common mode, with external ideal 100 kohm loads and 4 uA bias.
Both cases timed out at 30 seconds without measurements. Evidence:
`evidence/aimc-simulator-adapters/isolated-latch-v2-transient/20260906T193245512527Z/`.
This is a bias/testbench diagnostic, not integration of the full sampled
frontend. The instrumented repeat at
`evidence/aimc-simulator-adapters/isolated-latch-v2-transient/20260906T193418176879Z/`
also timed out in both cases with empty simulator logs. The timeout phase is
still unresolved; no transient process remains live from either completed run.

Reproduction commands from the EDA root:

```bash
python3 scripts/test_isolated_latch_connectivity.py
python3 scripts/run_sky130_isolated_frontend_active_load_latch_physical_check.py
python3 scripts/run_isolated_latch_v2_lvs.py
python3 scripts/run_isolated_latch_v2_transient.py evidence/aimc-simulator-adapters/isolated-latch-v2-lvs/20260906T193116440268Z
```

These are bounded sub-block results. M2 remains open until transistor behavior
and the actual frontend signal handoff meet the frozen engineering contract.

## Model-loading isolation and actual transistor results (2026-09-06)

The timeout was reproduced before simulation in a resistor-only deck that
loaded the complete Sky130 TT library. The resistor without that library ran
in about 0.03 seconds. Loading the PDK-provided `.spiceinit` alone did not
resolve the full-library timeout. No latch convergence conclusion follows
from those earlier timeouts.

The scoped device-model setup now uses the exact TT NFET/PFET model and mismatch
files referenced by `corners/tt.spice`, the common scale/parameter header from
`all.spice`, and its LOD parameters. It loads the PDK's own `spinit` locally.
Only the two device classes actually present in the LVS netlist are selected;
BSIM models and extracted transistor dimensions are unchanged. An intermediate
missing-scale test and a missing-PFET-LOD-parameter test were rejected and retained.
The completed minimal startup probe is
`evidence/aimc-simulator-adapters/model-startup-probe/20260906T193810789423Z/`.
The full library's precise loading bottleneck remains undiagnosed; it does not
prevent simulation of this candidate with its explicit dependency set.

Fresh transistor experiments all use the same passing LVS snapshot:

| Run under `isolated-latch-v2-transient/` | Setup | Result |
| --- | --- | --- |
| `20260906T193913444867Z` | Extracted, 100 kohm loads, ±0.5 mV | Both measured, correct final sign, only -0.259/+0.125 mV output; insufficient swing |
| `20260906T193942806397Z` | Extracted, 560 kohm loads, ±0.5 mV | Both measured; both resolve positive near 1.79 V differential; negative input fails |
| `20260906T194026110395Z` | Extracted, 560 kohm loads, ±10 mV | Both measured; output remains positive for both signs |
| `20260906T194026194226Z` | Independent schematic, 560 kohm, ±0.5 mV | Both measured; output sign opposite to the declared convention; no passing polarity claim |
| `20260906T194149500549Z` | Extracted, 560 kohm, tail enabled at 7.8 ns before reset releases at 8 ns | Both measured; output still pinned positive; peak output about 1.811 V on 1.8 V supply; rejected |

The preamp output at 100 kohm is around 1.6 V; 560 kohm moves it near 0.68 V
and restores regeneration, but not reliable polarity. Raw schematic waveform
inspection shows a startup overshoot around 2.315 V at the original evaluation
timing. Timing overlap reduces the extracted peak but does not remove the
polarity failure. This is evidence for investigating startup/asymmetry and
decision sequencing, not justification to flip the expected output sign.

The transient harness now checks final polarity, swing, and whole saved-waveform
node voltage extrema separately. Earlier `pass` flags covered final sign/swing
only and cannot stand in for the stronger voltage gate. Each run retains the
deck, input configuration, model-file hashes, selected schematic/extracted view,
LVS source hash, logs, and raw waveform. Loads and bias remain ideal external
testbench components; none of these results closes the converter gate.

## Startup and parasitic isolation follow-up (2026-09-06)

Raw trajectories show that the extracted circuit develops about 30 mV output
difference by 7.9 ns and 121 mV by 8 ns when evaluation starts at 7.8 ns.
The sign is the same for ±0.5 mV input. The corresponding frontend differential
is then disturbed toward the same sign. The bias develops during tail discharge,
before a useful input-dependent decision is established.

Additional bounded diagnostics under `isolated-latch-v2-transient/`:

| Run | Controlled change | Outcome |
| --- | --- | --- |
| `20260906T194356323320Z` | Add one schematic PMOS output equalizer during reset | Both measured; still pinned positive; rejected |
| `20260906T194422942651Z` | Intermediate 350 kohm load; ±0.5 and ±10 mV | All four measured; still pinned positive; rejected |
| `20260906T194526896574Z` | Two-device transmission-gate equalizer, independently released at 10 ns | Both measured; pinned positive; tail undershoot about -10 mV; rejected |
| `20260906T194600679149Z` | Remove only explicit extracted capacitors; retain all MOS terminals, sizes and junction properties | Both measured; opposite decisions for opposite inputs, but reversed from declared polarity and above supply; rejected |

The equalizers are schematic additions, not LVS-verified additions to the
physical candidate. The no-capacitor run is a diagnostic ablation, not extracted
acceptance. Its result identifies interconnect capacitance as a contributor to
the one-sided decision under this setup. It does not establish that balancing
capacitance alone will fix polarity, clock feedthrough, or voltage legality.

The harness records these changes explicitly, including the simulated netlist
hash and capacitor removal count. The original extracted netlist is unchanged.
`--view device-only-extracted` must never be promoted as a physical pass.

## Extraction-mode correction (2026-09-06)

The next layout revision was deferred after a same-geometry export comparison
found that the supposed capacitance imbalance was partly an extraction-flow
artifact. In the raw `.ext`, out_p/out_n substrate capacitances are
15.1647/16.2693 fF. With `ext2spice lvs` followed by `cthresh 0`, hierarchical
export emitted 12.23545 fF on out_p and no out_n-to-vss capacitor. Turning
hierarchy off restored the raw values for both outputs. Default flat export
agreed. The geometry and device terminals were unchanged across these cases.

The four-mode comparison is retained at
`evidence/aimc-simulator-adapters/extraction-consistency/20260906T195017682114Z/`.
Commands, copied geometry, raw extraction, SPICE exports and tool logs are
available per mode. An initial missing-PDK-environment run was rejected.

The physical checker now explicitly uses flat export with a subcircuit wrapper
and compares both exported output capacitances to the raw extraction. The new
negative control rejects an omitted output capacitor. Six tests pass.
Magic documents that its LVS preset enables hierarchical export; this flat
candidate therefore requires an explicit override for the validated export flow:
[Magic ext2spice reference](https://www.opencircuitdesign.com/magic/commandref/ext2spice.html).
This observation is specific to the tested cell/tool setup, not a general
claim that all hierarchical extraction is invalid.

Fresh DRC, terminal-graph checks, capacitance consistency, and Netgen LVS pass.
The corrected snapshot is
`evidence/aimc-simulator-adapters/isolated-latch-v2-lvs/20260906T195121917566Z/`.
Use this snapshot for new experiments; the earlier one remains historical.

Corrected extracted transients at 560 kohm and evaluation at 7.8 ns:

- `isolated-latch-v2-transient/20260906T195143370541Z/`: both inputs now
  resolve negative at approximately -1.795 V differential; only the negative
  input has correct polarity; output overshoot still reaches about 1.813 V.
- `isolated-latch-v2-transient/20260906T195225694931Z/`: independently timed
  schematic transmission-gate equalizer still resolves negative for both
  signs and introduces roughly -8 mV tail undershoot. Rejected.

The previous claim that routing alone caused the one-sided decision was too
strong: export settings materially change its direction. The corrected circuit
still needs startup/polarity and parasitic-balance repair, but changes must now
be based on the validated export, not the missing-capacitance artifact.

## M1 real-workload start (2026-09-06)

To connect the circuit work to an explicit task, the first engineering
demonstrator is now the UCI optical handwritten-digit classifier. Its
preregistered contract and preparation code live in the sibling project:
`analog-in-memory-ai-inference/software-architecture/experiments/optdigits-v1/`.
The original writer-disjoint test population is retained. Only the official
training population was split, trained on, or scored for calibration.

The contract declares a fixed 64–32–10 ReLU MLP, first-projection analog
candidacy, digital output/control, a minimum 95% digital test accuracy,
at most one percentage point hybrid accuracy loss, and comparative energy,
latency and fallback targets. These targets were written before training and
are engineering hypotheses, not customer requirements. Array technology,
qualified converter profile, absolute device budgets and board setup remain open.

Initial preparation run `20260906T195549986562Z` uses 3,062 training and 761
calibration rows. Calibration accuracy is 96.98%; ONNX and NumPy outputs agree.
The 1,797-row official test file is archived and hashed but remains unscored.
Source data is attributed and pinned by SHA-256. The training procedure is
fixed final-epoch Adam; there was no hyperparameter selection using test results.

The existing backend successfully analyzes this actual ONNX model: five
operators, two matrix operations, unique operator identities. Its placement
proposal is saved under that run. It is not contract-specific target lowering
or hardware authorization; its heuristic cost fields remain estimates.

A second preparation run, `20260906T195750363771Z`, verified the pinned
downloads and reproduced the identical ONNX model hash
`1bed25ce66c60420209fc25c379497ac7f3b588c98db3cf8a4eac971079d72d3`.
It also records the training-script and split hashes. Test scoring remains off.

## M1 shared compiler and executable software fallback (2026-09-06)

The frozen real-data model now runs through the shared target compiler and
review-command decoder, with explicit activation/output shapes and bounds-checked
SRAM allocations. The new `scripts/run_optdigits_compiled_fallback.py` verifies
the model, contract, data and calibration-split hashes before lowering all five
operators. Compiler and reference-runner entry points accept isolated output
directories without replacing the legacy evidence.

Latest provenance-recorded result:
`evidence/aimc-hardware-lab/optdigits-compiled-fallback/20260906T200500785965Z/execution_result.json`.
All 761 calibration records preserve ONNX reference classifications; maximum
logit difference is 5.7220458984375e-6 and calibration accuracy is 96.98%.
The package contains five commands, 1,408 allocated SRAM bytes and 15 planning
cycles. These are not measured device cycles or performance results. Source
scripts, compiled artifacts and the failed extracted-latch gate are hashed.

The first projection remains 100% digital fallback. Both extracted latch cases
fail the combined polarity/voltage gate. Weights reside in host memory and
NumPy implements digital operations; this is not firmware or physical execution.
The official test set remains unscored. A separate isolated legacy compilation
preserved all 321 runtime commands, 460 register writes and 687 planning cycles,
and passed the shared bytecode reference check.

## Parasitic symmetry and bias counterfactual (2026-09-06)

The corrected extracted baseline shows roughly 11.6 mV output imbalance by
7.85 ns for either input sign, soon after evaluation starts at 7.8 ns. Its
output-to-substrate capacitances are 15.1647/16.2693 fF and its latch-input
substrate capacitances are 6.9417/9.45522 fF. Other coupling terms differ too.

Added `--view symmetric-cap-diagnostic` to the transient runner. It averages
every capacitor edge with its polarity-mirrored counterpart, including the
two floating metal nodes. Missing counterparts count as zero. Total explicit
capacitance is conserved and every MOS statement is unchanged. Two unit tests
verify averaging, missing counterparts, unchanged device text, idempotence and
rejection of unexpected units. This artificial network is explicitly marked
as modified parasitics and not a combined LVS-verified circuit. It cannot
qualify hardware or replace the actual extracted baseline.

Diagnostic runs under `evidence/aimc-simulator-adapters/isolated-latch-v2-transient/`:

- `20260906T200645026022Z`: 560 kohm, evaluation 7.8 ns; all four
  inputs (-10, -0.5, +0.5, +10 mV) produce mirror-symmetric but reversed
  polarity. Output overshoot reaches 1.81113 V. All fail.
- `20260906T200724503852Z`: same 560 kohm, evaluation 8.2 ns;
  both ±0.5 mV decisions remain reversed and overshoot worsens to 1.87848 V.
- `20260906T200736862102Z`: 350 kohm, evaluation 7.8 ns;
  both ±0.5 mV decisions now have correct polarity and ±1.23777 V output
  differential. Both still fail waveform legality, peaking at 1.81113 V.

These controlled comparisons support pursuing physical parasitic balance at
350 kohm, not assuming symmetry alone repairs the 560 kohm operating point.
They do not prove that a realizable layout will reproduce the artificial
network. Supply/reset feedthrough legality remains a separate acceptance issue.
The real-workload analog gate remains unchanged and closed.

## Real paired-row layout revision (2026-09-06)

Added `scripts/build_balanced_isolated_latch_candidate.py`: a fresh 11-device
layout with mirrored paired rows, paired source buses, body contacts and
shorter local input routing. Each run is isolated; the preserved v2 geometry
and extraction remain untouched. It uses the same independently authored
device schematic and does not replace capacitors after extraction.

The first generated layout was DRC-clean but failed connectivity because its
VSS route crossed the tail bridge on M3. Moving that crossing onto M2 repaired
the short. This is another example of why DRC alone is insufficient.

Primary physical candidate:
`evidence/aimc-simulator-adapters/balanced-latch-layout/20260906T201157518366Z/`.
Zero DRC errors, correct MOS terminal graph and body ties, and consistent
output-capacitance export. Layout/extraction/log hashes are recorded. Output
substrate capacitances are 19.9895/19.8461 fF (~0.72% mismatch versus ~7.03%
in the preserved v2). Latch input substrate capacitances both equal 7.56409 fF.
This does not establish total parasitic symmetry or matching yield; common
tail capacitance increased to 42.4589 fF.

Independent Netgen LVS passes uniquely against the unchanged reference:
`evidence/aimc-simulator-adapters/isolated-latch-v2-lvs/20260906T201207097774Z/`.
The LVS runner now accepts `--candidate-dir`, requires physical preflight and
layout/extraction hash agreement, and retains the candidate report and log.

Actual extracted transients, 350 kohm load, evaluation at 7.8 ns:

- `isolated-latch-v2-transient/20260906T201218068247Z/`: both ±0.5 mV
  inputs produce correct polarity, but differentials are -0.138605/+1.053788 V.
  The negative case fails the 0.5 V margin. Maximum voltage is 1.801064 V,
  so both fail the unchanged full-waveform voltage gate.
- `isolated-latch-v2-transient/20260906T201336793688Z/`: increasing ideal
  reset/evaluation rise time from 20 ps to 200 ps gives -0.115235/+1.053514 V
  and a maximum 1.800437 V. Still fails; slew alone does not repair the margin.
  `--clock-rise-ps` records this diagnostic setting explicitly. Ideal clocks
  are not extracted clock-driver evidence.

An alternate crossover ordering was also built, at
`balanced-latch-layout/20260906T201257028887Z/`. Physical preflight passes,
but output capacitances remain 19.9901/19.8456 fF: no useful improvement.
That variant has not undergone LVS/transient and is not preferred over the
primary snapshot. The generator currently contains this alternate ordering;
use the explicit primary LVS snapshot above to reproduce measured results.
Future generation now archives the generator source as well as its hash.

Eight connectivity/counterfactual unit tests and syntax checks pass. No
converter or workload analog gate was promoted. These results justify further
physical branch-balance and regeneration work, not a claim of hardware success.

## Matched feedback stubs and separate precharge rail (2026-09-06)

Controlled diagnostics confirmed that the remaining small parasitic imbalance
still matters. At 350 kohm, the primary paired-row netlist with artificially
averaged mirrored capacitors gives ±0.939565 V decisions, both meeting polarity
and margin but failing the voltage gate. This diagnostic is
`isolated-latch-v2-transient/20260906T201538159443Z/`.
Actual extracted runs at 400 kohm (`20260906T201522858503Z`) and 450 kohm
(`20260906T201524187208Z`) resolve positive for both signs. They are rejected;
increasing resistance is not the physical fix.

The new physical revision retains equal M3 gate-stub length on both sides,
including a dead-end extension on each lower crossover landing. This is actual
metal geometry, not post-extraction capacitance editing. Candidate:
`balanced-latch-layout/20260906T201600126881Z/`, with archived generator source,
zero DRC errors, correct connectivity/body ties, and consistent capacitance
export. Output substrate capacitances are 20.0444/20.006 fF (~0.192% mismatch).
Its unchanged independent reference passes Netgen LVS in
`isolated-latch-v2-lvs/20260906T201610493967Z/`.
Use this as the current preferred physical snapshot.

Actual extracted run `isolated-latch-v2-transient/20260906T201621936740Z/`,
350 kohm/evaluation 7.8 ns, now gives -0.948962/+0.922322 V for ±0.5 mV:
both polarity and margin pass. The maximum remains 1.801058 V, so waveform
legality still fails the unchanged 0..1.8 V gate.

The existing layout already separates precharge and active-load supply ports.
Added `--precharge-v` to the diagnostic runner and held active/sense-load
supplies at 1.8 V while testing a 1.75 V precharge rail. With default 1.8 V,
voltage behavior remains equivalent, but sense-load current now appears under
VACTIVE rather than VDD; do not compare individual source-current columns
across that runner change as though their partition were unchanged.
The reduced rail is an ideal external supply, not an implemented regulator.
The report explicitly records unverified rail generation. No voltage limit
was relaxed and no clipping was added.

- `isolated-latch-v2-transient/20260906T201700874750Z/`: both ±0.5 mV
  cases pass the nominal sub-block diagnostic: -0.930969/+0.904659 V
  differential and all six saved internal voltages within 0..1.8 V throughout
  the transient. Maximum output is about 1.751059 V.
- `isolated-latch-v2-transient/20260906T201722606756Z/`: eight additional
  cases at ±0.25, ±1, ±2 and ±10 mV all have correct polarity and legal
  waveforms; seven meet the 0.5 V differential margin. The +0.25 mV case
  reaches only +0.463252 V at the fixed 18 ns measurement and fails margin.

Across these two runs, 9/10 nominal cases pass the diagnostic. This is neither
a characterized offset distribution nor converter qualification. Absolute
output levels do not yet establish compatibility with a digital receiver:
for example, the +0.5 mV case's high output is only about 0.922 V at 18 ns.
Single-conversion sampling also does not prove hold time, repeated reset,
noise, mismatch, PVT, extracted clock drivers, sampled frontend integration,
or hardware rail generation. The converter/workload analog gate stays closed.
Eight unit tests continue to pass.

## Repeated reset and loaded receiver boundary (2026-09-06)

Added `scripts/run_latch_repeated_readout.py`. It preserves one continuous
SPICE state across four alternating ±0.5 mV conversions, 50 ns apart. Inputs
change during reset, five ns before the next cycle start; sampling remains
at offset 18 ns. The preregistered diagnostic additionally requires a signed
0.5 V differential throughout offsets 16..20 ns, equal precharged outputs
at offset 7.6 ns, and full-run voltage legality. Source netlist and PDK model
hashes are checked; decks, source/config, runner and hashes are archived.

All following runs are under
`evidence/aimc-simulator-adapters/latch-repeated-readout/` and use the matched
stub extraction with 350 kohm and ideal 1.75 V precharge supply:

- `20260906T202020525711Z`: original 20 ps falling edges. All four
  decisions, hold windows and reset checks pass, but the full transient fails:
  tail reaches -160.3 mV and outputs also undershoot during reset transitions.
- `20260906T202021706149Z`: two schematic CMOS inverter receivers
  (NFET 1.2/0.6, PFET 2.4/0.6 um, 2 fF output load each) added to the
  original-clock test. All four loaded hold-margin and receiver tests fail;
  both receiver outputs remain high during intended complementary readout.
  Receiver output overshoot and tail undershoot also fail voltage legality.
  This is a rejected unlaid-out receiver, not combined-layout LVS evidence.
  The chosen 0.18/1.62 V receiver-output limits are explicit engineering
  diagnostic targets, not characterized standard-cell thresholds.
- `20260906T202052609461Z`: starting precharge 0.5 ns earlier alone
  reduces but does not fix tail undershoot (-144.7 mV).
- `20260906T202150330170Z`: same 0.5 ns advance, 500 ps falling
  edges. All four decision/hold/reset checks pass; tail minimum -0.205 mV
  still fails the unchanged voltage limit.
- `20260906T202220666512Z`: same 0.5 ns advance, **1 ns falling
  edges**, no added receiver. All four repeated-cycle diagnostics pass.
  Minimum tail voltage is +9.319 mV; maximum output is 1.76737 V.
  The worst signed hold-window differential is 0.537324 V.

This establishes a nominal unloaded repeated-operation point, not a digital
readout or converter. Clock shaping is still represented by ideal sources;
driver implementation, loading, rail generation, PVT/noise and sampled DAC
integration remain open. The failed receiver cannot be inferred to work under
the revised clocks without testing it. Ten topology/counterfactual/testbench
unit tests pass. Workload analog execution remains disabled.

Reproduction of the passing repeated diagnostic (from the EDA directory):

```bash
../analog-in-memory-ai-inference/software-architecture/backend/.venv/bin/python scripts/run_latch_repeated_readout.py evidence/aimc-simulator-adapters/isolated-latch-v2-transient/20260906T201700874750Z --reset-early-ns 0.5 --clock-fall-ps 1000
```

## Stronger physical regeneration and successful nominal logic readout (2026-09-06)

The original receiver was retested with the passing repeated-cycle clock
profile (0.5 ns early precharge, 1 ns falling edges):
`latch-repeated-readout/20260906T202317503233Z/`. Readout still fails all
four cycles. Two additional schematic receiver profiles were tested:

- `20260906T202401855409Z`, compact: NFET/PFET each W/L=0.42/0.15 um.
  Latch hold margin survives all four cycles, but receiver lows remain too high.
- `20260906T202403227448Z`, skewed: NFET 0.84/0.15 and PFET 0.42/0.6 um.
  No cycle meets the full receiver readout test; two also lose latch hold margin.

These failures distinguish insufficient absolute high level from merely
excessive gate loading. The next revision increases both regenerative PMOS
widths from 1.2 to 2.4 um in **actual layout diffusion**, keeping L=0.6 um
and the other nine devices unchanged. The generator exposes the two reviewed
width choices and writes a matching independent design reference from the
declared width, not from extraction. The LVS runner verifies that reference's
hash before using it. Topology preflight remains separate from dimensional LVS.

Physical candidate `balanced-latch-layout/20260906T202539896363Z/` passes
DRC, body/connectivity and capacitance-export checks. Dimensional Netgen LVS
passes in `isolated-latch-v2-lvs/20260906T202553317062Z/`. The older 1.2 um
references and snapshots remain preserved; this is a device-sizing revision,
not evidence that the old device dimensions somehow passed a new reference.

Unloaded signed transient `isolated-latch-v2-transient/20260906T202600550851Z/`
passes both ±0.5 mV cases at the existing 350 kohm/1.75 V precharge profile.
The high output is now about 1.553 V, with differential ±1.537 V.

Loaded repeated run `latch-repeated-readout/20260906T202633366189Z/` uses
this actual extracted stronger latch plus the unlaid-out compact receivers:

- All four alternating cycles pass latch polarity, reset and 16..20 ns hold
  margin. Minimum signed differential is 1.52637 V.
- All four receiver readout windows pass the preregistered 0.18/1.62 V limits:
  correct complementary outputs, high approximately 1.8 V and low at most
  1.851 microvolt during the checked windows.
- All saved latch internal voltages remain inside 0..1.8 V throughout the run.
- **The combined diagnostic still fails full-waveform legality**: receiver
  transitions range from about -2.302 mV to 1.801615 V. The existing strict
  0..1.8 V gate is unchanged. No combined physical receiver extraction exists.

This is the first working nominal loaded logic readout, not a qualified
converter or digital interface across conditions. The receiver circuit still
needs layout, characterized loading and transient-voltage closure. Ten
existing unit tests pass. Analog workload execution stays disabled.

## Native-PDK compact receiver layout and extracted readout (2026-09-06)

Added `scripts/build_compact_receiver_layout.py`. It uses the installed
Sky130 Magic NFET/PFET drawing procedures at their 0.42/0.15 um defaults,
including native contacts and guard rings. The procedures reset their origin,
so drawing both into the same cell did not create two separated devices; that
initial primitive-only attempt is preserved at
`compact-receiver-layout/20260906T202900284088Z/` and is not accepted.
The corrected generator draws separate primitives, explicitly checks their
half-lambda grid, composes flat geometry, routes input/output and body/supply
connections, and runs DRC, extraction and independent dimensional Netgen LVS.

Verified receiver snapshot:
`evidence/aimc-simulator-adapters/compact-receiver-layout/20260906T203157079188Z/`.
Zero DRC errors; two intended MOS devices with correct gate/drain/source/body
connections; unique LVS match against a separately specified inverter
reference. Drawer, layout, extraction, source and reference hashes are recorded.
The extracted input-to-vss capacitance is 1.00905 fF and input-to-vdd is
0.38269 fF, in addition to gate/output coupling and transistor capacitance.
These parasitics were not present in the schematic-only receiver experiment.

The repeated runner now accepts `--receiver-layout`, requires its DRC/LVS
pass and matching layout/netlist/reference hashes, and retains both the
receiver extraction and physical report. It records compact dimensions and
explicitly reports ideal inter-subblock wires rather than combined-layout LVS.

Readout result:
`evidence/aimc-simulator-adapters/latch-repeated-readout/20260906T203219462598Z/`.
The actual extracted stronger latch and two instances of the actual extracted
receiver retain correct polarity, reset, latch hold margin and complementary
receiver levels for all four alternating cycles. Worst signed latch hold
differential is 1.52624 V; receiver low during the window is at most 1.546 uV.
All latch internal voltages remain legal throughout the run.

The combined test still fails the unchanged full-waveform gate because
receiver transition extrema are approximately -2.517 mV and 1.801798 V.
No threshold has been relaxed. This is two independently verified subblocks
connected by ideal netlist wires, not a combined routed extraction or a
qualified converter. Ten existing unit tests pass.

## Combined routed 15-transistor extraction (2026-09-06)

Added `scripts/build_combined_latch_receiver.py`. It verifies both source
geometry/reference hashes, converts the latch's grid explicitly to the
receiver's half-lambda grid, places two mirrored receivers between latch rows,
and physically routes their inputs, supply and ground connections. The
combined independent reference contains the 11 declared latch devices and
four declared receiver devices. No extracted MOS or capacitor value is edited.

Candidate:
`evidence/aimc-simulator-adapters/combined-latch-receiver/20260906T203539307640Z/`.
Zero DRC errors, unique independent Netgen LVS match, and consistent output
capacitance export. The output substrate capacitances are 21.5529/21.5282 fF.
Layout, extraction, reference and generator snapshots/hashes are retained.

`run_latch_repeated_readout.py --combined-layout` now verifies this candidate's
physical status, hashes and source-latch identity, then uses its single full
extraction with two external 2 fF readout loads. It does not also instantiate
schematic receivers or duplicate extracted receiver instances.

Measured result:
`evidence/aimc-simulator-adapters/latch-repeated-readout/20260906T203635608244Z/`.
All four alternating cycles retain correct polarity, precharge/reset,
16..20 ns latch margin and complementary digital readout. Minimum signed
hold differential is 1.52615 V. All saved latch internal voltages remain in
0..1.8 V, but receiver transition extrema still reach approximately -2.516 mV
and 1.801795 V. Thus the unchanged strict rail-envelope gate still fails.
Ten existing unit tests pass.

Important qualification distinction for the next audit: the strict 0..1.8 V
node-envelope diagnostic is not itself a sourced device reliability limit.
The official [Sky130 device documentation](https://skywater-pdk.readthedocs.io/en/main/rules/device-details.html)
specifies model-validity ranges in terminal differences: NFET VDS/VGS 0..1.95 V,
VBS -1.95..+0.3 V; PFET VDS/VGS -1.95..0 V, VBS -0.1..+1.95 V.
These are model-validity statements, not a blanket reliability or overshoot
waiver. Actual terminal orientations, reverse bias, duration, receiver loads
and physical operating limits need a separate audit. In particular, do not
simply replace the old node limit with 1.95 V or promote this run to accepted.
The strict diagnostic remains preserved and failed.

## Per-transistor bias audit and reset-domain correction (2026-09-06)

Added `scripts/audit_latch_terminal_voltages.py`, which verifies the exact deck
and circuit hashes, reads all saved terminal waveforms and reconstructs only
constant/PWL ideal sources from that deck. It reports VDS/VGS/VBS for all 15
devices both as netlisted and with polarity-normalized source/drain orientation.
The second view is explicitly diagnostic, not authority to extend model ranges.
Results retain waveform hashes and copies/hashes of the official NFET/PFET
model-range source pages. Outside-range durations are sampled trapezoidal
estimates, not exact crossing-time or lifetime limits.

Initial audit `latch-terminal-audit/20260906T203941667691Z/` of the combined
readout establishes that maximum absolute gate-to-drain/source/body magnitude
is 1.8 V, but not that the models or physical reliability are fully qualified.
After polarity normalization, six devices leave the published VGS ranges:
two precharge PFETs reach +0.05 V, two feedback NFETs about -3.534 mV, and
two input NFETs about -0.31909/-0.313881 V during reset. This is different
from simply labelling every tiny receiver node overshoot as device overstress.
The documented model ranges do not themselves provide a reverse-bias or
transient-reliability waiver.

Added an explicit `--reset-high-v` testbench setting and matched it to the
existing 1.75 V precharge rail. Combined repeated run
`latch-repeated-readout/20260906T204107245424Z/` preserves all four logic,
hold-margin and reset results (minimum signed margin 1.52614 V). Receiver
node excursions remain and the original strict diagnostic still fails.

Follow-up audit `latch-terminal-audit/20260906T204123230261Z/` confirms that
the two PFET reverse-gate excursions disappear. Four NFET reverse-gate cases
remain: input devices around -0.32 V, feedback devices around -3.3 mV.
All source/drain-polarity-normalized VDS and VBS checks pass; raw netlisted
orientation checks can fail because extraction reverses some S/D assignments.
Neither view is promoted to physical model/reliability signoff. The ideal
reset driver and rail still require implementation.

Three new audit tests cover explicit source/drain orientation, normalization
invariance, reverse-bias rejection despite small absolute magnitude, ideal
source reconstruction and malformed/missing sources. Thirteen unit tests pass.
No acceptance threshold or analog-execution gate was relaxed.

## Process-corner and temperature diagnostic screen (2026-09-06)

The bias-coverage gaps remain open, but do not prevent additional diagnostic
evidence. Added `--corner` and `--temperature-c` to the repeated runner. Model
selection follows the installed PDK corner selectors: NFET pm3 plus PFET
corner wrapper and its pm3 dependency, retaining the original common setup
and mismatch-disabled configuration. Actual selected model files and selector
hashes are recorded separately from the preserved source-run configuration.
No model type is substituted and all geometry remains fixed.

`scripts/run_combined_latch_corner_screen.py` freezes seven profiles before
running: TT/FF/SS/FS/SF at 27 C, plus TT at -40 C and 125 C. Rails, bias,
clock timing, reset high=1.75 V and four alternating ±0.5 mV inputs stay fixed.
Results are saved at
`evidence/aimc-simulator-adapters/combined-latch-corner-screen/20260906T204410275503Z/`.

All seven simulations completed, with all 28 conversions passing polarity,
receiver readout, 16..20 ns hold margin and reset checks. Worst hold differential
per profile:

| Process | Temperature C | Minimum signed differential V |
| --- | ---: | ---: |
| TT | 27 | 1.526139 |
| FF | 27 | 1.500349 |
| SS | 27 | 1.551133 |
| FS | 27 | 1.631557 |
| SF | 27 | 1.286132 |
| TT | -40 | 1.509658 |
| TT | 125 | 1.542169 |

All seven still fail the unchanged strict full-waveform voltage envelope.
This is a process/temperature screen, not complete PVT signoff: it omits supply
variation, process-temperature cross-product, interconnect corners, mismatch,
noise, alternate input histories and the complete sampled converter. It does
not resolve the previously documented reverse-gate model-range gaps or certify
operation at the tested temperatures. No analog gate is promoted. Thirteen
unit tests remain passing.

## Reproducible PDK mismatch and a real decision failure (2026-09-06)

The installed model files contain instance-local AGAUSS terms gated by
MC_MM_SWITCH for threshold/oxide/offset variations. Added `--mismatch-seed`
to enable these PDK terms while keeping process Monte Carlo disabled. Added
explicit nonzero input sequences for later offset diagnostics.

Initial seed initialization was NOT reproducible on installed ngspice-36.
Runs `20260906T204642918542Z`, `20260906T204657875698Z`,
`20260906T204659186915Z`, and input sweep `20260906T204735823456Z`
used startup setseed alone. Runs `20260906T204822349769Z` and
`20260906T204823818134Z` also set the startup seed variable, but still differed.
All are preserved unseeded/historical diagnostics, excluded from reproducible
offset or yield conclusions despite their recorded requested seed values.

The verified method sets the seed in the control block and then executes
`reset` before `run`, re-evaluating model random parameters deterministically.
The runner records method `startup_seed_plus_control_setseed_reset`.

Verified runs under `latch-repeated-readout/`:

- Seed 101: `20260906T204850468583Z` and `20260906T204851665179Z`.
  Their numeric waveform bytes are identical (SHA-256
  `5d8574fec606ac06462c20a031cc67c83c7179c6410d1e6376503878cded76b1`).
  Both preserve correct polarity for all four ±0.5 mV conversions.
- Seed 102: `20260906T204924644087Z` gives a different waveform and resolves
  negative for both input signs. Both positive-input conversions are wrong.

`scripts/check_latch_mismatch_reproducibility.py` verifies same-profile source
hashes, seed method, repeat identity and different-seed sensitivity. Its passing
proof is `latch-mismatch-reproducibility/20260906T205012462481Z/`.
This proves replay and sensitivity, NOT statistical yield: there are only two
distinct deterministic realizations. The strict voltage-envelope failures
also remain. Crucially, failure is now not merely a small rail excursion:
device mismatch can corrupt the decision at the tested ±0.5 mV input level.
Characterize input-referred offset and compare it with the eventual converter
LSB/calibration budget; do not claim that this sample establishes a distribution.

## Seed-102 input-referred decision bracket (2026-09-06)

Added `scripts/analyze_latch_offset_sweeps.py`. It evaluates actual stable
positive/negative receiver decisions independently of the expected input
sign, checks the entire 16..20 ns window including interpolated endpoints,
and distinguishes unresolved readout from a valid but offset decision. It
verifies source hashes and identical mismatch/corner/physical profiles across
sweeps. Two new tests cover both decision polarities and rejection of weak,
invalid or missing hold-window evidence; fifteen unit tests pass.

Using the verified seed-102 realization, coarse ascending and descending
input sequences (-20,-10,-5,-1,+1,+5,+10,+20 mV and reverse) both show stable
negative decisions through +10 mV and stable positive decisions at +20 mV.
All reset checks pass. Source runs are `20260906T205113361878Z` and
`20260906T205114834739Z` under `latch-repeated-readout/`.

Initial fine runs `20260906T205217980264Z` and `20260906T205218768562Z`
terminated at the 45-second simulator limit and are incomplete, not evidence
of a decision at any missing point. Added a bounded, recorded `--timeout-s`
option (maximum 180 seconds). Sequential reruns with a 120-second limit
completed, with the circuit, solver settings and input grids unchanged.

Completed fine sweeps:

- Ascending 10,12,14,16,18,20 mV: `20260906T205342636084Z`.
- Descending 20,18,16,14,12,10 mV: `20260906T205414366150Z`.

Both sweeps give a stable negative receiver decision at +12 mV and stable
positive decision at +14 mV, with all precharge/reset checks passing. The
seed-specific dynamic decision transition is therefore bracketed by **+12 to
+14 mV** under these tested histories. The two directions agree at this
resolution; this does not prove zero hysteresis or history independence.
Verified combined analysis:
`evidence/aimc-simulator-adapters/latch-offset-sweeps/20260906T205453207390Z/`.

This is a single realization's dynamic input-referred bracket, not DC offset,
a statistical distribution, calibrated performance, or a converter LSB result.
The full sampled DAC/comparator transfer function must be characterized before
translating this bracket into ADC code error; historical representative-code
reference settings do not establish that mapping. No analog gate is promoted.

## Frozen midpoint correction fails a new input history (2026-09-06)

Before validation, wrote `evidence/aimc-simulator-adapters/latch-calibration-contract-v1.json`:
seed 102, TT/27 C, +13 mV midpoint of the previously measured +12..14 mV
bracket, and a fixed logical validation sequence
[-2,-0.5,+0.5,+2,+0.5,-0.5,+2,-2] mV. The source bracket hash is pinned.
Added `--calibration-offset-mv` to the repeated runner. It explicitly records
logical inputs separately from physically applied differential inputs and
implements correction only through the ideal input source. No actual trim
circuit or calibration hardware is implied. Existing readout/voltage limits
and expected logical signs are unchanged.

Validation `latch-repeated-readout/20260906T205700513711Z/` passes polarity,
hold and receiver readout for seven of eight cycles, with all reset checks
passing. The sixth cycle (logical -0.5 mV, applied +12.5 mV), following
a positive decision, resolves positive and is wrong. The same applied level
earlier in the sequence, following a negative decision, resolves negative.
The frozen correction therefore fails the declared validation sequence.

Exploratory follow-up `latch-repeated-readout/20260906T205806378063Z/`
keeps +13 mV correction and all acceptance criteria fixed, but changes the
input-update setup from 5 to 10 ns before cycle start. The input transition
ends 17.78 ns before evaluation instead of 12.78 ns. The same sixth decision
still fails. This does not support attributing the failure solely to inadequate
external input settling. The follow-up is not an untouched preregistered test.

Both runs also retain receiver voltage-envelope failures. Do not select a
new correction from these validation outcomes and relabel it as a passing
frozen calibration. Characterize positive-history and negative-history
transition brackets explicitly, then define a new calibration procedure and
validate on fresh sequences. This is one simulated mismatch realization,
not calibration generalization across devices or a completed ADC error model.

Raw-offset analysis now rejects corrected input axes. Mismatch replay checks
reject differing correction or input-setup profiles. Sixteen unit tests pass,
including explicit verification of the advanced input-update timing.

## Conditioned history and longer reset experiment (2026-09-06)

Seed 102, TT/27 C, uncorrected inputs [11,12,15,12,11,12.5,15,12.5,
11,13,15,13] mV explicitly probe repeated levels after both decision signs.
At the original 50 ns period, run `latch-repeated-readout/20260906T210000496532Z/`
resolves +12.5 mV negative after a negative decision and positive after a
positive decision. All output-reset checks pass. Analysis
`latch-offset-sweeps/20260906T210045639643Z/` therefore rejects a single
transition bracket; history-conditioned brackets are [12.5,13] mV after
negative and [12,12.5] mV after positive decisions.

At the reset-check instant for these two +12.5 mV cycles, the internal
latch-sense differential is approximately 6.388 mV versus 0.737 mV.
Passing external output reset does not establish erased internal state.

Added recorded `--period-ns` (50..200 ns) to the repeated runner; evaluation
width remains 30 ns, so increasing period adds reset time rather than extending
the decision window. Input updates and measurement windows track the period.
Profile comparisons reject mixing different periods.

The same sequence at 100 ns in `latch-repeated-readout/20260906T210211453467Z/`
has no conflicting decisions at sampled repeated inputs: +12 mV is negative
and +12.5 mV positive under both tested preceding signs. Analysis
`latch-offset-sweeps/20260906T210603349084Z/` gives [12,12.5] mV.
This supports reset-duration sensitivity but does not prove history independence
between sampled levels. It doubles the comparator cycle period and changes the
transition bracket; the failed frozen 50 ns calibration remains failed.

Strict waveform voltage-envelope failures remain, and this is one mismatch
realization with ideal clocks, bias rails, and input sources. No ADC, workload,
yield, or hardware gate is promoted. Next characterize the narrower conditional
transition at 100 ns, then freeze any new calibration before fresh validation;
alternatively implement and independently verify internal-state reset circuitry.

## Finer 100 ns sweep disproves sampled history independence (2026-09-06)

Run `latch-repeated-readout/20260906T210700558153Z/` uses seed 102 and
the same 100 ns profile, probing 12.125, 12.25 and 12.375 mV after
11 mV negative and 15 mV positive conditioning decisions. All reset checks
pass. At 12.125 mV both histories resolve negative, but at both 12.25 and
12.375 mV the result follows the preceding sign. Analysis
`latch-offset-sweeps/20260906T210743959644Z/` correctly reports no single
transition bracket. The earlier coarse 100 ns result was insufficiently
resolved, not evidence of eliminated memory. No new scalar calibration is frozen.

The independent reference has output-reset PFETs but no explicit latch-sense
reset devices. Numerical refinement is being checked before attributing this
solely to circuit topology. The runner now records optional explicit 5/10/20 ps
maximum transient steps and relative tolerance 1e-4/1e-5; defaults preserve the
earlier deck. Offset aggregation and mismatch replay reject mixed solver profiles.

The analyzer now saves its source/hash and interpolated latch-sense voltages at
the declared reset-check instant. Reanalysis
`latch-offset-sweeps/20260906T211154119754Z/` records +12.25 mV reset differentials
7.04168 mV after negative and 4.93274 mV after positive conditioning. These are
observed internal-node differences, not a model proving their sole causality.

The 12-cycle refined run `latch-repeated-readout/20260906T210850292250Z/`
(5 ps maximum step, reltol 1e-5) reached the actual 180-second subprocess timeout.
It is incomplete and excluded from decision evidence. A shorter matched
baseline/refined sequence [11,12.25,15,12.25] mV is the next numerical check.

Both shorter runs completed:

- Baseline `latch-repeated-readout/20260906T211211177628Z/`, analysis
  `latch-offset-sweeps/20260906T211503959383Z/`.
- Refined (5 ps maximum step, reltol 1e-5)
  `latch-repeated-readout/20260906T211214080067Z/`, analysis
  `latch-offset-sweeps/20260906T211511006985Z/`.

Both give decisions negative, negative, positive, positive, preserving the
12.25 mV history conflict. Reset latch-sense differentials at the two probes
are 7.041681/4.932739 mV baseline and 7.041731/4.932631 mV refined. All output
reset checks pass; strict receiver voltage-envelope checks still fail. This
one numerical refinement supports a genuine modeled state-memory issue, not
full numerical convergence or physical measurement. The next circuit experiment
should introduce a separately identified internal-reset candidate, with an
independent reference and new DRC/LVS/extraction, preserving this failing
15-device baseline. Do not promote a schematic-only equalizer as extracted proof.

Twelve focused latch unit tests pass after the analysis/runner changes.

## Physically drawn internal equalizer candidate (2026-09-06)

Added opt-in `--internal-equalizer` to the combined layout generator, preserving
the original 15-device generation mode. New candidate
`combined-latch-receiver/20260906T211728514831Z/` adds a W/L=1.2/0.6 um PFET
between latch_sense_p and latch_sense_n, body tied to vdd_active, with a separate
eq_reset port. This is actual drawn geometry, not a transistor inserted only
into an extracted netlist. Independent reference specifies the added device;
Netgen reports 9 NFETs, 7 PFETs, 16 nets, unique match, and Magic reports zero
DRC errors. Output substrate-capacitance export checks pass.

Extended the capacitance audit to selected internal nodes. Read-only audit of
this same candidate matches raw .ext to SPICE: latch_sense_p 8.19727 fF,
latch_sense_n 7.80027 fF, eq_reset approximately 0.422866 fF. Future generated
equalizer candidates record and require this check directly. This is export
consistency, not independent extraction or distributed-R signoff.

The repeated runner requires explicit `--equalizer-release-ns` together with
an equalizer-bearing, verified layout. The initial diagnostic releases it at
2 ns and reapplies it with output reset near 37.5 ns, using a separate ideal
0/1.8 V source. This is not a physical clock driver. Geometry and parser profiles
are distinct from the baseline; mismatch seed 102 does NOT guarantee that old
devices receive the same variation after instance topology/order changes.

Nominal TT/27 C alternating -0.5/+0.5 mV at 50 ns period,
`latch-repeated-readout/20260906T211819331198Z/`, passes all four polarity,
full-window hold, receiver readout and output-reset checks. Strict full-waveform
voltage-envelope checks still fail. No converter gate is promoted.

New-topology seed-102 coarse sweep [-40,-20,-10,-1,1,10,20,40] mV,
`latch-repeated-readout/20260906T211850039160Z/`, gives stable negative at
+1 mV and positive at +10 mV; analysis
`latch-offset-sweeps/20260906T211939278640Z/`. This is a new realization's coarse
bracket, not offset improvement on a matched device population. Large-input
cases also show small output/tail undershoots; physical/model-bias qualification
including the added PFET remains open. Fourteen focused latch unit tests pass.

Conditioned sweep [-10,2,10,2,-10,5,10,5,-10,8,10,8] mV,
`latch-repeated-readout/20260906T212013646720Z/`, resolves +2 mV negative and
+5/+8 mV positive after both conditioning signs, with all output-reset checks
passing. Analysis `latch-offset-sweeps/20260906T212117950717Z/` brackets the
transition at [2,5] mV with no conflict on this coarse grid. At +2 mV, reset
latch-sense differential differs by about 0.00552 mV between histories; at
+5 and +8 mV, differences are about 0.00993 and 0.01371 mV. These new-topology
observations are not a matched-realization before/after comparison. Refine the
2..5 mV conditional boundary before claiming the memory issue is fixed; the
earlier 100 ns coarse-grid false reassurance is a required negative precedent.

## Equalizer fine bracket and frozen diagnostic calibration (2026-09-06)

Conditioned 2.5/3.5/4.5 mV probes in
`latch-repeated-readout/20260906T212201141313Z/` narrow the transition to
[2.5,3.5] mV. The next 2.75/3.0/3.25 mV probes in
`latch-repeated-readout/20260906T212308855172Z/` give negative at 3.0 and
positive at 3.25 mV after both conditioning signs. All reset checks pass;
no history conflict is found on this grid. Combined analysis
`latch-offset-sweeps/20260906T212347171163Z/` preserves both sweeps and hashes.
This does not establish zero hysteresis within the remaining 0.25 mV interval.

Before validation, froze `latch-calibration-contract-v2.json`: midpoint +3.125 mV,
same equalizer layout/seed 102/TT/27 C/50 ns/2 ns release, and fresh logical
sequence [-1.25,0.5,1.75,-0.5,0.75,-0.75,-0.5,0.5,-1.75,1.25,0.5,-0.5] mV.
Selection evidence and extracted-netlist hashes are pinned. The old v1 failure
is unchanged. Validation `latch-repeated-readout/20260906T212445466447Z/` gives
12/12 correct logical decisions with hold, receiver readout and reset checks
passing. Strict receiver waveform envelopes still fail (approximately
-2.71 mV minimum and 1.80172 V maximum across receivers).

Added `verify_latch_calibration_contract.py` to bind saved results to frozen
inputs, correction, timing, solver, seed method, layout and selection hashes.
It rejects profile changes and explicitly separates decision-only diagnostics
from the declared full validation. Evidence
`latch-calibration-validation/20260906T212600832138Z/` reports zero profile
mismatches, decision_only_diagnostic_pass=true, declared_validation_pass=false,
accepted_converter=false. This aggregates the runner's checks; it is not a
second waveform solver or independent physical qualification.

Extended terminal auditing to require full 16-device coverage and the intended
equalizer gate, signal terminals and body tie. Nominal equalizer run audit
`latch-terminal-audit/20260906T212255213261Z/` retains four NFET gate-bias range
flags and adds the equalizer PFET's positive VGS, reaching about +0.806335 V
after polarity normalization. Maximum absolute gate-to-terminal voltage is
1.8 V, which does not authorize extrapolating published model characterization
ranges. These remain model-coverage diagnostics, not damage claims or a
justification to relax strict node limits. Sixteen focused unit tests pass.

## Equalizer replay and receiver excursion localization (2026-09-06)

Full 12-cycle repeat `latch-repeated-readout/20260906T212725812737Z/` and
refined run `20260906T212726771793Z/` both reached actual 180-second subprocess
timeouts while run concurrently. Both are incomplete and excluded from evidence
of replay/refinement. Comparing the repeat's deck against the completed frozen
validation finds only the run-local circuit include path changed. There is no
evidence that CPU contention alone caused these timeouts.

A sequential four-cycle prefix [-1.25,0.5,1.75,-0.5] mV with the same +3.125 mV
correction completes in `latch-repeated-readout/20260906T213056297348Z/`.
Its complete numeric waveform through 170 ns is bit-identical to the original
12-cycle validation over that interval: 8775 samples x 14 vectors, SHA256
`4c00dba951f517a23cf0dde84f34f805c6c3be7e1dc53a9b3da7713fd4c54a86`.
This verifies replay of the first four decision windows, not all twelve cycles
or different-seed sensitivity in this new topology.

Added `analyze_latch_receiver_excursions.py`, with interval/serialization tests,
to preserve sampled excursion extrema, bracketing times, cycle offsets and
coincident driver/control voltages. Full original validation analysis:
`latch-receiver-excursions/20260906T213021453146Z/`; four-cycle analysis:
`latch-receiver-excursions/20260906T213204856913Z/`.

Largest undershoots occur near 8.066..8.068 ns cycle offset, immediately after
output reset releases, with the driving latch output around 1.35 V. Largest
overshoots occur during later precharge/reset, at 38.59 ns (rx_n) and 39.51 ns
(rx_p), with different driving output levels. These are coincident observations,
not yet causal proof of a specific capacitance or clock edge. No voltage limit
is relaxed. Seventeen focused tests pass.

Sequential refined four-cycle prefix `latch-repeated-readout/20260906T213155833570Z/`
also reached the actual 180-second timeout. Just before termination the process
had used about 111 CPU seconds in 172 elapsed seconds; neither numerical failure
nor CPU contention alone is established by this. Numerical sensitivity remains
unverified. Expanded the runner's explicitly requested timeout ceiling to
600 seconds (default unchanged), so refinement can receive a larger finite
compute allowance without changing circuit, solver or acceptance criteria.

In-flight refinement at handoff: `latch-repeated-readout/20260906T213539895693Z/`,
tool session 62211, observed ngspice PID 455183. Four-cycle prefix, 5 ps maximum
step, reltol 1e-5, 600-second subprocess limit. Revalidate the actual handle or
process before treating it as live/terminal; do not restart solely from this
ledger entry. No result was available at handoff.

## Refinement completed; output-reset release slew experiment (2026-09-06)

The previously in-flight `latch-repeated-readout/20260906T213539895693Z/`
completed normally within the 600-second allowance. Session 62211 is terminal;
do not poll/restart it as a live job. All four decision/hold/reset/receiver checks
pass under 5 ps maximum step and reltol 1e-5, with the same extracted circuit,
inputs, seed, model files and physical timing as baseline prefix
`20260906T213056297348Z`. Hold-minimum changes are approximately -45.62,
-45.91, -31.92 and -23.75 microvolts. Receiver minima change from
-2.69338/-2.63144 mV to -2.59763/-2.54044 mV, and maxima remain
1.80172263/1.80167272 V. Thus the voltage-envelope failure survives this
refinement; this is one sensitivity comparison, not a convergence proof.
Refined excursion analysis: `latch-receiver-excursions/20260906T213857406706Z/`.

Added an explicit `--reset-rise-ps` release-slew parameter (default 20 ps).
The pulse's high duration compensates for changed rise time so falling/precharge
edge start stays at 38.02 ns minus reset advance. Evaluation and equalizer
clocks are untouched. Unit tests check that 20 ps/500 ps releases preserve this
edge, and profile aggregation, mismatch replay and frozen calibration binding
reject changed release slew. The old frozen v2 retains its original 20 ps;
it is not rewritten to accept a changed clock.

Single-variable 500 ps release experiment
`latch-repeated-readout/20260906T213844028085Z/` retains the four logical
inputs, +3.125 mV correction, seed, geometry and baseline solver. All four
decision/hold/reset/receiver checks pass. Receiver minima improve to
-2.03266/-1.96012 mV, while maxima remain 1.80172224/1.80168273 V.
This supports release-slew sensitivity of undershoot and separates it from the
later precharge overshoot. It does not close the strict envelope, qualify a
physical driver, or validate the original frozen contract with modified timing.
Eighteen focused unit tests pass.

## Independent precharge slew and bounded supply-energy measurement (2026-09-06)

Added optional `--reset-fall-ps` to vary output precharge slew independently of
evaluation/equalizer clocks. Defaults retain the original common clock-fall
setting. Offset aggregation, mismatch replay and frozen calibration binding
reject changed effective precharge slew; tests verify unchanged pulse start
and duration when only fall time changes. No frozen contract is rewritten.

Run `latch-repeated-readout/20260906T214054728224Z/` changes only the output
precharge fall from 1000 to 2000 ps relative to the completed 500 ps release
experiment `20260906T213844028085Z`. Four decisions, hold, reset and receiver
checks pass, but maxima worsen from 1.80172224/1.80168273 V to
1.80182348/1.80184418 V. Undershoot remains about -2.033/-1.961 mV. This
rejects the tested slower-precharge setting as a solution to the overshoot.
It is an ideal-clock diagnostic, not a physical driver implementation.

Added `analyze_latch_supply_energy.py` to integrate saved VDD and VACTIVE
currents over exact cycle windows. Positive delivered and returned energy are
kept separately, with zero crossings inserted before piecewise-linear
integration. First-cycle operating-point initialization is excluded from the
reported nonstartup average. Tests cover signed energy, interval endpoints,
missing coverage and constant-supply validation.

Evidence `latch-supply-energy/20260906T214230227207Z/` gives mean net energy
from these two rails for cycles 1..3:

- Original four-cycle prefix: 3.232029 pJ/cycle.
- Refined solver, same physical profile: 3.232156 pJ/cycle.
- 500 ps release: 3.238419 pJ/cycle.
- 500 ps release plus 2000 ps precharge: 3.240703 pJ/cycle.

These are partial simulated supply-energy measurements including loads fed
from those rails, NOT total comparator or inference energy. Unsaved clock,
input and bias-source energy, actual driver generation, ADC/DAC/array,
memory and runtime are excluded. No efficiency benefit or hardware measurement
is claimed. All four profiles retain strict voltage-envelope failures.
Twenty focused tests pass; no converter/workload gate is promoted.

## Complete independent ideal-source port instrumentation (2026-09-06)

The repeated runner now saves input voltages and VP/VN/VRESET/VEVAL currents,
plus VEQRESET current when the equalizer exists. These are write-time observables;
no circuit elements, clock values or acceptance limits change. Instrumented
baseline prefix `latch-repeated-readout/20260906T214520181430Z/` has 10288
samples x 21 vectors. Projecting onto the original 14 vectors gives exact
bitwise equality with `20260906T213056297348Z/` over the entire 200 ns run;
both projected hashes are
`91f593572184483412f15b649f3b6eefb9f0b6246adc2a81274e133b93ec2983`.
Four decision/hold/reset/readout checks still pass; voltage failures remain.

Extended the supply-energy analyzer to enumerate independent voltage/current
sources, calculate delivered power with explicit polarity, and report missing
current observables rather than silently treating them as zero. Zero-voltage
ground-source power is identically zero. Constant IBIAS power uses its exact
deck value and saved terminal voltage. Historical reports remain two-rail-only.

Evidence `latch-supply-energy/20260906T214640758018Z/` has no missing independent
source ports. Mean net energies for nonstartup cycles 1..3 are:

- VDD: 303.43545 fJ; VACTIVE: 2928.59363 fJ.
- Output-reset clock: 1.01626 fJ; evaluation clock: 7.83832 fJ;
  equalizer clock: 0.18557 fJ.
- VP/VN input sources: approximately 0.00076/0.00270 fJ net.
- IBIAS: -35.39204 fJ, meaning absorption by the ideal current sink.
- Sum over all independent ideal sources: 3205.68065 fJ net.

The sum is lower than two-rail delivery because the ideal bias sink absorbs
energy; it is NOT evidence that a physical implementation recovers that energy.
Positive-delivered/returned components are retained per source and cycle.
Physical clock/bias/input driver generation losses, ADC/DAC/array, storage,
runtime and actual hardware measurements remain outside this boundary. This
does not establish total comparator energy or inference efficiency. Twenty-one
focused unit tests pass, including source polarity and missing-current controls.

## Installed-library decision capture cell smoke test (2026-09-06)

Inspected installed `sky130_fd_sc_hd__dfxtp_1`: SPICE port order
CLK D VGND VNB VPB VPWR Q, 24 transistor instances. The TT/25 C/1.8 V Liberty
cell specifies rising-edge capture (`clocked_on: CLK`, `next_state: D`),
data-pin capacitance 0.001678 pF and clock-pin capacitance 0.001794 pF.
These are characterized library values, not extracted analog-to-cell wiring.

Added `run_sky130_decision_capture_cell.py` to select the unchanged cell block,
check exact port order/device count, load installed model dependencies, pin
source hashes, and test capture/retention independently before analog coupling.
It retains the Apache source notice. No digital cell substitution or manual
device-dimension changes are used. The nominal test is TT/25 C, no mismatch,
50 ns period, capture beginning at 20 ns with 100 ps edges, and 2 fF Q load.
Declared hold windows span data changes occurring between clock edges.

Initial run `decision-capture-cell/20260906T215143525715Z/` failed model loading
because a standalone special-NFET file duplicated the alias already present
in the regular TT NFET model. Removing that redundant include uses the installed
alias; HVT PFET and mismatch-parameter dependencies are still explicitly loaded.
Second run `20260906T215315973406Z/` actually wrote a complete 10105-row transient
but was classified incomplete by the harness because ngspice returned 1 after
reporting no batch print/plot analysis. Contrary to the interim commentary, this
second run was not a parameter-expansion failure. Added an explicit measurement
directive; no circuit or stimulus change was needed.

Current completed evidence `decision-capture-cell/20260906T215435738569Z/`
passes all four full-window capture/retention checks for Q=[0,1,1,0], including
intervening data changes without a capture edge. It nevertheless has Q extrema
-0.0286184 V and 1.9208842 V, so strict_q_envelope_pass=false. This is evidence
that even this installed transistor-level capture-cell view requires a separate
transient-voltage assessment; it does NOT justify waiving the analog receiver's
limits or claiming foundry reliability/physical signoff. This cell's view is
not combined-layout extraction, and no setup/hold or PVT sweep was performed.
Twenty-two focused unit tests pass, including capture-interface negative controls.

## Receiver-to-capture integration diagnostic (2026-09-06)

Added `run_latch_capture_integration.py`: the actual 16-device extracted
equalizer/latch/receiver drives D of the installed 24-device transistor capture
cell through rx_n. No behavioral decision source drives D. Original receiver
2 fF loads are retained, and capture Q has a separate 2 fF load. Cell supply
and capture-clock currents are saved separately. This is a mixed-view,
40-transistor diagnostic with ideal connection wiring and clocks, NOT a
combined-layout or physical hardware result. Both blocks use TT/25 C with
mismatch disabled; the source analog run was 27 C, so this is a new operating
point, not a replay of its frozen calibration.

Completed `latch-capture-integration/20260906T215802138232Z/` captures the four
input signs [-0.5,+0.5,-0.5,+0.5] mV as Q=[0,1,0,1]. Receiver D is checked
through 19..21 ns around each 20 ns rising capture edge. Q is checked over
[22,69], [72,119], [122,169] and [172,199] ns, including comparator reset and,
for the first three windows, the following analog decision before recapture.
All four D and Q windows pass. Q nevertheless ranges from -0.0283122 to
1.9209609 V, and receiver excursions persist, so the strict saved-node envelope
fails and accepted_converter remains false. Capture internal nodes were not
all saved/audited; terminal qualification is not established.

Energy analysis `latch-supply-energy/20260906T215928972266Z/` accounts for all
independent ideal-source ports. Over nonstartup cycles 1..3, the capture-cell
supply delivers 53.33895 fJ/cycle net and capture clock 0.55907 fJ/cycle net;
the original two rails supply 3.258794 pJ/cycle. Do not compare this directly
to the earlier mismatched/27 C energy as a matched optimization. Physical
driver generation, layout interconnect and the complete ADC remain outside
this electrical-port accounting.

A clock-disabled negative-control mode holds the capture clock low while
retaining the same expected bit sequence. Its outcome is recorded separately;
do not redefine expected bits to make a disabled clock pass. Twenty-three
focused tests pass, including full-window rather than endpoint-only retention.

Completed negative control `latch-capture-integration/20260906T215926350212Z/`:
all four receiver-D windows still pass, while Q remains near zero and correctly
fails the two expected-high windows (cycles 1 and 3). The active-clock result
therefore depends on capture-clock operation in this simulated circuit, not
merely correct combinational receiver data or initial Q. Neither run qualifies
the physical voltage envelope. The negative control is retained as an expected
diagnostic failure, not relabeled as a passing converter.

## Forty-device routed capture layout and extracted transient (2026-09-06)

Added `build_combined_latch_capture.py` to merge actual analog geometry with
the installed capture-cell Magic geometry on the same 0.005 um grid. Explicit
pin-coordinate checks guard D/CLK/Q landings; original receiver rx_n is routed
on M2 to D, and separate capture clock, Q and supply ports are exposed.
The reference retains the independent analog schematic and unchanged installed
capture-cell circuit. No extracted connectivity is used to generate the reference.

First candidate `combined-latch-capture/20260906T220446020798Z/` is DRC-clean
but fails LVS: all 40 devices are present, but the capture cell's 12 PMOS bodies
are on an untapped well. The cell VPB port requires physical well connection;
its supply pin alone does not supply a body tap. Added an actual well extension,
n+ contact stack, and metal supply connection rather than relabeling the well.

Revised candidate `combined-latch-capture/20260906T220543571833Z/` has zero
reported DRC errors and unique LVS match: 40 devices, 30 nets. Exported selected
node-to-substrate capacitances agree with raw .ext. rx_n-to-vss is 8.72709 fF,
up from 0.78574 fF in the earlier analog/receiver layout. This is total exported
node-to-substrate capacitance, not the entire DFF input capacitance or a pure
single-wire capacitance measurement. Distributed interconnect resistance is
not signed off.

The integration runner now has an opt-in verified `--combined-layout` mode.
It simulates the single 40-device extraction, removes the separate capture-cell
instance/include, and checks source identities and physical artifact hashes.
Current transient `latch-capture-integration/20260906T220705990157Z/` passes all
four D-window and captured-Q retention windows at TT/25 C, no mismatch.
rx_n ranges from -0.0080310 to 1.8112182 V and Q from -0.0460215 to 1.8707854 V;
strict saved-node envelope fails. Capture internal nodes are not all saved, so
this is not complete terminal-bias coverage or converter qualification.

Same-extraction clock-disabled control
`latch-capture-integration/20260906T220902483472Z/` keeps all four D windows
correct but Q stays near 1.8 V, failing expected-low cycles 0 and 2. Unlike the
mixed-view control's initial low state, the extracted circuit finds a high
operating-point state. No power-up state is guaranteed: the active-clock test
checks only after capture. The negative-control failure confirms the tested
retention behavior depends on the capture clock, not an assumed initial bit.

Source-energy evidence `latch-supply-energy/20260906T220904336795Z/` has no
missing independent ideal-source ports and reports 3.284349 pJ/cycle from the
two original rails over nonstartup cycles 1..3. Capture supply/clock are separate
ports; these measurements still exclude actual driver generation and the full
ADC/inference path. Twenty-five focused unit tests pass, including physical
pin-movement rejection and well-tap geometry checks. No acceptance gate is promoted.

## Next actions (current)

1. Continue the new equalizer candidate `20260906T211728514831Z` at a 50 ns
   period and 2 ns equalizer release: the both-history boundary is now 3..3.25 mV
   and frozen +3.125 mV correction passes 12/12 decision-only checks. Verify
   full-sequence replay and expand numerical checks beyond the now-verified
   four-cycle prefix. Close receiver voltage excursions and terminal-model
   coverage before promotion. Release slew alone reduces but does not remove
   undershoot, while precharge overshoot is unchanged; investigate the separate
   precharge/receiver loading boundary with an explicit cost/driver contract.
   The tested 2 ns precharge slew worsens overshoot; do not adopt it. Partial
   energy accounting now covers every independent ideal-source port in the
   instrumented prefix, but physical driver costs remain missing and must not
   be inferred from those ideal-source net flows.
   Preserve the original failing 15-device
   candidate and do not infer matched mismatch samples across layouts.
   Complete tool/PDK provenance beyond the initial executable/import probes.
   The seven-profile process/temperature screen and verified mismatch replay
   now exist. Seed-102's coarse transition is bracketed at +12..14 mV, but
   midpoint correction fails a history-dependent validation case. Conditioned
   sweeps on the original layout find conflicts at both 50 and 100 ns. Numerical
   refinement reproduces the 100 ns conflict; the physically verified equalizer
   now needs finer conditional tests. Expand a preregistered sample
   set; supply/noise tests and bias-model coverage are still outstanding.
2. Continue from stronger-PMOS LVS snapshot `20260906T202553317062Z`, using
   350 kohm/evaluation 7.8 ns and the explicitly separate 1.75 V precharge rail
   as the nominal diagnostic profile. The unloaded four-cycle profile now uses
   0.5 ns early precharge and 1 ns falling clock edges. Establish a working
   reverse-gate-bias qualification or circuit revision for the four flagged
   NFETs, plus a justified physical voltage acceptance contract. Use 1.75 V
   reset-high for the current ideal-driver profile. Combined routed readout
   works, but model-range coverage and strict node-envelope diagnostics are
   not closed. Implement
   physical clock/rail generation before promoting beyond ideal-source evidence.
   Keep the failed +0.25 mV case visible; the 0.5 V differential diagnostic
   threshold is not a substitute for a real digital receiver contract.
3. Establish repeatable signed decisions and full waveform legality before
   connecting the actual sampled frontend. Do not promote a one-sided latch.
   The separate capture connection now demonstrates nominal decision retention
   through reset and its clock-disabled negative control fails as intended.
   A combined 40-device DRC/LVS-passing extraction now also passes nominal
   capture and its negative control. Expand declared timing/load and internal
   terminal coverage; compare capture-clock slew against the measured D/Q
   excursions without changing acceptance limits. Keep nominal extracted logic
   evidence explicitly separate from qualified integration.
4. Bind the preregistered real workload to a circuit-derived error profile and
   analog lowering beyond the now-executable digital fallback. Keep test data unscored until model/profile
   freeze; complete unresolved array and hardware requirements in M1.
