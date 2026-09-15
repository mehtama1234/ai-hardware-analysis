# Analog, Digital Chip Design, and EDA

This folder is a first-principles working lab for analog design, digital design, and electronic design automation.

The active cross-project implementation goal is the
[rigorous hybrid inference execution plan](docs/roadmaps/rigorous-hybrid-inference-execution-plan.md),
with current progress in the [restart ledger](docs/roadmaps/rigorous-hybrid-inference-restart-ledger.md).

The authoritative model-to-chip goal and cross-repository handoff is
[../END_TO_END_QUALIFICATION_HANDOFF.md](../END_TO_END_QUALIFICATION_HANDOFF.md).

The broader autonomous design and verification North Star, including the
canonical end-to-end implementation goal and staged research plan, is in
[the North Star roadmap](../docs/roadmaps/autonomous-silicon-design-verification-north-star.md).

The goal is not to collect loose notes. The goal is to explain chip design from the physical and mathematical objects that must be controlled:

- voltage, current, charge, noise, gain, bandwidth, and stability in analog circuits
- Boolean function, state, delay, power, area, and clock timing in digital circuits
- design rules, parasitics, placement, routing, extraction, yield, and verification evidence in EDA

The writing standard is simple: every article should name the object, the constraint, the mathematical shape, the concrete design move, and the failure mode.

## Current Local Status

The old `ai-hardware-analysis` folder is present again at `/home/mehtama1/git-repo/ai-hardware-analysis`.

The two repos now have a clear split:

- `ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/` is the architecture and product-spec source for analog in-memory AI inference, including AIHWKIT, CrossSim-style layout checks, analog-MLIR/compiler paths, validation, evidence packages, and tapeout-risk pages.
- `analog-digital-chip-design-eda/` is the working chip-design lab that turns that architecture into executable analog measurements, model-impact checks, RTL control logic, synthesis, OpenLane results, and first-principles concept pages.

The bridge page is:

```text
docs/research/ai-hardware-architecture-to-working-lab-bridge.md
```

## Working Areas

- `docs/concepts/`: first-principles concept articles
- `docs/roadmaps/`: writing plans and reading paths
- `labs/analog/`: SPICE circuits and measurements
- `labs/digital/`: Verilog/SystemVerilog examples and simulation notes
- `labs/eda/`: synthesis, layout, timing, and verification flows
- `scripts/`: environment checks and install helpers
- `sources/`: local seed material and future paper/source indexes

## Tool Stack

Start with the smallest useful open-source stack:

- `ngspice` for analog simulation
- `xschem` for schematic capture
- `magic` for layout
- `klayout` for layout viewing and DRC scripting
- `yosys` for digital synthesis
- `iverilog` or `verilator` for RTL simulation
- `gtkwave` for waveform inspection
- `openroad` and `openlane` when the flow needs full RTL-to-GDS examples

Run:

```bash
./scripts/check_tools.sh
```

Run the current AIMC analog-to-RTL bridge checks:

```bash
./scripts/check_aimc_bridge.sh
```

To install common Ubuntu packages:

```bash
sudo ./scripts/install_ubuntu_eda_tools.sh
```

To install optional analog in-memory simulator adapters:

```bash
./scripts/install_optional_aimc_simulators.sh --all
```

Those optional adapters are AIHWKIT and CrossSim. They do not strengthen any claim just by being installed. They become useful only after a real run writes a strict simulator payload that passes the guarded importer.

## Digital Verification Pilot Service

For a compact four-workstream software demonstration in Google Colab, see
[`colab/README.md`](colab/README.md). It runs the seeded example through
planning, tool gates, structural analysis, agent diagnosis/assertion checks,
debugging, and optimization proposal selection.

The plain-language implementation status, current evidence, and remaining
claim boundaries are documented in
[`../docs/roadmaps/four-workstream-implementation-status-2026-09-13.md`](../docs/roadmaps/four-workstream-implementation-status-2026-09-13.md).
The detailed auto-formalization plan is in
[`../docs/roadmaps/llm-autoformalization-extension-plan.md`](../docs/roadmaps/llm-autoformalization-extension-plan.md).

