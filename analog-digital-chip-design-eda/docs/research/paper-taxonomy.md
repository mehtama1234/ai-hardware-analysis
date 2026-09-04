# Paper Taxonomy For Analog, Digital, And EDA

This taxonomy defines how future papers should be read into the corpus. A paper is not grouped by buzzword. It is grouped by the object it changes and the evidence it gives.

## Analog And Mixed-Signal Design

The object is a continuous electrical quantity: voltage, current, charge, phase, frequency, noise, offset, or distortion.

Subthemes:

- device sizing and biasing
- amplifiers and feedback loops
- data converters
- PLLs, clocks, and jitter
- power management circuits
- RF and high-speed interfaces
- layout-aware analog design
- calibration and trimming

Reading test: identify which physical error source the paper controls and how the circuit proves the error is small enough.

## Digital Design And Architecture

The object is symbolic state carried by physical voltage and timed by clocks.

Subthemes:

- RTL design and microarchitecture
- memory hierarchy and data movement
- arithmetic units
- accelerators and domain-specific logic
- clocking, reset, and CDC
- low-power design
- verification and formal methods
- post-silicon debug

Reading test: identify the state update, the timing boundary, and the evidence that the implementation preserves the intended behavior.

## Physical Design And Signoff

The object is the translation from gates into legal, timed, powered geometry.

Subthemes:

- floorplanning and macro placement
- global and detailed placement
- clock-tree synthesis
- global and detailed routing
- extraction and parasitic modeling
- static timing analysis
- power integrity and IR drop
- DRC, LVS, and signoff

Reading test: identify which physical constraint is binding and what artifact proves the design survived it.

## AI For EDA

The object is an engineering loop: generate, check, repair, search, size, place, route, verify, or explain.

Subthemes:

- RTL generation and repair
- testbench and assertion generation
- analog sizing and topology search
- placement and routing optimization
- log triage and debug agents
- design-rule repair
- surrogate modeling for expensive simulation
- human-in-the-loop design assistants

Reading test: identify the tool action the model performs, the checker that catches wrong actions, and the baseline engineering loop it improves.

## Manufacturing, Packaging, And Yield

The object is probability of a working product after fabrication, packaging, and test.

Subthemes:

- process variation and statistical design
- defect density and yield learning
- advanced packaging and chiplets
- HBM and memory bandwidth
- thermal and power delivery limits
- wafer inspection and metrology
- test, binning, and repair
- supply-chain and foundry constraints

Reading test: identify whether the paper changes design margin, inspection evidence, repair ability, throughput, or cost per good die.

## Corpus Rule

Every paper entry should record:

1. object controlled
2. constraint
3. mathematical form
4. concrete method
5. evidence artifact
6. failure boundary
7. related concept article
8. related lab, if any

