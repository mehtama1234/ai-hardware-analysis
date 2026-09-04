# Coverage Audit And Next Expansion

This audit states what the current chip-design corpus covers and where the next paper batch should go.

## Current Proven Coverage

The project currently has:

- 22 first-principles concept articles
- 6 lab guides
- 20 sourced paper entries
- 20 full paper notes
- 2 research maps
- 2 synthesis pages

Every paper entry has a matching full note. Every paper entry names the object controlled, constraint, mathematical form, concrete method, evidence artifact, failure boundary, related concepts, and related labs.

## Track Balance

Current paper coverage:

- physical design and signoff: 6 papers
- AI for EDA: 4 papers
- digital design and architecture: 4 papers
- analog and mixed-signal: 3 papers
- manufacturing, packaging, and yield: 3 papers

This is a useful first corpus, but it is not yet evenly deep. Physical design is strongest because OpenROAD, OpenLane, VTR, DREAMPlace, PDN generation, and statistical timing already form a connected flow. AI-for-EDA is coherent because the papers cover survey taxonomy, placement, language models, Verilog generation, and surrogate signoff analysis.

Analog is thinner. It has analog sizing and analog layout automation, but it still needs data converters, PLLs, LDOs, RF/high-speed links, analog verification, and post-layout simulation papers.

Manufacturing and packaging are also thin. The corpus has yield learning, chiplets, and hardware Trojan detection, but it still needs DFM, lithography-aware design, test/DFT, packaging power delivery, thermal reliability, and memory/HBM integration.

## What The Corpus Already Teaches

The strongest current argument is preservation under translation:

```text
intent -> program or RTL -> logic -> placed geometry -> routed geometry -> extracted circuit -> signoff evidence -> manufactured product
```

Open flows make the translation visible. Analog automation shows that layout must preserve electrical relationships. AI-for-EDA shows that model output needs a checker. Signoff papers show that hidden physics must be turned into explicit evidence. Manufacturing and security papers show that a working design also needs yield and trust.

## Thin Areas To Fix Next

### Analog Circuit Families

Add papers on:

- ADC architecture and calibration
- PLL design and jitter
- LDO and power-management design
- RF front-end design
- high-speed SerDes or wireline links
- analog verification and post-layout simulation

Reason: the concept atlas already explains noise, bandwidth, stability, mismatch, and ADCs, but the paper layer does not yet show enough real circuit families.

### Digital Verification And Test

Add papers on:

- SystemVerilog assertion and formal property checking
- UVM-style verification methodology
- fuzzing for hardware designs
- DFT, scan, ATPG, and built-in self-test
- clock-domain crossing verification

Reason: the corpus has ABC, VerilogEval, LegUp, OpenTitan, and Trojan detection, but it needs more papers about how digital correctness is established before and after synthesis.

### Timing, Power, And Reliability Signoff

Add papers on:

- static timing analysis engines
- on-chip variation and multi-corner multi-mode timing
- electromigration
- dynamic voltage drop
- thermal-aware placement
- aging and BTI/HCI reliability

Reason: timing, power, and yield are coupled. The current corpus names that coupling but needs more signoff mechanisms.

### Manufacturing And Advanced Packaging

Add papers on:

- DFM and lithography-aware layout
- chemical-mechanical polishing variation
- wafer inspection and metrology
- chiplet interconnect and UCIe
- HBM integration
- 2.5D/3D thermal and power delivery

Reason: chiplet and yield papers introduce the system boundary shift, but the corpus needs more evidence around package-level design constraints.

### AI For EDA With Strong Checkers

Add papers on:

- LLM agents for EDA scripting
- RTL repair with compiler and simulator feedback
- formal-verification-guided code generation
- design-rule repair
- timing-closure parameter tuning
- analog sizing under corners and extraction

Reason: AI-for-EDA should stay tied to checked loops. The next AI papers should be chosen only when the checker is explicit.

## Next 25-Paper Target

The next expansion should add:

- 6 analog circuit-family papers
- 5 digital verification/test papers
- 5 timing/power/reliability signoff papers
- 5 manufacturing/advanced-packaging papers
- 4 AI-for-EDA checked-loop papers

The target after that batch:

- 45 sourced paper entries
- 45 full paper notes
- 22 or more concept articles
- all papers linked to concepts and labs
- a revised synthesis page that explains how the new analog and manufacturing papers change the map

## Quality Gate

Do not add a paper unless it can answer:

1. What object is controlled?
2. What constraint makes control hard?
3. What mathematical form exposes the constraint?
4. What concrete method changes the object?
5. What evidence artifact proves the method worked?
6. What failure boundary remains?