The open-source digital verification vertical slice runs as a containerized
API plus durable worker. It accepts authenticated jobs, executes the
multi-design pilot with Icarus/Verilator/Yosys, and produces downloadable
evidence bundles. See the [deployment instructions](deployment/README.md):

```bash
cp deployment/.env.example deployment/.env
docker compose --env-file deployment/.env -f deployment/docker-compose.yml up --build
```

This is a production-shaped pilot foundation. Customer deployment still needs
managed queue/database storage, external identity and RBAC, object storage,
isolated workspaces, and customer EDA adapters.

For the provider-free public reference acceptance boundary, run
`python3 scripts/run_public_reference_acceptance.py`. It produces one
hash-bound decision package covering the pilot, scorecard, source archive
replay, and local browser/API adversarial checks.
For the verified scope and explicit production gates, see the [commercial beta
handoff](deployment/COMMERCIAL_BETA_HANDOFF.md), [recovery runbook](deployment/RECOVERY_RUNBOOK.md),
[customer adapter guide](deployment/CUSTOM_ADAPTER_GUIDE.md), and [pilot
measurement plan](deployment/PILOT_MEASUREMENT_PLAN.md).

## Current Physical Handoff

### Multi-clock RTL-to-GDS evidence

The AIMC control subsystem has a completed local OpenLane implementation and
signoff package: RTL simulation, synthesis, placement, CTS, routing, extracted
MCSTA, and DEF/GDS/LEF/LIB/SDC/SDF/SPEF views. Recheck the hash-bound package
with:

```bash
python3 scripts/check_aimc_multiclock_signoff.py
# Stronger variant with explicit modeled VPWR/VGND source locations:
python3 scripts/check_aimc_multiclock_signoff.py \
  labs/eda/aimc-multi-clock-control-subsystem-openlane-prep \
  openlane-vsrc-aligned-manifest.json
```

The checker intentionally preserves the claim boundary: this is open-source
local implementation evidence, not Innovus/ICC2/PrimeTime or foundry tapeout
signoff. The aligned variant uses modeled package sources, not a real package;
the remaining engineering warning is max fanout.
See the [RTL2GDS/STA handoff](docs/roadmaps/aimc-rtl2gds-sta-handoff.md) for
the plain-language mapping to ASIC physical-design responsibilities.

The first joined verification-to-physical handoff gate is:

```bash
python3 scripts/run_verified_rtl2gds_bridge.py
# Independently recheck its joined report:
python3 scripts/check_verified_rtl2gds_bridge.py
```

It proves that the canonical RTL simulation and the existing aligned OpenLane
package refer to byte-identical RTL sources. It does not rerun OpenLane or
claim commercial-tool or silicon signoff.

### Real-model LLM benchmark on Colab

The local Colab OAuth cache can be used for an opt-in real-model benchmark.
The runner packages source only, downloads model weights inside the temporary
Colab runtime, validates all proposal and adversarial-review gates, and
downloads only the resulting evidence. It never uploads credentials or
modifies canonical RTL:

```bash
COLAB_SESSION_NAME=aimc-llm-agent \
COLAB_GPU_TYPE=T4 \
COLAB_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct \
COLAB_ASSIGN_RETRIES=3 \
COLAB_ASSIGN_BACKOFF_SECONDS=20 \
bash colab/run_llm_agent_benchmark_local.sh
```

This run consumes Colab compute and should be started deliberately. A passing
result measures the selected model on the benchmark; it does not authorize
autonomous repair, physical signoff, or silicon claims.
Assignment failures are retried a bounded number of times and recorded with
every attempt; set `COLAB_ASSIGN_RETRIES=1` and
`COLAB_ASSIGN_BACKOFF_SECONDS=0` for a single immediate attempt.

