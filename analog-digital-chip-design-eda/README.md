# Analog, Digital Chip Design, and EDA

This folder is a first-principles working lab for analog design, digital design, and electronic design automation.

The active cross-project implementation goal is the
[rigorous hybrid inference execution plan](docs/roadmaps/rigorous-hybrid-inference-execution-plan.md),
with current progress in the [restart ledger](docs/roadmaps/rigorous-hybrid-inference-restart-ledger.md).

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
