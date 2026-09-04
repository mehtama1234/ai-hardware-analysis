# Toolchain Map

The toolchain is organized by the kind of evidence each tool can produce.

## Workflow Contract

Consumes: model graphs, analog measurements, RTL, synthesis scripts, OpenLane packages, and backend evidence requirements.

Produces: a claim boundary for each tool: what it can prove, what it cannot prove, and which artifact should be exported into the workbench.

Supports: the combined system can separate simulation evidence, RTL evidence, synthesis evidence, physical-flow evidence, and backend claim evidence.

Refuses: treating any one tool result as proof of a production analog foundation-model chip.

The AIHWKIT and CrossSim-style adapter boundary is detailed in `aihwkit-crosssim-adapter-boundary.md`. The current local status is recorded in `current-simulator-adapter-status.md`, and the required JSON output for a real run is defined in `analog-simulator-adapter-output-contract.md`.

The command `./scripts/check_tools.sh` now separates required chip/EDA tools from optional simulator adapters. It can say `OPTIONAL-MISSING aihwkit python module` or `OPTIONAL-MISSING crosssim python module` without making the current ngspice, RTL, synthesis, OpenLane-readiness, backend, and site bridge fail.

The install path for those optional adapters is described in `optional-aimc-simulator-install-path.md`.

## SPICE Evidence

Tools: `ngspice`, later `xschem`.

SPICE answers circuit-equation questions. It can show transient response, DC operating point, AC gain, noise, and sensitivity to simple parameter changes.

What it proves: the circuit equations behave as simulated under the selected models and conditions.

What it does not prove: layout parasitics, manufacturing legality, full process variation, or system-level correctness unless those are explicitly modeled.

Handoff: SPICE-style outputs should become analog-error evidence, not model-accuracy evidence. They feed the analog measurement chain and converter-boundary pages.

## RTL Simulation Evidence

Tools: `iverilog`, `verilator`, `gtkwave`.

RTL simulation answers sequence questions. It checks whether a design produces expected values for selected input histories.

What it proves: the sampled scenarios behave as expected.

What it does not prove: all states, physical timing, power, placement, routing, or manufacturability.

Handoff: RTL simulation outputs should become control-rule evidence. They feed the backend as proof that the governor rule was represented and checked as hardware logic.

## Synthesis Evidence

Tools: `yosys`, later standard-cell libraries.

Synthesis answers translation questions. It turns RTL into a lower-level logic network and exposes what implementation structure the tool chose.

What it proves: the RTL can be elaborated and transformed into logic under the tool's rules.

What it does not prove: timing closure, physical routing, final power, or silicon yield.

Handoff: synthesis outputs should become implementation-translation evidence. They say the controller can lower into gates, but the claim still stops before layout and signoff.

## Layout Evidence

Tools: `magic`, `klayout`.

Layout tools answer geometry questions. They expose whether drawn shapes satisfy design rules and whether the physical structure matches the intended circuit.

What they prove: geometry and connectivity claims, depending on rule decks and setup.

What they do not prove: every analog performance or timing property unless extraction and simulation are included.

Handoff: layout outputs should become geometry-preservation evidence. They are useful only when the design rule deck, extracted netlist, and checked circuit are named.

## Place-And-Route Evidence

Tools: `openroad`, `openlane`.

Place-and-route tools answer physical implementation questions. They test whether a gate-level design can become placed, routed, timed, powered geometry.

What they prove: a particular flow can produce a checked physical implementation under the selected process, constraints, and tool settings.

What they do not prove: production readiness without signoff-quality checks, packaging, test, reliability, and silicon data.

Handoff: OpenLane/OpenROAD outputs should become educational physical-flow evidence. The backend should treat them as stronger than RTL and weaker than signoff or silicon.

## Backend Evidence Evidence

Tools: restored FastAPI backend, evidence exporter, package archive, claim-readiness endpoint.

The backend does not prove physics. It proves bookkeeping discipline. It attaches artifacts to a package, checks provenance, and refuses claims that outrun the evidence.

What it proves: the workbench can turn lab outputs into supported, needs-review, or blocked claims.

What it does not prove: that the underlying local simulation, RTL, or physical-flow evidence is stronger than it really is.

Handoff: this is where the user-facing answer lands. The frontend should show the backend's supported and blocked claims, not rewrite them into broader language.
