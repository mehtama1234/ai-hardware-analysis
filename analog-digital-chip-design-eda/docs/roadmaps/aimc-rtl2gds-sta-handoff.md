# AIMC RTL2GDS / STA handoff

## What this project demonstrates

In simple terms, the project starts with RTL—the text description of a small
multi-clock AIMC controller—and turns it into a placed and wired chip block.
The flow then checks whether signals arrive on time and whether the layout is
structurally clean.

| ASIC responsibility | Evidence in this project |
| --- | --- |
| Synthesis | Yosys/OpenLane synthesis of the integrated controller |
| Block implementation | Multi-clock controller, scheduler, readout, and error-budget logic integrated as one top |
| Placement and routing | OpenLane floorplan, CTS, global and detailed routing |
| MCMM STA | Extracted min/max/nominal SPEF timing and explicit core/maintenance clock constraints |
| Timing ECOs | Deliberate 10 ns failure, 20 ns recovery, then input-register pipeline closure at 10 ns |
| Physical checks | DRC 0, LVS clean, XOR clean, antenna clean, ERC completed |
| Power integrity | Local modeled VPWR/VGND source analysis; worst modeled drop 3.87 mV |
| Release discipline | Hash-bound DEF/GDS/LEF/LIB/SDC/SDF/SPEF manifest and independent checker |

## What it does not demonstrate

It does not prove experience with Innovus, ICC2, PrimeTime, a foundry PDK,
signoff corners supplied by a real project, package/board power delivery, or
production tapeout execution. The modeled source locations are useful for
learning and comparison, but are not measured package data.

The canonical run still reports 38 max-fanout violations. Several targeted
ECOs were measured and rejected because they either failed timing, increased
fanout, increased area, or worsened IR. This is preserved as an honest open
engineering item in `fanout-eco-comparison.md`.

## Appropriate resume/interview wording

“I implemented and locally signoff-checked a multi-clock RTL subsystem through
an open-source RTL-to-GDS flow. I wrote clock/CDC constraints, used extracted
multi-corner timing, diagnosed a failing 10 ns baseline, applied timing ECOs,
and produced DRC/LVS/XOR/antenna-clean layout artifacts with a hash-bound
release package. I have not yet run the equivalent flow in Innovus, ICC2, or
PrimeTime, nor executed a foundry tapeout.”

## Next commercial bridge

The next project-specific step is to reproduce this same block under an
authorized commercial flow and project PDK, then close max fanout, MCMM setup
and hold, EM/IR, and final tapeout checks under that tool's reports.
