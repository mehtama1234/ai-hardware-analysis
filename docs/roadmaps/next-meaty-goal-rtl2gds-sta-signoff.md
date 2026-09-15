# Next meaty goal: reproducible RTL-to-GDS and STA signoff

## Goal

Take one real digital block from a written hardware description (RTL) all the
way to a routed, manufacturable layout, and produce timing and physical
evidence that explains whether it is ready for human review.

In simple terms:

```text
digital behavior → logic gates → chip placement → chip wiring
                 → timing checks → fixes → final layout evidence
```

This is a digital implementation workstream that complements the existing
AI/analog model-to-chip qualification work. It is intended to build a concrete
RTL2GDS/STA portfolio artifact, not to claim commercial-tool tapeout experience
that has not been performed.

## Scope

Use an existing AIMC control-plane or scheduler RTL block and an open,
reproducible flow such as Yosys, OpenROAD/OpenLane, and OpenSTA. Keep the
interfaces and workload contract tied to the existing project so the result is
connected to the AI-hardware system rather than being an unrelated toy block.

## Six end-to-end gates

1. **RTL and checks** — freeze the block interface, clocks, resets, operating
   modes, and a small functional/regression test.
2. **Synthesis** — map the RTL to a named standard-cell library and retain the
   netlist, constraints, area, cell-count, and synthesis logs.
3. **Physical implementation** — run floorplanning, power planning, placement,
   clock-tree construction, routing, and layout export; retain DEF/GDS,
   congestion, utilization, and routing reports.
4. **MCMM timing** — analyze all declared clocks and modes across at least
   representative slow, typical, and fast conditions; report WNS, TNS, critical
   paths, setup, and hold results.
5. **Repair and physical checks** — introduce or identify a timing failure,
   apply one bounded RTL/constraint/layout ECO, rerun timing, and run available
   DRC, LVS/connectivity, antenna, and power/IR checks or clearly label any
   unavailable check.
6. **Release bundle** — create a hash-bound manifest joining RTL, constraints,
   scripts, tool versions, logs, netlist, DEF/GDS, timing reports, ECO diff,
   physical checks, and a plain-language pass/fail decision.

## Definition of done

The project is complete when a clean checkout can reproduce the flow and a
reviewer can answer, from retained evidence:

- what the block does;
- what gates and cells implement it;
- where those cells and wires are placed;
- whether every declared mode/corner meets timing;
- what was changed when timing failed;
- whether the final layout passes the available physical checks; and
- which conclusions remain unproven without commercial tools, foundry data, or
  silicon.

## Claim boundary

Passing this goal demonstrates practical RTL synthesis, open-source physical
implementation, timing analysis, automation, and signoff reasoning. It does
not by itself demonstrate production experience with Innovus, ICC2, PrimeTime,
Tempus, Voltus, foundry signoff decks, or tapeout execution. Those distinctions
must remain explicit in the project and in any job application.

## First execution checkpoint

The selected block is the existing `aimc_control_plane` RTL. Its functional
regression passes, and Yosys synthesis completes with zero inferred memories,
zero remaining processes, 277 generic cells, and five resettable flip-flop
bits. The packaged OpenLane readiness check also passes the design-file, JSON,
Yosys, Docker, OpenLane-source, and Docker-image checks.

The first OpenLane attempt stopped because the default Sky130 PDK directory was
absent. The pinned PDK revision tested by this OpenLane image was then fetched
and enabled at `/home/mehtama1/eda-tools/pdks`, and the flow was rerun through
`analog-digital-chip-design-eda/scripts/run_aimc_openlane_flow.sh`.

That CTS-enabled run completed synthesis, floorplanning, placement, clock-tree
construction, global and detailed routing, parasitic extraction, min/max/nom
multi-corner STA, GDS streaming, XOR comparison, LVS, DRC, and antenna checks.
The retained summary is
`analog-digital-chip-design-eda/labs/eda/aimc-control-plane-openlane-prep/openlane-cts-metrics-summary.md`,
with the hash-bound artifact manifest at
`analog-digital-chip-design-eda/labs/eda/aimc-control-plane-openlane-prep/openlane-cts-manifest.json`.
It reports zero setup violations, zero hold violations, zero Magic DRC
violations, a clean LVS, zero antenna violations, `1.76 ns` critical path,
`10 ns` clock period, `1,141.09 um^2` core area, and all final DEF/GDS/LEF/LIB/
SDC/SDF/SPEF views present. IR-drop analysis ran without configured
`VSRC_LOC_FILES`, so those IR values are not treated as signoff evidence.

## Timing failure and ECO retest

The required repair loop has now been exercised. A deliberately over-tightened
`1 ns` clock screen reached synthesis STA and failed with setup WNS `-1.09 ns`,
TNS `-5.03 ns`, and worst hold slack `-0.35 ns`. OpenLane stopped during
detailed placement because the constraint was infeasible; this is retained as
a timing-failure screen, not a physical signoff run.

The bounded constraint ECO restored the declared `10 ns` clock contract and
reran the complete flow under the tag
`aimc_control_plane_timing_eco_retest`. The retest completed CTS, routing,
multi-corner STA, parasitic extraction, GDS generation, XOR comparison, LVS,
DRC, antenna, and ERC steps. It reports WNS/TNS `0.0`, a `1.76 ns` critical
path, zero setup and hold violations, zero Magic DRC violations, clean LVS, and
zero antenna violations. Its repository summaries are
`openlane-eco-retest-metrics-summary.md` and
`openlane-eco-retest-manifest.json` in the OpenLane prep directory.
