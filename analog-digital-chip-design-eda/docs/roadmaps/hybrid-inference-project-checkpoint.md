# Hybrid inference project checkpoint — 2026-09-06

## Bottom line

We have a real-workload digital execution baseline and increasingly detailed
analog circuit simulation/layout evidence. We do not have an end-to-end analog
inference prototype or a hardware-backed comparison. Installing EDA, CrossSim
and AIHWKIT made experiments possible; it did not supply an analog array,
fabricated converter, board, instruments or execution target.

The project spent too many iterations optimizing a capture sub-block while
the system architecture and hardware-access requirements remained unresolved.
That work is reusable, but it is not the full project's critical path by itself.

## Evidence-backed position

| Requirement | Verified evidence | What remains |
| --- | --- | --- |
| Reproducible baseline | Named runs, source hashes, environment probes, extensive circuit snapshots | Complete tool/dependency lock and final clean rerun package |
| Real workload and acceptance | Optdigits 64–32–10 contract; train/calibration/test separation; numeric accuracy and benefit targets | Array, converter, hardware and absolute operating requirements unresolved |
| Digital reference execution | 761 calibration examples; five commands/sample; 1,408-byte SRAM arena; reference logit difference ≤5.73e-6; 100% digital fallback | Held-out evaluation deferred; not firmware or board execution |
| Decision/capture circuit | Nominal small-signal decisions and retention in transistor simulation; extracted source with DRC/LVS | Input/frontend integration, voltage/model validity, broader robustness and real drivers |
| Capacitor layout revision | Interrupted run actually completed: DRC 0, no layout-read errors, unique LVS; saved hashes verified at checkpoint | Capacitance/substrate export audit and transient on this exact revision |
| Complete converter | Historical representative schematic SAR results | Full supported transfer curve, all-code/history coverage, extracted integrated converter, calibration and PVT/noise qualification |
| Analog matrix computation | First 64×32 layer selected as candidate; simulator tools installed | Physical memory/array selected and accessible; signed representation, conductance, tiling, interfaces and programming defined |
| Circuit-to-task simulation | Adapter infrastructure and fixture experiments exist | Same-candidate converter/array profile bound to real workload, independent cross-checks, frozen held-out evaluation |
| Target execution boundary | Review compiler/interpreter and software fallback trace | Chosen hardware interface, controller/firmware, real transfers/handshakes, fault recovery and measured execution |
| Hardware comparison | No supported hardware-backed task result found in this checkpoint | Same-task analog computation, instrumentation, accuracy/latency/energy/fallback accounting |

No completion percentage is defensible: these are dependent gates, not equally
weighted checkboxes. DRC/LVS are layout checks, not fabricated hardware evidence.

## Authoritative anchors inspected

- Workload contract: sibling software-architecture project,
  `experiments/optdigits-v1/contract.json`. Its open requirements explicitly
  include memory/array technology, converter envelope, target binding and
  hardware access. Its `analog_authorized_now` flag is false.
- Digital execution:
  `evidence/aimc-hardware-lab/optdigits-compiled-fallback/20260906T200500785965Z/execution_result.json`.
  Calibration accuracy 0.9697766 is not held-out accuracy; `test_evaluated=false`.
- Modeled-capacitor coupled experiment:
  `evidence/aimc-simulator-adapters/latch-capture-integration/20260906T224013473263Z`.
  Four decisions pass, strict node envelope fails, no matching combined layout
  was used in that transient. Its improved peaks cannot transfer automatically
  to the subsequent physical revision.
- Latest physical revision:
  `evidence/aimc-simulator-adapters/capture-with-mim-layout/20260906T225029565233Z`.
  Raw LVS log ends in unique match. All saved artifact hashes verified.
  This corrects the earlier status statement that the latest layout still fails.
- Saved simulator environment probe:
  `evidence/aimc-hardware-lab/recovery-baselines/20260906T192609283268Z/simulator_imports.json`.
  Import success is tool availability, not analog hardware access.

No simulator/layout process was found running at this checkpoint. The interrupted
diffusion-extension edit and its completed result survived. Common local serial
and USB measurement device paths were absent; this does not establish that the
user lacks remote, disconnected, networked or laboratory equipment.

Historical status pages mix different circuit candidates and should not be used
as a current system acceptance report. This checkpoint and exact source runs
take precedence over those broad status paragraphs.

## Critical-path reset

1. **Resolve hardware feasibility now, not after converter optimization.**
   Inventory actual available analog compute hardware, controller/host,
   instruments, access rights and constraints. Identify a path that physically
   computes the first layer; a digital FPGA calculation behind an ADC is not
   analog inference. No purchases, fabrication or external deployment authorized.
2. **Close the system contract.** Specify array technology, tile dimensions,
   signed weights, conductance/voltage ranges, conversion resolution and error
   budget, sample throughput, data movement and power measurement boundaries.
   Check that the custom SKY130 path could serve this system before investing
   further in it. Keep original task thresholds and untouched test split.
3. **Connect one complete simulation path.** Compile the frozen workload,
   execute its analog-candidate first layer with an explicit array model and
   circuit-derived converter behavior, retain digital support and fault fallback,
   and produce a trace through the full workload. Any provisional profile is
   labeled provisional and cannot authorize held-out acceptance or hardware claims.
4. **One bounded custom-converter closure package.** Audit substrate/capacitance
   export and run the latest DRC/LVS-passing layout once with the existing matched
   timing/energy/voltage checks. Decide whether the result supports integration
   with sample/hold, DAC and SAR—not another open-ended sequence of latch tweaks.
   If it fails, document the mechanism and reassess topology/system suitability.
5. **Implement the chosen target and measure.** Only after a concrete hardware
   path exists, bind control/firmware and instrumentation to it, freeze the final
   profile, score held-out data and compare measured task costs to digital.

Steps 1–2 are the next priority. Step 4 is a bounded supporting task, not a
substitute for them. The original end-to-end goal remains unchanged.

## Hardware-path decision needed

- Existing analog-compute hardware access would allow a concrete integration
  plan around its actual interfaces. It would not prove this custom converter.
- A board-level analog demonstrator could establish real analog computation,
  but its array and converter choices must be explicit; a substituted converter
  changes the claim and needs agreement. It does not retire custom-converter
  qualification from the stated goal.
- A custom-silicon path needs fabrication, packaging, board and test access.
  Those are unapproved external steps. Layout/simulation cannot satisfy them.

Next user input: what analog-compute hardware, FPGA/controller boards and
measurement equipment are actually available, including remote lab access?
If none, record that explicitly and prepare a proposal for approval rather than
assuming hardware-backed completion is possible with installed software alone.
