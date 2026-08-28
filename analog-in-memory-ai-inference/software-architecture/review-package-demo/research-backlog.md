# Research Backlog

This backlog tells the team what to research next before the roadmap is used for investor, customer, or partner decisions.

The goal is simple: every outside claim must be checked, dated, and tied to a roadmap decision. A source can explain why a topic matters. A source cannot prove that our chip works unless the source is a measured result from our chip, our board, our compiler, or our lab setup.

Checked date for this backlog: `2026-08-25`

## Source Standards

Use different source types for different claims.

| Claim Type | Best Source | Acceptable Source | Not Enough By Itself |
|---|---|---|---|
| Product feature or product availability | official company product page, official documentation, datasheet, release note | company blog or recorded conference talk from the company | press summary, analyst note, social post |
| Funding amount or valuation | company press release, investor press release, SEC filing, regulator filing | trusted business press that names the round, date, and investors | unsourced database snippet, reposted article |
| Technical capability from research | peer-reviewed paper, arXiv paper, official lab page, conference proceedings | author slides if the paper is also linked | blog post without method, benchmark, or setup |
| Chip performance | measured result from the same chip or board, with setup and conditions | measured result from a close prototype, clearly labeled | simulator output, another company's chip result |
| Compiler support | compiler report from our pipeline, with supported and unsupported operators | upstream compiler documentation for reusable ideas | general MLIR claims without our chip target |
| Board behavior | board runtime trace from the same package and firmware | bring-up log with missing task linkage, clearly labeled | screenshot, manual note, simulated runtime only |
| Power and temperature | lab instrument trace tied to the same board run | onboard monitor trace if sensor limits are stated | average estimate without rail map or sample rate |
| Calibration behavior | calibration trace from the same chip, same setup, and same runtime package | simulator calibration result, clearly labeled | a statement that calibration exists |
| Reliability or updates | write, retention, endurance, rollback, and post-update task result from the same device class | vendor device data with our risk called out | memory endurance number without workload mapping |

Every source entry should record:

- source name
- source URL or file path
- checked date
- exact claim text being used
- allowed use
- what the source does not prove
- roadmap section or artifact affected
- owner who accepted the source

## Research Passes

### 1. Physical AI Market And First-Customer Fit

Question to answer: Which first market gives the chip a narrow, measurable job instead of a broad claim?

Research queries:

- `physical AI edge inference low power robotics sensor fusion workload 2026 official`
- `warehouse robotics edge AI power latency local inference customer deployment`
- `industrial inspection edge AI sensor fusion low power accelerator requirements`
- `drones edge AI inference power latency thermal constraints`

Preferred sources:

- official product pages from robotics, industrial, drone, and edge AI companies
- customer case studies with workload, power, latency, or deployment detail
- credible market reports only for context, not proof

What Research Can Change:

- first wedge market
- workload examples used in the roadmap
- customer proof requirements
- executive brief language about why the company exists now

What it must not be used to claim:

- that our chip has product-market fit
- that our chip beats digital edge chips
- that any customer will adopt the chip

Package fields affected:

- `physical-ai-opportunity-map.md`
- `executive-brief.md`
- `artifacts/opportunity_fit.json`
- `source-review-register.md`

Owner: product strategy with engineering review.

### 2. Analog AI Chip Startup And Funding Landscape

Question to answer: Which companies are building adjacent analog, compute-in-memory, neuromorphic, or low-power inference chips, and what claims are they making?

Research queries:

- `analog in-memory computing startup funding 2025 2026`
- `compute-in-memory AI chip startup Series B analog inference`
- `RRAM AI accelerator startup funding memristor inference`
- `analog AI inference chip company tapeout 300mm production`

Preferred sources:

- company press releases
- investor announcements
- SEC or regulator filings when available
- official foundry or memory partner announcements
- trusted semiconductor press with clear dates and named sources

What Research Can Change:

- competitor map
- investor-risk section
- build-versus-partner decisions
- roadmap timing for foundry, memory, packaging, and customer proof

What it must not be used to claim:

- that our chip has the same performance as another startup
- that another company's funding proves our roadmap is correct
- that press coverage proves manufacturability

Package fields affected:

- `source-review-register.md`
- `physical-ai-opportunity-map.md`
- `execution-roadmap.md`

Owner: strategy lead with technical diligence owner.

### 3. Toolkits, Simulators, And What They Actually Prove

Question to answer: Which tools can we reuse, and what exact proof level can each one support?