The complete failure-to-closure state machine is
`scripts/run_agentic_hardware_closure.py`. It consumes the verified Colab
model report, runs a bounded primary repair and held-out temporal repair,
requires an explicit review decision, retests only disposable copies at the
same simulation/formal scope, and can continue through same-run OpenLane.
`scripts/check_agentic_hardware_closure.py` and
`scripts/check_agentic_hardware_release_manifest.py` independently verify the
trajectory, hashes, physical handoff, claim classes, and release boundary.

The browser/API surface exposes the same review boundary through
`/v1/agentic-closure` and `/v1/agentic-closure/signoff`. A signoff receipt is
digest-bound to the closure summary and manifest; stale manifests are rejected.
Fixture approvals remain blocked from release, and `analog_authorized=false`
is preserved in every manifest.

The verified real-model/OpenLane replay is retained under
`.artifacts/llm-agent-colab/agentic-hardware-closure-realcolab-v4-20260913/`.
It is evidence of the LLM-assisted digital/physical workflow, not autonomous
tapeout, analog qualification, measured hardware, or silicon signoff.

Rebuild the portable handoff archive with:

```bash
python3 scripts/archive_aimc_multiclock_signoff.py \
  --output /tmp/aimc-multiclock-signoff-v0.1.tar.gz
```

The software side imports a measured Tesla T4 GPT-2 baseline and evaluates a real projection through a provisional array model and shared compiler/SRAM fallback. The [contact/routing rebuild](docs/roadmaps/converter-drc-closure-2026-09-09.md) now passes completed full-cell Magic DRC with zero reports and preserves the repaired preamp connections and 13 transistors. Both tested input signs resolve correctly, but electrical output margin fails. The original macro's historical zero summary count was not full-cell clearance; the new candidate has a separate verified audit.

The [active-transistor schematic LVS now passes](docs/roadmaps/converter-regeneration-diagnosis-2026-09-09.md). Bounded diagnostics show that longer settling/precharge does not fix the tested electrical failures: the default load stays weak, while an alternate load regenerates to the wrong side for negative inputs. The next physical target is the sampling/regeneration interface followed by complete SAR/sample/mux and robustness qualification. See the [connected GPT-2 evaluation](../analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/README.md) for the remaining program gates.

The [phase-separated schematic exploration](docs/roadmaps/sample-regeneration-exploration-2026-09-09.md) now resolves ±100 mV with sufficient margin, but no tested setting qualifies ±0.153 mV. These new topologies have provisional parasitics and do not inherit the physical candidate's DRC/LVS evidence or authorize analog placement.

The non-hardware path is now closed in the [software closeout](../analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/NON-HARDWARE-CLOSEOUT-2026-09-09.md). The [hardware handoff](docs/roadmaps/hardware-handoff-after-software-closeout-2026-09-09.md) and [target options](docs/roadmaps/hardware-target-options-2026-09-09.md) define the remaining physical gates and the information required to resume them.

## First Writing Goal

Write the first 20 concept articles as a connected atlas:

1. Voltage is a state variable
2. Current is movement of charge
3. Transconductance is control gain
4. Noise is unwanted uncertainty at the signal boundary
5. Mismatch is local manufacturing error becoming circuit behavior
6. Feedback trades gain for control
7. Stability means disturbances shrink over time
8. Bandwidth is the price of storing charge
9. ADCs turn continuous voltage into bounded decisions
10. Digital logic turns voltage ranges into symbols
11. A flip-flop is a timed memory decision
12. Timing closure is proof that data arrives before the decision
13. Power is switching plus leakage plus delivery loss
14. Area is a physical budget, not just a cost
15. Placement turns graph structure into distance
16. Routing turns connection demand into geometry
17. Extraction turns drawn shapes back into circuit equations
18. Verification is evidence that the implemented function matches the intended function
19. Yield is probability over manufacturing variation
20. EDA is constraint solving over physics, logic, and geometry
