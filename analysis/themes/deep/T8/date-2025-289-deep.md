# CorrectBench: Automatic Testbench Generation with Functional Self-Correction using LLMs for HDL Design

**Venue:** DATE · **Subtheme:** Automated HDL Testbench Synthesis and Validation

## What It Does

CorrectBench automates the generation of hardware testbenches from RTL specifications using an LLM, then closes the correctness loop via automatic functional validation and self-correction. The system begins by prompting an LLM (e.g., GPT-3.5/4) with the RTL source and a natural-language specification of the design's intended behavior, producing a testbench (Verilog/VHDL stimulus and assertions). Rather than trusting the LLM output directly, the framework immediately runs the generated testbench against the RTL in simulation (ModelSim or similar), collecting validation failures: if an assertion fires, the simulation returns the exact assertion message and failing waveform segment. The framework then re-prompts the LLM with this failure information (bug trace + waveform context), asking it to fix the testbench. This iterate-until-passing loop continues until the testbench produces no further assertion violations or until a retry limit is hit.

The key data flow is LLM-generated code → simulation validation → failure feedback loop → corrected code, repeating. This differs from one-shot generation because the LLM never sees real simulation feedback; automatic self-correction allows the LLM to learn from concrete failures rather than abstract descriptions. For sequential circuits, the framework additionally models temporal delays and state evolution, which are frequent sources of LLM mistakes in one-shot generation.

## The Key Result

On a benchmark of HDL designs (both combinational and sequential), CorrectBench achieves 88.85% validation success rate (i.e., 88.85% of generated testbenches pass initial simulation without errors). The self-correction loop improves the overall pass rate to 70.13% compared to 52.18% for prior LLM-based methods (a 34% relative improvement). For sequential circuits specifically, the framework achieves 62.18% improvement over the previous best method. The corrected testbenches are functionally correct and integrate with existing CI/CD pipelines. Implementation and benchmark suite are open-sourced.

## Why This Approach

Testbench generation is a bottleneck in hardware design: engineers spend weeks writing and debugging comprehensive testbenches to cover corner cases, edge timing, and state machines. LLM-based generation promises automation, but naive LLM outputs are unreliable because the LLM lacks access to actual simulation semantics; it cannot tell if a testbench's assertions are semantically meaningful without running them. Automatic self-correction closes this gap by embedding the LLM into a validation loop: each failure message is concrete (not abstract) and directly actionable. This approach is simpler than training domain-specific models (which require labeled HDL datasets) and more maintainable than manual rule-based generators (which need constant updates for new design patterns). Sequential circuit testing is especially problematic for LLMs because they often generate incorrect delay assumptions; feeding real waveforms back to the LLM provides the temporal grounding the model lacks.

## What It Leaves Open

- **Overhead of iterative re-prompting not quantified**: each failure cycle re-invokes the LLM (cost and latency), and retry limits may prematurely terminate correction; the cost-benefit trade-off vs. manual testbench writing is not measured.
- **LLM hallucination on incomplete simulations**: if a design is genuinely buggy or underspecified, the LLM may generate assertions that are themselves incorrect; there is no oracle to distinguish design bugs from testbench errors.
- **Scalability to very large designs unclear**: all results are on small-to-medium RTL modules; integration with multi-module hierarchies, cross-module assertions, and formal property specifications remains unexplored.
- **Tool dependency**: the framework requires specific simulation tools (ModelSim, Vivado) and language-specific parsing; portability to other HDL variants or open-source simulators is not discussed.
- **Generalization to corner-case coverage**: the framework optimizes for assertion correctness, not thoroughness; it does not systematically explore unverified code paths or generate adversarial test cases to maximize coverage.