Research queries:

- `IBM AIHWKIT documentation analog hardware aware training PyTorch`
- `AIHWKIT Lightning analog foundation models hardware aware training`
- `Sandia CrossSim analog in-memory computing simulator documentation`
- `analog-mlir Golem SST processing in memory compiler`
- `ALPINE gem5-X analog in-memory acceleration AIMClib`
- `NeuroSim MNSIM analog in-memory computing simulator`
- `TxSim XBTorch RxNN memristor crossbar PyTorch simulator`

Preferred sources:

- official documentation
- GitHub repositories
- paper links from the tool authors
- lab pages from IBM, Sandia, EPFL, universities, and national labs

What Research Can Change:

- reuse-modification map
- simulator import templates
- compiler work queue
- evidence ladder labels

What it must not be used to claim:

- that simulator support equals chip support
- that PyTorch training proof equals board proof
- that upstream analog-mlir can target our chip without new lowering work

Package fields affected:

- `reuse-modification-map.md`
- `action-evidence-map.md`
- `engineering-work-queue.md`
- `import-templates/`

Owner: compiler lead and modeling lead.

### 4. Compiler Work For Transformers And VLA Models

Question to answer: What parts of transformer and VLA workloads can realistically map to analog arrays, and what must stay digital?

Research queries:

- `transformer analog in-memory computing linear projection attention softmax compiler`
- `vision language action model edge inference compiler partitioning`
- `compute in memory transformer attention accelerator softmax digital coprocessor`
- `analog MLIR transformer partitioning static weights dynamic attention`

Preferred sources:

- architecture papers with clear operator mapping
- compiler papers with pass descriptions and generated output
- official model cards for workload structure
- benchmark reports with setup details

What Research Can Change:

- analog/digital split
- compiler pass list
- unsupported operator list
- runtime package structure
- customer workload intake questions

What it must not be used to claim:

- full VLA readiness
- safety readiness
- task success on hardware
- support for a named model unless our compiler report proves it

Package fields affected:

- `artifacts/model_profile.json`
- `artifacts/compiler_mapping.json`
- `reuse-modification-map.md`
- `execution-roadmap.md`

Owner: model/compiler lead.

### 5. Memory Device Choice And Weight Updates

Question to answer: Which memory type is plausible for the first chip target, and how do writes, retention, drift, and endurance affect the roadmap?

Research queries:

- `RRAM analog in-memory computing write endurance retention variability inference`
- `FeFET compute in memory endurance retention analog AI accelerator`
- `MRAM compute in memory AI inference write latency energy endurance`
- `PCM analog AI drift retention programming noise hardware aware training`

Preferred sources:

- device papers with measured write and retention conditions
- foundry or memory partner documentation
- datasheets where available
- reliability reports with temperature and time conditions

What Research Can Change:

- memory choice assumptions
- update-readiness claims
- calibration needs
- thermal risk
- silicon requirements

What it must not be used to claim:

- safe local learning
- adaptive update readiness
- endurance for our workload without workload-specific write tests

Package fields affected:

- `artifacts/update_readiness.json`
- `artifacts/calibration_status.json`
- `silicon-board-proof-map.md`
- `import-templates/weight-update-report.template.json`

Owner: device lead and reliability lead.

### 6. Packaging, Noise, Heat, And Calibration

Question to answer: What hardware features are needed so analog results stay usable when digital logic, heat, voltage movement, and aging are present?

Research queries:

- `analog mixed signal substrate noise isolation deep n-well guard ring digital switching`
- `chiplet analog digital isolation thermal coupling in-memory computing`
- `analog in-memory computing calibration drift temperature voltage monitor`
- `FD-SOI analog neuromorphic compute mismatch leakage body bias`
- `thermal modeling 2.5D chiplet AI accelerator analog calibration`

Preferred sources:

- mixed-signal design papers
- foundry process notes when available
- packaging papers
- lab measurements tied to setup and temperature
- EDA documentation for simulation flow

What Research Can Change:

- silicon monitor requirements
- calibration trace fields
- board rail and temperature instrumentation
- package layout risk
- fallback behavior requirements

What it must not be used to claim:

- calibration is proven
- thermal safety is proven
- substrate noise is solved
- the board can fall back safely

Package fields affected:

- `silicon-board-proof-map.md`
- `artifacts/calibration_status.json`
- `import-templates/calibration-trace.template.json`
- `import-templates/power-thermal-report.template.json`

