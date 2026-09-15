# Next meaty goal: multi-clock AIMC control subsystem

## Goal

Build and sign off a small, auditable AIMC control subsystem that crosses a maintenance clock into a core execution clock, combines the existing tile controller with the scheduler/error-budget governor, and produces RTL, routed layout, extracted timing, and manufacturability evidence.

This is the next meaningful bridge toward ASIC physical-design work: it exercises clock constraints, CDC structure, synthesis, placement, routing, MCSTA, timing closure, and release artifacts in one block. It is not a claim of Innovus, ICC2, PrimeTime, foundry, or tapeout experience.

## Completed evidence

- RTL integration: `analog-digital-chip-design-eda/labs/digital/aimc-control-plane-rtl/aimc_multi_clock_control_subsystem.v`
- Two-clock behavioral test: `aimc_multi_clock_control_subsystem_tb.v` passes. The test observes a maintenance-domain budget being synchronized into the core domain and an analog request being accepted by the integrated governor.
- Packaged hierarchy passes Verilator lint and Yosys hierarchy lowering.
- OpenLane configuration and explicit constraints: `analog-digital-chip-design-eda/labs/eda/aimc-multi-clock-control-subsystem-openlane-prep/`
- Baseline 10 ns core-clock run completed physical implementation but failed final setup timing: post-route SPEF WNS −0.86 ns, TNS −8.55 ns. This is the deliberate failure screen.
- Timing ECO retest at a 20 ns core period completed the full flow: min/max/nominal extracted MCSTA, final setup and hold clean, route DRC 0, LVS clean, XOR clean, and antenna violations 0.
- ECO metrics and hash-bound manifest:
  `openlane-eco-20ns-metrics-summary.md` and `openlane-eco-20ns-manifest.json`
- ECO final evidence: 5.56 ns critical path, 20 ns clock period, 50 MHz suggested frequency, 1,477 synthesized cells, 7,015 total cells, and all DEF/GDS/LEF/LIB/SDC/SDF/SPEF views present.
- 10 ns timing-closure ECO: the integrated wrapper now registers the controller/readout inputs before the ADC correction arithmetic, preserving functional behavior with one additional cycle of latency. The retest completed full OpenLane flow with extracted SPEF WNS/TNS 0.0 and no setup or hold violations at nominal timing.
- 10 ns closure metrics and manifest: `openlane-pipeline-10ns-metrics-summary.md` and `openlane-pipeline-10ns-manifest.json`.
- 10 ns input-diode cleanup retest: antenna protection on input ports produced zero pin and net antenna violations while retaining zero setup/hold violations and complete final views. Canonical metrics and manifest: `openlane-10ns-diode-metrics-summary.md` and `openlane-10ns-diode-manifest.json`.
- Multi-clock SDC correction retest: moving the custom constraints to `BASE_SDC_FILE` made both clocks visible in the generated signoff SDC and removed the prior unclocked-register/unconstrained-endpoint warnings. The run retained zero setup/hold, DRC, LVS, XOR, and antenna violations. Evidence: `openlane-multiclock-sdc-metrics-summary.md` and `openlane-multiclock-sdc-manifest.json`.
- Release-package verification: `analog-digital-chip-design-eda/scripts/check_aimc_multiclock_signoff.py` independently verifies the canonical manifest hashes, all seven final views, clean timing/manufacturability extracts, and the two-clock SDC relationship. The integrated RTL regression and packaged Yosys lowering check also pass.
- Explicit-source IR retest: a complete rerun with four modeled VPWR and four modeled VGND sources, aligned to legal PDN nodes, completed with no IR-drop source warnings. The resulting package is `openlane-vsrc-aligned-metrics-summary.md` and `openlane-vsrc-aligned-manifest.json`; its voltage map is still a modeled package assumption, not measured package or board evidence.
- Portable handoff archive: `analog-digital-chip-design-eda/scripts/archive_aimc_multiclock_signoff.py` packages the source, constraints, selected manifest/summary, seven final views, and signoff reports. A build followed by clean extraction and per-file SHA-256 verification passed for 32 files.

## Remaining boundary work

- Resolve the remaining max-fanout warning with an RTL or buffering ECO and rerun signoff. The current 10 ns run still reports a max-fanout warning even though setup/hold are clean.
- Reconcile the remaining max-fanout count (38) with the intended implementation limits; the clock-model warnings are now resolved.
- A stricter max-fanout/CTS-clustering experiment was rejected because it caused global-routing congestion overflow; the package is restored to the last passing implementation settings. Selective buffering or hierarchy restructuring is still required for a clean fanout report.
- A selective RTL experiment that decomposed the signed `gain_q6` multiply into partial products was also rejected: its full routed retest reintroduced a typical-corner setup failure. The original multiplier implementation is restored and its unit test passes.
- A moderate physical experiment using max-fanout 8, tighter CTS clustering, and a larger die also failed the 10 ns setup check after wire delay increased. Those settings are rejected; the last passing geometry and CTS configuration are restored.
- A delay-oriented synthesis experiment (`DELAY 4`) preserved 10 ns timing but worsened the signoff tradeoff: max-fanout rose to 56, total cells to 11,551, and antenna violations returned. It is rejected and the area-oriented synthesis strategy is restored.
- A CTS-only experiment with smaller sink clusters completed timing and manufacturability checks but increased max-fanout from 38 to 40. It is rejected; the prior CTS settings are restored.
- A two-stage registered readout experiment preserved functional behavior and full physical timing/manufacturability checks, but increased max-fanout to 52 and expanded the block to 11,041 cells. It is rejected; the original one-cycle readout and controller latency are restored, and both direct regressions pass.
- A fanout-limit experiment allowing 20 loads reduced the reported fanout count from 38 to 30, but failed final setup timing by 0.05 ns. It is rejected; the default 10-load target and timing-clean canonical implementation are retained.
- A larger CTS cluster (10 sinks / 16 µm) reduced fanout from 38 to 32 and improved modeled IR, but reintroduced one pin and one net antenna violation. It is rejected; CTS 8 / 12 is retained because it keeps antenna clean.
- A narrower signed ADC operand experiment preserved RTL regressions and timing, but increased fanout from 38 to 40, increased area from 64,348 to 65,746 µm², worsened modeled IR drop, and introduced four width-expansion lint warnings. It is rejected and the original arithmetic is restored.
- A combinational radix-16 decomposition of the signed gain reduced fanout from 38 to 27 and reduced area to 62,735 µm², but failed extracted setup timing (SPEF WNS −0.19 ns, TNS −1.11 ns) and introduced one width-expansion lint warning. It is rejected and the original multiplier is restored.
- A narrower 20-bit version of the radix decomposition reduced fanout to 34 and area to 63,080 µm², but still produced a final setup violation (reported WNS −0.0 ns) and three lint warnings. It is rejected and the original multiplier is restored.
- Replace the modeled source locations with package/board-derived locations before treating IR-drop numbers as product signoff evidence.
- For a commercial claim, repeat the flow with authorized Innovus/ICC2/PrimeTime licenses, a target foundry PDK, project constraints, and a real tapeout checklist.

## Claim boundary

The current result supports: “implemented and locally signoff-checked a multi-clock RTL subsystem using an open-source RTL-to-GDS flow.” It does not support claiming commercial-tool proficiency or tapeout execution.