Owner: silicon lead, package lead, validation lead.

### 7. Board Runtime And Lab Instrumentation

Question to answer: What must the board expose so software can prove the chip ran and lab tools can measure the same run?

Research queries:

- `AI accelerator evaluation board runtime trace power measurement thermal trace firmware metadata`
- `FPGA PCIe USB UART JTAG board bring-up runtime logging power rail measurement`
- `edge AI accelerator board power thermal benchmark methodology`
- `hardware in the loop AI accelerator board trace task accuracy`

Preferred sources:

- evaluation board manuals
- accelerator SDK documentation
- lab measurement methodology notes
- firmware logging documentation
- customer pilot proof checklists

What Research Can Change:

- board interface requirements
- firmware metadata fields
- runtime trace template
- lab import templates
- product UI for measured proof

What it must not be used to claim:

- board measured lower energy unless measured
- runtime success unless the exact package ran
- task success unless task result is synchronized with the board trace

Package fields affected:

- `artifacts/runtime_package.json`
- `artifacts/board_runtime.json`
- `artifacts/power_thermal.json`
- `artifacts/task_accuracy.json`
- `import-templates/board-runtime-trace.template.json`

Owner: board lead and backend lead.

### 8. Sensor Interfaces For Physical AI

Question to answer: Should the first chip target prepared tensors, raw sensor streams, or both?

Research queries:

- `event based vision sensor interface low power edge AI accelerator`
- `Sony Prophesee IMX636 event sensor data interface documentation`
- `tactile sensor array edge AI force slip interface`
- `analog front end robot force torque tactile sensor AI inference`

Preferred sources:

- sensor datasheets
- official sensor product pages
- interface documentation
- customer workload traces when available
- papers that state sample rate, bandwidth, and preprocessing

What Research Can Change:

- sensor-path roadmap
- board connector requirements
- runtime synchronization fields
- first-market selection
- analog-front-end decision

What it must not be used to claim:

- native support for a specific sensor without interface proof
- energy savings across the full product without measured path energy
- task improvement without task result

Package fields affected:

- `artifacts/sensor_path.json`
- `import-templates/sensor-path-report.template.json`
- `physical-ai-opportunity-map.md`

Owner: sensor systems lead and product lead.

### 9. Adjacent Digital Edge Silicon

Question to answer: Where do digital edge chips already serve the customer well, and where might analog still have a narrower advantage?

Research queries:

- `NVIDIA Jetson robotics edge AI power latency developer kit official`
- `Qualcomm robotics platform edge AI NPU official documentation`
- `NXP robotics real time processor sensor bridge official`
- `Lattice FPGA robotics low power motor control official`
- `Hailo edge AI processor robotics power latency official`

Preferred sources:

- official datasheets
- official product pages
- SDK documentation
- developer kit manuals
- measured third-party benchmarks only when setup is clear

What Research Can Change:

- positioning against digital alternatives
- first-market filter
- pricing and power assumptions
- partner-versus-compete language

What it must not be used to claim:

- that our chip beats a competitor
- that competitor peak numbers map to customer workloads
- that analog is broadly better

Package fields affected:

- `physical-ai-opportunity-map.md`
- `executive-brief.md`
- `source-review-register.md`

Owner: strategy lead with systems engineering review.

## What Research Can Change

Research can change the roadmap only when the source standard matches the claim type.

Research can change:

- which first market we prioritize
- which workload we use for the first board proof
- which memory technology stays in the near-term plan
- which toolkits we reuse first
- which compiler passes must be built first
- which board links and lab instruments are required
- which claims are allowed in executive language
- which claims are blocked until measured proof exists

Research cannot change:

- the rule that simulator output is not board proof
- the rule that market interest is not chip proof
- the rule that another company result is not our result
- the rule that a board run without power, temperature, calibration, and task linkage is incomplete
- the rule that full VLA readiness stays blocked until a real compiler report, board run, task result, and safety boundary exist

## Decision Review Rhythm

Run the research backlog in review cycles.

1. Pick one research pass.
2. Record the question, source standard, and owner before searching.
3. Save each accepted source in `source-review-register.md`.
4. Write the exact claim text that the source supports.
5. Write the exact claim text that remains blocked.
6. Update only the roadmap sections and artifacts listed for that pass.
7. Rebuild the review package archive.
8. Run the package smoke tests.
9. Review whether the final answer changed.

If a source is useful but does not meet the standard, keep it as background context only. Do not use it to unlock a product claim.
